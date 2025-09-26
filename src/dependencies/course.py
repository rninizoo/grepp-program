
from fastapi import Depends

from ..dependencies.payment import get_payment_service
from ..features.courses.service import CourseService
from ..features.payments.service import PaymentService


def get_course_service(
    payment_service: PaymentService = Depends(get_payment_service),
) -> CourseService:
    return CourseService(payment_service)
