import random
from datetime import date, timedelta

from sqlalchemy.orm import Session
from tqdm import tqdm

from ..entities.courses import Course, CourseStatusEnum
from ..entities.tests import Test, TestStatusEnum
from ..entities.users import User

BATCH_SIZE = 50000  # 한 번에 insert할 수 있는 최대 안정적 배치


def seed_users(session: Session, user_count: int = 10):
    existing_users = session.query(User.id).first()
    if existing_users:
        print(
            f"{existing_users} users already exist. Skipping user seeding.", flush=True)
        return

    print("Seeding users...", flush=True)
    users = []
    for i in tqdm(range(user_count), desc="Users", unit="user"):
        user = User(
            username=f"user{i+1}",
            email=f"user{i+1}@example.com",
            password="password",
        )
        users.append(user)

        if len(users) >= BATCH_SIZE:
            session.bulk_save_objects(users)
            session.commit()
            users = []

    if users:
        session.bulk_save_objects(users)
        session.commit()
    print(f"Seeded {user_count} users successfully!", flush=True)


def seed_courses_and_tests(session: Session, course_count: int = 1000000, test_count: int = 1000000):
    users = session.query(User).filter(User.isDestroyed.is_(False)).all()
    if not users:
        raise ValueError("No users found. Seed users first.")

    # Courses
    print("Seeding courses...", flush=True)
    courses = []
    for i in tqdm(range(course_count), desc="Courses", unit="course"):
        actant = random.choice(users)
        course = Course(
            title=f"Course {i}",
            description="Auto-generated course",
            startAt=date.today(),
            endAt=date.today() + timedelta(days=random.randint(1, 7)),
            actantId=actant.id,
            status=CourseStatusEnum.AVAILABLE,
            cost=10000
        )
        courses.append(course)

        if len(courses) >= BATCH_SIZE:
            session.bulk_save_objects(courses)
            session.commit()
            courses = []

    if courses:
        session.bulk_save_objects(courses)
        session.commit()

    # Tests
    print("Seeding tests...", flush=True)
    tests = []
    for i in tqdm(range(test_count), desc="Tests", unit="test"):
        actant = random.choice(users)
        test = Test(
            title=f"Test {i}",
            description="Auto-generated test",
            startAt=date.today(),
            endAt=date.today() + timedelta(days=random.randint(1, 7)),
            actantId=actant.id,
            status=TestStatusEnum.AVAILABLE,
            cost=5000
        )
        tests.append(test)

        if len(tests) >= BATCH_SIZE:
            session.bulk_save_objects(tests)
            session.commit()
            tests = []

    if tests:
        session.bulk_save_objects(tests)
        session.commit()

    print(
        f"Seeded {course_count} courses and {test_count} tests successfully!", flush=True)
