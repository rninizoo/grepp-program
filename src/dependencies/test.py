
from fastapi import Depends

from ..dependencies.payment import get_payment_service
from ..features.payments.service import PaymentService
from ..features.tests.service import TestService


def get_test_service(
    payment_service: PaymentService = Depends(get_payment_service),
) -> TestService:
    return TestService(payment_service)
