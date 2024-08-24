import os

import lugach.cvutils as cvu
import dotenv as dv
import requests
from enum import Enum
from datetime import datetime

class AttendanceOptions(Enum):
    PRESENT = 0
    ABSENT = 1
    EXCUSED = 2

def get_th_auth_token_from_env_file() -> dict[str,str]:
    if not dv.find_dotenv():
        raise FileNotFoundError("No .env file was found.")

    dv.load_dotenv()    
    TH_AUTH_KEY = os.getenv("TH_AUTH_KEY")
    if not TH_AUTH_KEY:
        raise NameError("Failed to load TH auth key from .env file.")

    return TH_AUTH_KEY

def get_auth_header_for_session() -> str:
    jwt_url = 'https://app.tophat.com/identity/v1/refresh_jwt/'
    jwt_data = {
        "th_jwt_refresh": get_th_auth_token_from_env_file(),
    }

    jwt_response = requests.post(jwt_url, json=jwt_data)

    if jwt_response.status_code != 201:
        raise ConnectionRefusedError("Unable to obtain JWT token")

    print("JWT bearer token obtained!")
    jwt_token = jwt_response.json()["th_jwt"]

    auth_header = {
        "Authorization": f"Bearer {jwt_token}"
    }
    return auth_header

def get_th_courses(auth_header):
    courses_url = "https://app.tophat.com/api/v2/courses/"

    response = requests.get(courses_url, headers=auth_header)
    payload = response.json()

    courses = payload["objects"]

    return courses

def prompt_user_for_th_course(auth_header: dict[str, str]) -> dict[str]:
    raw_courses = get_th_courses(auth_header)
    courses_dict = {}

    for course in raw_courses:
        name = course["course_name"]
        courses_dict[name] = course

    course_results = courses_dict
    course = None

    while True:
        print("Which course would you like to access?")
        print("The options are: ")
        for name in course_results.keys():
            print(f"    {name}")

        query = input("Choose one of the above options: ")
        course_results = {name:course for name, course in course_results.items() if cvu.sanitize_string(query) in cvu.sanitize_string(name)}

        if len(course_results) == 0:
            print("No such course was found.")
            course_results = courses_dict
        elif len(course_results) == 1:
            name = list(course_results)[0]
            course = course_results[name]
            print(f"You chose {name}.")
            return course

def get_th_students(auth_header: dict[str, str], course: dict[str]) -> list[dict]:
    course_id = course["course_id"]
    students_url = f"https://app.tophat.com/api/v3/course/{course_id}/students/"

    response = requests.get(url=students_url, headers=auth_header)

    students = response.json()
    return students

def prompt_user_for_th_student(course: dict[str], auth_header: dict[str, str]) -> dict[str]:
    all_students = get_th_students(auth_header, course)
    student_results = all_students
    student = None

    while True:
        query = input("Search for the student by name: ")
        student_results = [student for student in student_results if cvu.sanitize_string(query) in cvu.sanitize_string(student["name"])]

        students_len = len(student_results)

        if students_len == 0:
            print("\nNo such student was found.")
            student_results = all_students
            continue
        elif students_len == 1:
            student = student_results[0]
            print(f"You chose {student['name']}.")
            return student

        print(f"\nYour query returned {students_len} students.")
        print("Here are their names:\n")
        for student in student_results:
            print(f"    {student['name']}")
        print()

def get_th_attendance_proportion(course: dict[str], student: dict[str], auth_header: dict[str, str]) -> tuple[int, int]:
    course_id = course["course_id"]
    metadata_url = f"https://app.tophat.com/api/gradebook/v1/gradeable_items/{course_id}/student/{student["id"]}/metadata/"
    response = requests.get(url=metadata_url, headers=auth_header)
    metadata = response.json()

    attended = metadata['attended_count']
    total = metadata['attendance_count']

    return (attended, total)

def _get_th_attendance_item_names_and_ids(course: dict[str], auth_header: dict[str, str]) -> list[tuple[str, int]]:
    """
    """
    course_id = course["course_id"]
    course_item_url = f"https://app.tophat.com/api/v3/course/{course_id}/gradeable_course_items_aggregated/"
    response = requests.get(url=course_item_url, headers=auth_header)
    course_items = response.json()

    attendance_item_names_and_ids = [(course_item["name"], course_item["id"]) for course_item in course_items if course_item["type"] == "attendance"]
    return attendance_item_names_and_ids

def _get_attendance_gradebook_data(course: dict[str], student: dict[str], auth_header: dict[str, str]) -> list[dict]:
    """
    This data provides information necessary to determine whether a given absence was excused or not.
    """
    course_id = course["course_id"]
    response = requests.get(f"https://app.tophat.com/api/gradebook/v1/gradeable_items/{course_id}/?limit=2000&student_ids={student["id"]}", headers=auth_header)
    attendance_gradebook_data = response.json()

    return attendance_gradebook_data["results"]

def _find_attendance_item_in_attendance_gradebook_data(attendance_gradebook_data: list[dict], attendance_item_id: int | str) -> dict:
    """
    This function facilitates searching data from the attendance gradebook endpoint by the ID provided by the attendance answers endpoint.
    """
    attendance_item_id = str(attendance_item_id)

    for attendance_gradebook_entry in attendance_gradebook_data:
        if "item_id" not in attendance_gradebook_entry:
            continue

        entry_item_id = attendance_gradebook_entry["item_id"]
        if entry_item_id == attendance_item_id:
            return attendance_gradebook_entry

    return {}

def get_attendance_records_for_student_in_course(course: dict[str], student: dict[str], auth_header: dict[str, str]) -> list[dict]:
    attendance_item_names_and_ids = _get_th_attendance_item_names_and_ids(course, auth_header)
    attendance_gradebook_data = _get_attendance_gradebook_data(course, student, auth_header)

    attendance_records = []
    for name, id in attendance_item_names_and_ids:
        attendance_item = _find_attendance_item_in_attendance_gradebook_data(attendance_gradebook_data, id)

        date_taken_str = name[:10] # Strip off the time
        date_taken = datetime.strptime(date_taken_str, "%Y-%m-%d").date()

        attended = attendance_item["weighted_correctness"] == 1
        excused = attendance_item["grade_type"] == "excused"

        attendance_records.append({
            "date_taken": date_taken,
            "attended": attended,
            "excused": excused,
            "id": id,
        })

    return attendance_records

def edit_attendance(course_id: int, student_id: int, attendance_id: int, new_attendance: AttendanceOptions, auth_header: dict[str, str]):
    if type(new_attendance) != AttendanceOptions:
        raise TypeError("Expected new_attendance to be an option from AttendanceOptions.")

    if new_attendance == AttendanceOptions.PRESENT:
        attended = True
        excused = False
    elif new_attendance == AttendanceOptions.ABSENT:
        attended = False
        excused = False
    else:
        attended = False
        excused = True

    edit_attendance_url = f"https://app.tophat.com/api/gradebook/v1/gradeable_items/{course_id}/edit/{attendance_id}/"
    edit_attendance_data = {
        "student_id": student_id,
        "weighted_correctness": 1 if attended else 0,
        "correctness_weight": 0 if excused else 1,
        "weighted_participation": 0,
        "participation_weight": 0,
        "is_excused": excused,
        "is_manual_entry": False,
        "return_tree_type": "selective",
    }
    response = requests.post(url=edit_attendance_url, json=edit_attendance_data, headers=auth_header)
    response.raise_for_status()

    print("Successfully modified attendance!")