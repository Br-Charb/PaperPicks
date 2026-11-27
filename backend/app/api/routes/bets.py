from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.bet import (
    BetCreate,
    BetPlacementResponse,
    BetResponse,
    BetStatus,
)
from app.services.betting import get_user_bets, place_bet, serialize_bet

router = APIRouter()


@router.post(
    "",
    response_model=BetPlacementResponse,
    status_code=status.HTTP_201_CREATED,
)
def submit_bet_slip(
    bet_data: BetCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    bet, new_balance = place_bet(db=db, user=current_user, payload=bet_data)
    return BetPlacementResponse(bet=serialize_bet(bet), balance=new_balance)


@router.get("", response_model=list[BetResponse], status_code=status.HTTP_200_OK)
def list_user_bets(
    bet_status: BetStatus | None = Query(default=None, alias="status"),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    bets = get_user_bets(
        db=db,
        user_id=current_user.id,
        status_filter=bet_status,
        limit=limit,
        offset=offset,
    )
    return [serialize_bet(bet) for bet in bets]
