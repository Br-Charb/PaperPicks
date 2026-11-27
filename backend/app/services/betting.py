from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.models.bet import Bet, BetLeg, multiplier_for_picks
from app.models.prop import Prop
from app.models.user import User
from app.schemas.bet import BetCreate, BetLegResponse, BetResponse


def serialize_bet(bet: Bet) -> BetResponse:
    legs = [
        BetLegResponse(
            id=leg.id,
            prop_id=leg.prop_id,
            player_name=leg.prop.player_name,
            stat_category=leg.prop.stat_category,
            matchup=leg.prop.game.matchup,
            line_snapshot=leg.line_snapshot,
            pick=leg.pick,
            status=leg.status,
        )
        for leg in bet.legs
    ]
    return BetResponse(
        id=bet.id,
        user_id=bet.user_id,
        wager=bet.wager,
        multiplier=bet.multiplier,
        potential_payout=bet.potential_payout,
        actual_payout=bet.actual_payout,
        status=bet.status,
        created_at=bet.created_at,
        settled_at=bet.settled_at,
        legs=legs,
    )


def place_bet(
    db: Session,
    user: User,
    payload: BetCreate,
    now: datetime | None = None,
) -> tuple[Bet, int]:
    check_time = now or datetime.now(timezone.utc)
    prop_ids = [leg.prop_id for leg in payload.legs]

    if len(set(prop_ids)) != len(prop_ids):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Duplicate props are not allowed in the same prediction slip.",
        )

    props = (
        db.query(Prop)
        .options(joinedload(Prop.game))
        .filter(Prop.id.in_(prop_ids))
        .all()
    )
    props_by_id = {prop.id: prop for prop in props}

    for leg in payload.legs:
        prop = props_by_id.get(leg.prop_id)
        if prop is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Prop {leg.prop_id} not found.",
            )
        if not prop.is_open_for_picks(check_time):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Prop {prop.id} ({prop.player_name}) is no longer open for picks.",
            )

    multiplier = multiplier_for_picks(len(payload.legs))
    potential_payout = round(payload.wager * multiplier)

    updated = (
        db.query(User)
        .filter(User.id == user.id, User.balance >= payload.wager)
        .update(
            {User.balance: User.balance - payload.wager},
            synchronize_session=False,
        )
    )
    if updated == 0:
        db.rollback()
        db.refresh(user)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient virtual currency balance.",
        )

    bet = Bet(
        user_id=user.id,
        wager=payload.wager,
        multiplier=multiplier,
        potential_payout=potential_payout,
        legs=[
            BetLeg(
                prop_id=leg.prop_id,
                pick=leg.pick,
                line_snapshot=props_by_id[leg.prop_id].line,
            )
            for leg in payload.legs
        ],
    )
    db.add(bet)
    db.commit()
    db.refresh(user)

    loaded_bet = (
        db.query(Bet)
        .options(
            joinedload(Bet.legs)
            .joinedload(BetLeg.prop)
            .joinedload(Prop.game)
        )
        .filter(Bet.id == bet.id)
        .one()
    )
    return loaded_bet, user.balance


def get_user_bets(
    db: Session,
    user_id: int,
    status_filter: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[Bet]:
    query = (
        db.query(Bet)
        .options(
            joinedload(Bet.legs)
            .joinedload(BetLeg.prop)
            .joinedload(Prop.game)
        )
        .filter(Bet.user_id == user_id)
    )
    if status_filter is not None:
        query = query.filter(Bet.status == status_filter)

    return (
        query.order_by(Bet.created_at.desc(), Bet.id.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )


def settle_prop_bets(
    db: Session,
    prop_id: int,
    actual_value: float,
    now: datetime | None = None,
) -> list[Bet]:
    settled_time = now or datetime.now(timezone.utc)
    prop = db.get(Prop, prop_id)
    if prop is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prop {prop_id} not found.",
        )
    if prop.status in ("settled", "cancelled"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Prop {prop_id} has already been {prop.status}.",
        )

    prop.status = "settled"

    pending_legs = (
        db.query(BetLeg)
        .filter(BetLeg.prop_id == prop_id, BetLeg.status == "pending")
        .all()
    )
    if not pending_legs:
        db.commit()
        return []

    affected_bet_ids = sorted({leg.bet_id for leg in pending_legs})
    for leg in pending_legs:
        won_leg = (
            actual_value > leg.line_snapshot
            if leg.pick == "over"
            else actual_value < leg.line_snapshot
        )
        leg.status = "won" if won_leg else "lost"

    db.flush()

    affected_bets = (
        db.query(Bet)
        .options(joinedload(Bet.legs))
        .filter(Bet.id.in_(affected_bet_ids), Bet.status == "pending")
        .all()
    )

    settled_bets: list[Bet] = []
    payouts_by_user: dict[int, int] = {}
    for bet in affected_bets:
        leg_statuses = {leg.status for leg in bet.legs}
        if "lost" in leg_statuses:
            bet.status = "lost"
            bet.actual_payout = 0
            bet.settled_at = settled_time
            settled_bets.append(bet)
        elif leg_statuses == {"won"}:
            bet.status = "won"
            bet.actual_payout = bet.potential_payout
            bet.settled_at = settled_time
            payouts_by_user[bet.user_id] = (
                payouts_by_user.get(bet.user_id, 0) + bet.actual_payout
            )
            settled_bets.append(bet)

    for user_id, payout in payouts_by_user.items():
        db.query(User).filter(User.id == user_id).update(
            {User.balance: User.balance + payout},
            synchronize_session=False,
        )

    db.commit()
    for bet in settled_bets:
        db.refresh(bet)
    return settled_bets

