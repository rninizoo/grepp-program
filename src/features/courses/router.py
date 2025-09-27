from typing import Literal

from fastapi import APIRouter, Body, Depends, Query
from fastapi.security import HTTPAuthorizationCredentials
from sqlmodel import Session

from ...dependencies.auth import get_auth_service
from ...dependencies.course import get_course_service
from ...features.auth.service import AuthService
from ...features.payments.schemas import PaymentApplyCourse, PaymentRead
from ...shared.database import get_session
from ...shared.security import security
from . import service
from .schemas import CourseCreate, CourseQueryOpts, CourseRead, CourseRowRead, CourseUpdate

router = APIRouter(prefix="/courses", tags=["courses"])


@router.get("", response_model=list[CourseRead])
def get_courses(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthService = Depends(get_auth_service),
    service: service.CourseService = Depends(get_course_service),
    status: str = Query("AVAILABLE", description="Filter by Course status"),
    sort: Literal["created", "popular"] = Query(
        "created", description="Sort by created or popular"),
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session),
) -> list[CourseRowRead]:
    current_user = auth_service.get_my_by_token(
        credentials.credentials, session=session)
    query_opts = CourseQueryOpts(status=status, sort=sort)

    return service.find_courses(session=session, skip=skip, limit=limit, actant_id=current_user['id'], query_opts=query_opts)


@router.post("", response_model=CourseRead)
def create_course(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthService = Depends(get_auth_service),
    service: service.CourseService = Depends(get_course_service),
    course_create: CourseCreate = Body(...),
    session: Session = Depends(get_session),
):
    current_user = auth_service.get_my_by_token(
        credentials.credentials, session=session)
    return service.create_course(course_create=course_create, actant_id=current_user["id"], session=session)


@router.patch("/{course_id}", response_model=CourseRead)
def update_course(
    course_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthService = Depends(get_auth_service),
    service: service.CourseService = Depends(get_course_service),
    course_update: CourseUpdate = Body(...),
    session: Session = Depends(get_session),
):
    auth_service(credentials.credentials)
    return service.update_course(course_id=course_id, course_update=course_update, session=session)


@router.post("/{course_id}/apply", response_model=PaymentRead)
def apply_course(
    course_id: str,
    payment_apply_course: PaymentApplyCourse = Body(...),
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthService = Depends(get_auth_service),
    session: Session = Depends(get_session),
    course_service: service.CourseService = Depends(get_course_service),
):
    current_user = auth_service.get_my_by_token(
        credentials.credentials, session=session)
    return course_service.apply_course(course_id=course_id, payment_apply_course=payment_apply_course, actant_id=current_user['id'], session=session)


@router.post("/{course_id}/complete", response_model=CourseRead)
def complete_course_registration(
    course_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthService = Depends(get_auth_service),
    session: Session = Depends(get_session),
    course_service: service.CourseService = Depends(get_course_service),
):
    current_user = auth_service.get_my_by_token(
        credentials.credentials, session=session)
    return course_service.complete_course(course_id=course_id, actant_id=current_user['id'], session=session)
