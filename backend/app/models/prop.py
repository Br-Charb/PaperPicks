from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy import UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base

if TYPE_CHECKING:
    from app.models.game import Game


STAT_CATEGORIES = (
    "Game Outcome",
    "Passing Yards",
    "Rushing Yards",
    "Receiving Yards",
    "TDs",
)
PROP_STATUSES = ("draft", "published", "locked", "settled", "cancelled")


def _sql_in_list(values: tuple[str, ...]) -> str:
    return ", ".join(f"'{value}'" for value in values)


class Prop(Base):
    __tablename__ = "props"
    __table_args__ = (
        UniqueConstraint(
            "game_id",
            "player_name",
            "stat_category",
            name="uq_props_game_player_category",
        ),
        CheckConstraint(
            f"stat_category IN ({_sql_in_list(STAT_CATEGORIES)})",
            name="ck_props_stat_category",
        ),
        CheckConstraint(
            f"status IN ({_sql_in_list(PROP_STATUSES)})",
            name="ck_props_status",
        ),
        # Line must end in .5 so results can't tie
        CheckConstraint(
            "line > 0 AND line * 2 = CAST(line * 2 AS INTEGER) "
            "AND CAST(line * 2 AS INTEGER) % 2 <> 0",
            name="ck_props_line_half_increment",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    game_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("games.id", name="fk_props_game_id"),
        nullable=False,
        index=True,
    )
    # Player name, or team name for "Game Outcome" props
    player_name: Mapped[str] = mapped_column(String(100), nullable=False)
    stat_category: Mapped[str] = mapped_column(String(30), nullable=False)
    # Float is exact for .5 values
    line: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="draft",
        server_default="draft",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    game: Mapped["Game"] = relationship(back_populates="props")
