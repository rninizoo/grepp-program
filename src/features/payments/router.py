
from fastapi import APIRouter, Depends
from sqlmodel import Session

from ...features.payments import service
from ...features.users.schemas import UserRead
from ...shared.database import get_session
from ...shared.security import authenticate_token
from .schemas import PaymentQueryOpts, PaymentRead

router = APIRouter(prefix="", tags=["payments"])


@router.get("/me/payments", response_model=list[PaymentRead])
def paginate_my_payments(
    current_user: UserRead = Depends(authenticate_token),
    session: Session = Depends(get_session),
    skip: int = 0,
    limit: int = 100,
    query_opts: PaymentQueryOpts = Depends(),
):
    payments = service.find_payments(session, skip, limit, query_opts)
    # 본인 결제만 필터링
    return [p for p in payments if p.userId == current_user.id]
