
from ..features.payments.service import PaymentService


def get_payment_service() -> PaymentService:
    return PaymentService()
