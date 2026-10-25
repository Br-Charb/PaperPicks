from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, DateTime, Integer, String, UniqueConstraint
from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base

if TYPE_CHECKING:
    from app.models.prop import Prop


class Game(Base):
    __tablename__ = "games"
    __table_args__ = (
        UniqueConstraint(
            "away_team", "home_team", "kickoff_at", name="uq_games_matchup_kickoff"
        ),
        CheckConstraint("away_team <> home_team", name="ck_games_distinct_teams"),
        CheckConstraint(
            "status IN ('scheduled', 'in_progress', 'final', 'postponed', 'cancelled')",
            name="ck_games_status",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    # Team abbreviations, e.g. "BUF" and "KC"
    away_team: Mapped[str] = mapped_column(String(3), nullable=False)
    home_team: Mapped[str] = mapped_column(String(3), nullable=False)
    kickoff_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="scheduled",
        server_default="scheduled",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    props: Mapped[list["Prop"]] = relationship(back_populates="game")

    @property
    def matchup(self) -> str:
        return f"{self.away_team} @ {self.home_team}"
