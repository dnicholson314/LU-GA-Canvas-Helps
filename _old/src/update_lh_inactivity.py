import lhutils as lhu
import cvutils as cvu
import thutils as thu

import requests

def get_th_student_from_lh_student(lh_student, all_th_students):
    email = lh_student["emailAddress"]

    th_student = None
    th_student_matches = [student for student in all_th_students 
                          if cvu.sanitize_string(email) in cvu.sanitize_string(student["email"])]
    num_matches = len(th_student_matches)

    if num_matches == 0:
        print(f"No corresponding TH student was found for LH student {name}.")
        return None
    elif num_matches > 1:
        print(f"The query for LH student {name} returned {num_matches} results in Top Hat.")
        print("Here are their names:")
        for index, th_student in enumerate(th_student_matches, start=1):
            print(f"{index}. {th_student['name']}")

        index = int(input(f"Enter the index of the student named {name}: "))
        return th_student_matches[index - 1]
    else:
        return th_student_matches[0]

canvas = cvu.get_canvas_object_from_env_file()
cv_course = cvu.prompt_for_course(canvas)

th_auth_header = thu.get_auth_header_for_session()
th_course = thu.prompt_user_for_th_course(th_auth_header)

username, password = lhu.get_liberty_credentials_from_env_file()
course_sis_id, lh_auth_header = lhu.get_lh_auth_credentials_for_session(cv_course, username, password)

all_lh_students = lhu.get_lh_students(course_sis_id, lh_auth_header)
all_th_students = thu.get_th_students(th_auth_header, th_course)

for num_students, lh_student in enumerate(all_lh_students, start=1):
    name = f"{lh_student["firstName"]} {lh_student["lastName"]}"

    if lh_student['daysSinceLastActivity'] < 14:
        print(f"Skipped {name} because they attended in the last 14 days... ({num_students} processed so far)")
        continue

    if lh_student["status"] == "REMOVED":
        print(f"Skipped {name} because they are no longer enrolled in the course... ({num_students} processed so far)")
        continue

    th_student = get_th_student_from_lh_student(lh_student, all_th_students)
    if not th_student:
        print(f"Skipped {name} because they were not found in TH... ({num_students} processed so far)")
        continue

    attendance_records = thu.get_th_student_attendance_records(th_course, th_student, th_auth_header)

    for record in attendance_records:
        student_id = th_student["id"]
        course_id = th_course["course_id"]
        record_id = record["item_id"]
        response = requests.get(url=f"https://app.tophat.com/api/gradebook/v1/gradeable_items/{course_id}/item/{record_id}/grades/?student_ids={student_id}", headers=th_auth_header)

        print(response.text)