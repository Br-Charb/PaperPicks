from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.balance import BalanceResponse, BalanceRestoreResponse

RESTORE_AMOUNT = 1000

router = APIRouter()


@router.get("", response_model=BalanceResponse, status_code=status.HTTP_200_OK)
def get_balance(current_user: User = Depends(get_current_user)):
    """Retrieves the current user's virtual currency balance and restoration eligibility."""
    return BalanceResponse(
        balance=current_user.balance,
        can_restore=current_user.balance == 0,
        restore_amount=RESTORE_AMOUNT,
    )


@router.post(
    "/restore",
    response_model=BalanceRestoreResponse,
    status_code=status.HTTP_200_OK,
)
def restore_balance(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Credits 1,000 virtual currency units if and only if the user's current balance is 0.
    Uses an atomic conditional update to prevent concurrent double-credits.
    """
    updated = (
        db.query(User)
        .filter(User.id == current_user.id, User.balance == 0)
        .update({User.balance: RESTORE_AMOUNT}, synchronize_session=False)
    )

    if updated == 0:
        db.rollback()
        db.refresh(current_user)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Balance must be 0 before requesting restoration.",
        )

    db.commit()
    db.refresh(current_user)

    return BalanceRestoreResponse(
        message=f"Successfully restored {RESTORE_AMOUNT:,} virtual currency units.",
        balance=current_user.balance,
        credited_amount=RESTORE_AMOUNT,
    )

