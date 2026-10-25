from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

StatCategory = Literal[
    "Game Outcome",
    "Passing Yards",
    "Rushing Yards",
    "Receiving Yards",
    "TDs",
]


class PropCreate(BaseModel):
    game_id: int
    player_name: str
    stat_category: StatCategory
    line: float = Field(allow_inf_nan=False)

    @field_validator("player_name")
    @classmethod
    def validate_player_name(cls, v: str) -> str:
        clean = v.strip()
        if len(clean) < 1 or len(clean) > 100:
            raise ValueError("Player name must be between 1 and 100 characters")
        return clean

    @field_validator("line")
    @classmethod
    def validate_line(cls, v: float) -> float:
        # Must end in .5 so results can't tie
        doubled = v * 2
        if v <= 0 or doubled != int(doubled) or int(doubled) % 2 == 0:
            raise ValueError(
                f"Line must be a positive number ending in .5 (e.g. 299.5), got {v:g}"
            )
        return v


class PropResponse(BaseModel):
    id: int
    game_id: int
    player_name: str
    stat_category: str
    line: float
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Mirror frontend/src/types.ts
class PlayerPropResponse(BaseModel):
    id: str
    player: str
    category: str
    line: str
    matchup: str
    time: str


class GamePropsResponse(BaseModel):
    id: str
    matchup: str
    kickoff: str
    props: list[PlayerPropResponse]


class DateGroupResponse(BaseModel):
    date: str
    games: list[GamePropsResponse]
