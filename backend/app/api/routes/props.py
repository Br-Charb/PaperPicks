from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, contains_eager

from app.api.deps import get_current_user, get_db
from app.models import Game, Prop
from app.schemas.prop import DateGroupResponse, GamePropsResponse, PlayerPropResponse

router = APIRouter(dependencies=[Depends(get_current_user)])

# Frontend shows Eastern time
DISPLAY_TIMEZONE = ZoneInfo("America/New_York")
VISIBLE_WINDOW = timedelta(days=7)


def _as_utc(value: datetime) -> datetime:
    # SQLite returns naive datetimes; they are stored as UTC
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value


def _format_time(value: datetime) -> str:
    # e.g. "4:25 PM"
    return f"{value.hour % 12 or 12}:{value:%M %p}"


@router.get("", response_model=list[DateGroupResponse])
def list_available_props(db: Session = Depends(get_db)):
    """Lists open props for games in the next 7 days."""
    now = datetime.now(timezone.utc)
    props = (
        db.query(Prop)
        .join(Prop.game)
        .options(contains_eager(Prop.game))
        .filter(Game.kickoff_at > now, Game.kickoff_at <= now + VISIBLE_WINDOW)
        .order_by(Game.kickoff_at, Game.id, Prop.player_name)
        .all()
    )

    date_groups: dict[str, DateGroupResponse] = {}
    games: dict[int, GamePropsResponse] = {}
    for prop in props:
        if not prop.is_open_for_picks(now):
            continue

        game = prop.game
        kickoff = _as_utc(game.kickoff_at).astimezone(DISPLAY_TIMEZONE)
        if game.id not in games:
            games[game.id] = GamePropsResponse(
                id=str(game.id),
                matchup=game.matchup,
                kickoff=kickoff.isoformat(),
                props=[],
            )
            date = kickoff.strftime("%m/%d/%Y")
            date_groups.setdefault(date, DateGroupResponse(date=date, games=[]))
            date_groups[date].games.append(games[game.id])

        games[game.id].props.append(
            PlayerPropResponse(
                id=str(prop.id),
                player=prop.player_name,
                category=prop.stat_category,
                line=str(prop.line),
                matchup=game.matchup,
                time=_format_time(kickoff),
            )
        )

    return list(date_groups.values())
