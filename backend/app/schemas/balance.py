from pydantic import BaseModel


class BalanceResponse(BaseModel):
    balance: int
    can_restore: bool
    restore_amount: int = 1000


class BalanceRestoreResponse(BaseModel):
    message: str
    balance: int
    credited_amount: int

