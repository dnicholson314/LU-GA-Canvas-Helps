import os

import dotenv as dv
import requests

import modules.canvasapiutils as cvu


def get_th_auth_token_from_env_file() -> str:
    if not dv.find_dotenv():
        raise FileNotFoundError("No .env file was found.")
    
    dv.load_dotenv()    
    TH_AUTH_KEY = os.getenv("TH_AUTH_KEY")
    if not TH_AUTH_KEY:
        raise NameError("Failed to load TH auth key from .env file.")
    
    return TH_AUTH_KEY

def get_jwt_token_for_session() -> str:
    jwt_url = 'https://app.tophat.com/identity/v1/refresh_jwt/'
    jwt_data = {
        "th_jwt_refresh": get_th_auth_token_from_env_file(),
    }

    jwt_response = requests.post(jwt_url, json=jwt_data)

    jwt_status_code = jwt_response.status_code
    if jwt_status_code != 201:
        raise ConnectionRefusedError("Unable to obtain JWT token")

    print("JWT bearer token obtained!")
    jwt_token = jwt_response.json()["th_jwt"]
    return jwt_token

def prompt_user_for_th_course(auth_header: dict[str, str]) -> dict[str]:
    courses_url = "https://app.tophat.com/api/v2/courses/"

    response = requests.get(courses_url, headers=auth_header)
    payload = response.json()

    raw_courses = payload["objects"]
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

def prompt_user_for_th_student(course: dict[str], auth_header: dict[str, str]) -> dict[str]:
    course_id = course["course_id"]
    students_url = f"https://app.tophat.com/api/v3/course/{course_id}/students/"

    response = requests.get(url=students_url, headers=auth_header)

    all_students = response.json()
    student_results = all_students
    student = None

    while True:
        query = input("Search for the student by name: ")
        student_results = [student for student in student_results if cvu.sanitize_string(query) in cvu.sanitize_string(student["name"])]

        students_len = len(student_results)

        if students_len == 0:
            print("\nNo such student was found.")
            student_results = all_students
        elif students_len == 1:
            student = student_results[0]
            print(f"You chose {student['name']}.")
            return student

        print(f"\nYour query returned {students_len} students.")
        print("Here are their names:\n")
        for student in student_results:
            print(f"    {student['name']}")
        print()

def get_th_student_attendance_records(course: dict[str], student: int, auth_header: dict[str, str], limit=2000) -> list[dict]:
    course_id = course["course_id"]
    student_id = student["id"]
    offset = 0

    init_attendance_url = f"https://app.tophat.com/api/gradebook/v1/gradeable_items/{course_id}/?limit={limit}&offset={offset}&student_ids={student_id}"
    attendance_url = init_attendance_url
    records = []
    while True:
        response = requests.get(url=attendance_url, headers=auth_header)
        payload = response.json()

        if payload["results"]:
            records.extend(payload["results"])
        if not payload["next"]:
            break
        
        offset += limit
        attendance_url = f"https://app.tophat.com/api/gradebook/v1/gradeable_items/{course_id}/?limit={limit}&offset={offset}&student_ids={student_id}"

    return records

def get_th_attendance_proportion(records: list[dict]) -> tuple[int, int]:
    main_records = [record for record in records 
                    if "production" in record["item_id"]
                    and "attendance" in record["item_id"]]
    if len(main_records) != 1:
        raise NotImplementedError("The attendance records had an unexpected number (!= 1) of 'production...attendance' entries.")
    
    main_record = main_records[0]
    
    attended = main_record["weighted_correctness"]
    total = main_record["correctness_weight"]

    return (attended, total)

jwt_token = get_jwt_token_for_session()
auth_header = {
    "Authorization": f"Bearer {jwt_token}"
}

course = prompt_user_for_th_course(auth_header)
course_id = course["course_id"]

students_url = f"https://app.tophat.com/api/v3/course/{course_id}/students/"
response = requests.get(url=students_url, headers=auth_header)
students = response.json()

print()

absent_students = {}
for i, student in zip(range(len(students)), students):
    if i % 50 == 0:
        print(f"Checking student attendance records ({i} so far)...")

    records = get_th_student_attendance_records(course, student, auth_header)
    attendance_proportion = get_th_attendance_proportion(records)
    classes_missed = attendance_proportion[1] - attendance_proportion[0]
   
    if classes_missed >= 3:
        name = student["name"]
        absent_students[name] = classes_missed

three_absences = {student: absences for student, absences in absent_students.items() if absences == 3}
four_plus_absences = {student: absences for student, absences in absent_students.items() if absences >= 4}

print()
print("Here are all the students with three absences: ")
for student, absences in three_absences.items():
    print(f"    {student}: {absences}")

print()
print("Here are all the students with four or more absences: ")
for student, absences in four_plus_absences.items():
    print(f"    {student}: {absences}")

print()
input("Press ENTER to quit.")