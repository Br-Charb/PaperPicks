from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

PickChoice = Literal["over", "under"]
BetStatus = Literal["pending", "won", "lost", "cancelled"]


class BetLegCreate(BaseModel):
    prop_id: int = Field(gt=0)
    pick: PickChoice


class BetCreate(BaseModel):
    wager: int = Field(gt=0)
    legs: list[BetLegCreate] = Field(min_length=1)


class BetLegResponse(BaseModel):
    id: int
    prop_id: int
    player_name: str
    stat_category: str
    matchup: str
    line_snapshot: float
    pick: PickChoice
    status: BetStatus

    model_config = ConfigDict(from_attributes=True)


class BetResponse(BaseModel):
    id: int
    user_id: int
    wager: int
    multiplier: float
    potential_payout: int
    actual_payout: int
    status: BetStatus
    created_at: datetime
    settled_at: datetime | None
    legs: list[BetLegResponse]

    model_config = ConfigDict(from_attributes=True)


class BetPlacementResponse(BaseModel):
    bet: BetResponse
    balance: int
