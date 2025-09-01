from canvasapi.assignment import Assignment
from canvasapi.course import Course
from canvasapi.user import User
from canvasapi.page import PaginatedList


def parse_canvas_courses_for_cli(courses: PaginatedList | list[Course]) -> list[dict]:
    return [
        {
            "name": course.name,
            "id": course.id,
            "start_at": course.start_at,
            "end_at": course.end_at,
        }
        for course in courses
    ]


def parse_canvas_users_for_cli(
    users: PaginatedList | list[User], filter: str | None
) -> list[dict]:
    if type(users) is PaginatedList:
        users = list(users)

    return [
        {
            "name": user.name,
            "id": user.id,
            "sis_user_id": user.sis_user_id,
            "email": user.email,
        }
        for user in users
        if not filter or filter in user.name
    ]


def parse_canvas_assignments_for_cli(
    assignments: PaginatedList | list[Assignment],
) -> list[dict]:
    if type(assignments) is PaginatedList:
        assignments = list(assignments)

    return [
        {
            "name": assignment.name,
            "id": assignment.id,
            "quiz_id": assignment.quiz_id if hasattr(assignment, "quiz_id") else "",
            "due_at": assignment.due_at,
        }
        for assignment in assignments
    ]


def parse_top_hat_courses_for_cli(courses: list[dict]) -> list[dict]:
    return [
        {
            "name": course["course_name"],
            "id": course["course_id"],
        }
        for course in courses
    ]


def parse_top_hat_students_for_cli(students: list[dict]) -> list[dict]:
    return [
        {
            "name": student["name"],
            "id": student["id"],
            "email": student["email"],
            "sis_user_id": student["student_id"],
        }
        for student in students
    ]
