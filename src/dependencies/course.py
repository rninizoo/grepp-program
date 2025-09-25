
from ..features.courses import service


def get_course_service() -> service.CourseService:
    return service.CourseService()
