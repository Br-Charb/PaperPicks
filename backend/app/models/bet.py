from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base

if TYPE_CHECKING:
    from app.models.prop import Prop
    from app.models.user import User

BET_STATUSES = ("pending", "won", "lost", "cancelled")
BET_LEG_STATUSES = ("pending", "won", "lost", "cancelled")
PICK_CHOICES = ("over", "under")
MULTIPLIERS = (1.0, 1.5, 2.0, 2.6, 4.0, 6.0)


def _sql_in_list(values: tuple[str, ...]) -> str:
    return ", ".join(f"'{value}'" for value in values)


def multiplier_for_picks(pick_count: int) -> float:
    if pick_count <= 0:
        return MULTIPLIERS[0]
    return MULTIPLIERS[min(pick_count, len(MULTIPLIERS) - 1)]


class Bet(Base):
    __tablename__ = "bets"
    __table_args__ = (
        CheckConstraint("wager > 0", name="ck_bets_positive_wager"),
        CheckConstraint("multiplier > 0", name="ck_bets_positive_multiplier"),
        CheckConstraint(
            "potential_payout > 0", name="ck_bets_positive_potential_payout"
        ),
        CheckConstraint(
            "actual_payout >= 0", name="ck_bets_non_negative_actual_payout"
        ),
        CheckConstraint(
            f"status IN ({_sql_in_list(BET_STATUSES)})",
            name="ck_bets_status",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", name="fk_bets_user_id"),
        nullable=False,
        index=True,
    )
    wager: Mapped[int] = mapped_column(Integer, nullable=False)
    multiplier: Mapped[float] = mapped_column(Float, nullable=False)
    potential_payout: Mapped[int] = mapped_column(Integer, nullable=False)
    actual_payout: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
    )
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="pending",
        server_default="pending",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    settled_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    user: Mapped["User"] = relationship()
    legs: Mapped[list["BetLeg"]] = relationship(
        back_populates="bet",
        cascade="all, delete-orphan",
    )


class BetLeg(Base):
    __tablename__ = "bet_legs"
    __table_args__ = (
        UniqueConstraint("bet_id", "prop_id", name="uq_bet_legs_bet_prop"),
        CheckConstraint(
            f"pick IN ({_sql_in_list(PICK_CHOICES)})",
            name="ck_bet_legs_pick",
        ),
        CheckConstraint(
            f"status IN ({_sql_in_list(BET_LEG_STATUSES)})",
            name="ck_bet_legs_status",
        ),
        CheckConstraint("line_snapshot > 0", name="ck_bet_legs_positive_line"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    bet_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("bets.id", name="fk_bet_legs_bet_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    prop_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("props.id", name="fk_bet_legs_prop_id"),
        nullable=False,
        index=True,
    )
    pick: Mapped[str] = mapped_column(String(10), nullable=False)
    line_snapshot: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="pending",
        server_default="pending",
    )

    bet: Mapped["Bet"] = relationship(back_populates="legs")
    prop: Mapped["Prop"] = relationship()
