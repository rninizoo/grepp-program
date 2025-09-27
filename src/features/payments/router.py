from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials
from sqlmodel import Session

from ...dependencies.auth import get_auth_service
from ...dependencies.payment import get_payment_service
from ...features.auth.service import AuthService
from ...features.payments.service import PaymentService
from ...shared.database import get_session
from ...shared.security import security
from .schemas import PaymentQueryOpts, PaymentRead

router = APIRouter(prefix="/payments", tags=["payments"])


@router.get("/me", response_model=list[PaymentRead])
def paginate_my_payments(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        auth_service: AuthService = Depends(get_auth_service),
        payment_service: PaymentService = Depends(get_payment_service),
        session: Session = Depends(get_session),
        query_opts: PaymentQueryOpts = Depends(),
        skip: int = 0,
        limit: int = 100):

    current_user = auth_service.get_my_by_token(
        credentials.credentials, session=session)
    payments = payment_service.find_payments(session, skip, limit, query_opts)
    # 본인 결제만 필터링
    return [p for p in payments if p.userId == current_user['id']]


@router.post("/{payment_id}/cancel", response_model=PaymentRead)
def cancel_payments(
    payment_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthService = Depends(get_auth_service),
    session: Session = Depends(get_session),
    payment_service: PaymentService = Depends(get_payment_service),
):
    current_user = auth_service.get_my_by_token(
        credentials.credentials, session=session)
    payment = payment_service.cancel_payment(
        payment_id=payment_id, user_id=current_user['id'], session=session)

    return payment
