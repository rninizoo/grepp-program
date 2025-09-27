import csv
import random
from datetime import date, datetime, timedelta, timezone
from io import StringIO

import ulid
from sqlalchemy import text
from sqlalchemy.engine import Engine
from tqdm import tqdm

from ..entities.courses import CourseStatusEnum
from ..entities.tests import TestStatusEnum

BATCH_SIZE = 50000  # COPY 한 번에 처리할 건수


def seed_users(engine: Engine, user_count: int = 10):
    print("Seeding users...")
    with engine.connect() as conn:
        result = conn.execute(text("SELECT id FROM users LIMIT 1"))
        if result.first():
            print("Users already exist. Skipping.")
            return

    now = datetime.now(timezone.utc)
    users = [{"id": str(ulid.new()), "username": f"user{i+1}",
              "email": f"user{i+1}@example.com", "password": "password",
              "createdAt": now,  "isDestroyed": False} for i in range(user_count)]

    output = StringIO()
    writer = csv.writer(output)
    for u in tqdm(users, desc="Users"):
        writer.writerow([u["id"], u["username"], u["email"],
                        u["password"], u["createdAt"], u["isDestroyed"]])

    output.seek(0)
    conn = engine.raw_connection()
    cursor = conn.cursor()
    cursor.copy_expert(
        'COPY users(id, username, email, password, "createdAt", "isDestroyed") FROM STDIN WITH CSV',
        output
    )
    conn.commit()
    cursor.close()
    conn.close()
    print(f"Seeded {user_count} users successfully!")


def seed_courses_and_tests(engine: Engine, course_count: int = 1000000, test_count: int = 1000000):
    print("Seeding courses and tests...")

    # Users ID 가져오기
    with engine.connect() as conn:
        result = conn.execute(
            text('SELECT id FROM users WHERE "isDestroyed" = false'))
        user_ids = [row[0] for row in result.fetchall()]
        if not user_ids:
            raise ValueError("No users found. Seed users first.")

    now = datetime.now(timezone.utc)

    # Courses
    print("Seeding courses...")
    output = StringIO()
    writer = csv.writer(output)
    for i in tqdm(range(course_count), desc="Courses"):
        course_id = str(ulid.new())
        actant_id = random.choice(user_ids)
        start_at = date.today()
        end_at = start_at + timedelta(days=random.randint(1, 7))
        writer.writerow([course_id, f"Course {i}", "Auto-generated course",
                         start_at, end_at, actant_id, CourseStatusEnum.AVAILABLE.value,
                         10000, 0, now, False])

        if (i + 1) % BATCH_SIZE == 0 or i + 1 == course_count:
            output.seek(0)
            conn = engine.raw_connection()
            cursor = conn.cursor()
            cursor.copy_expert(
                'COPY courses(id, title, description, "startAt", "endAt", "actantId", status, cost, "studentCount", "createdAt", "isDestroyed") FROM STDIN WITH CSV',
                output
            )
            conn.commit()
            cursor.close()
            conn.close()
            output = StringIO()
            writer = csv.writer(output)

    # Tests
    print("Seeding tests...")
    output = StringIO()
    writer = csv.writer(output)
    for i in tqdm(range(test_count), desc="Tests"):
        test_id = str(ulid.new())
        actant_id = random.choice(user_ids)
        start_at = date.today()
        end_at = start_at + timedelta(days=random.randint(1, 7))
        writer.writerow([test_id, f"Test {i}", "Auto-generated test",
                         start_at, end_at, actant_id, TestStatusEnum.AVAILABLE.value,
                         5000, 0, now, False])

        if (i + 1) % BATCH_SIZE == 0 or i + 1 == test_count:
            output.seek(0)
            conn = engine.raw_connection()
            cursor = conn.cursor()
            cursor.copy_expert(
                'COPY tests(id, title, description, "startAt", "endAt", "actantId", status, cost, "examineeCount", "createdAt", "isDestroyed") FROM STDIN WITH CSV',
                output
            )
            conn.commit()
            cursor.close()
            conn.close()
            output = StringIO()
            writer = csv.writer(output)

    print(f"Seeded {course_count} courses and {test_count} tests successfully!")
