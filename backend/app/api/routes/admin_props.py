from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_admin
from app.models import Game, Prop
from app.schemas.prop import PropCreate, PropResponse

router = APIRouter(dependencies=[Depends(require_admin)])


def _has_kicked_off(game: Game) -> bool:
    kickoff = game.kickoff_at
    # SQLite returns naive datetimes; they are stored as UTC
    if kickoff.tzinfo is None:
        kickoff = kickoff.replace(tzinfo=timezone.utc)
    return kickoff <= datetime.now(timezone.utc)


def _ensure_game_open(game: Game) -> None:
    if game.status != "scheduled" or _has_kicked_off(game):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Game has already kicked off or is no longer scheduled",
        )


@router.post("", response_model=PropResponse, status_code=status.HTTP_201_CREATED)
def create_prop(prop_data: PropCreate, db: Session = Depends(get_db)):
    """Creates a new prop as a draft."""
    game = db.get(Game, prop_data.game_id)
    if game is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found",
        )
    _ensure_game_open(game)

    existing_prop = (
        db.query(Prop)
        .filter(
            Prop.game_id == prop_data.game_id,
            Prop.player_name == prop_data.player_name,
            Prop.stat_category == prop_data.stat_category,
        )
        .first()
    )
    if existing_prop:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A prop for this player and stat already exists for this game",
        )

    new_prop = Prop(**prop_data.model_dump())
    db.add(new_prop)
    db.commit()
    db.refresh(new_prop)
    return new_prop


@router.post("/{prop_id}/publish", response_model=PropResponse)
def publish_prop(prop_id: int, db: Session = Depends(get_db)):
    """Publishes a draft prop."""
    prop = db.get(Prop, prop_id)
    if prop is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prop not found",
        )
    if prop.status != "draft":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Only draft props can be published",
        )
    _ensure_game_open(prop.game)

    prop.status = "published"
    db.commit()
    db.refresh(prop)
    return prop
