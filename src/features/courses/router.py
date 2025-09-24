from typing import Literal

from fastapi import APIRouter, Body, Depends, Query
from sqlmodel import Session

from ...features.users.schemas import UserRead
from ...shared.database import get_session
from ...shared.security import authenticate_token
from . import service
from .schemas import CourseCreate, CourseQueryOpts, CourseRead, CourseUpdate

router = APIRouter(prefix="/courses", tags=["courses"])

@router.get("", response_model=list[CourseRead])
def get_courses(status: str = Query("AVAILABLE", description="Filter by Course status"), sort: Literal["created", "popular"] = Query("created", description="Sort by created or popular"),skip: int = 0, limit: int = 100, session: Session = Depends(get_session)):

    query_opts = CourseQueryOpts(status=status, sort=sort)
    return service.find_courses(session=session, skip=skip, limit=limit, query_opts = query_opts)

@router.post("", response_model=CourseRead)
def create_course(current_user: UserRead = Depends(authenticate_token), course_create: CourseCreate = Body(...), session: Session = Depends(get_session)):
    return service.create_course(course_create=course_create, actant_id=current_user["id"], session=session)

@router.patch("/{course_id}", response_model=CourseRead)
def update_course(course_id: int, course_update: CourseUpdate = Body(...), current_user: UserRead = Depends(authenticate_token), session: Session = Depends(get_session)):
    return service.update_course(course_id=course_id, course_update=course_update, actant_id=current_user["id"], session=session)


