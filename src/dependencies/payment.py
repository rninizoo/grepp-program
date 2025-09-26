from fastapi import Depends

from ..features.course_registration.service import CourseRegistrationService
from ..features.payments.service import PaymentService
from ..features.test_registration.service import TestRegistrationService


def get_test_registration_service() -> TestRegistrationService:
    return TestRegistrationService()


def get_course_registration_service() -> CourseRegistrationService:
    return CourseRegistrationService()


def get_payment_service(test_registration_service: TestRegistrationService = Depends(get_test_registration_service), course_registration_service: CourseRegistrationService = Depends(get_course_registration_service)) -> PaymentService:
    return PaymentService(test_registration_service=test_registration_service, course_registration_service=course_registration_service)
