import requests

import modules.thutils as thu

auth_header = thu.get_auth_header_for_session()

course = thu.prompt_user_for_th_course(auth_header)
course_id = course["course_id"]

students_url = f"https://app.tophat.com/api/v3/course/{course_id}/students/"
response = requests.get(url=students_url, headers=auth_header)
students = response.json()

print()

absent_students = {}
for i, student in enumerate(students):
    if i % 50 == 0:
        print(f"Checking student attendance records ({i} so far)...")

    records = thu.get_th_student_attendance_records(course, student, auth_header)
    attendance_proportion = thu.get_th_attendance_proportion(records)
    classes_missed = attendance_proportion[1] - attendance_proportion[0]
   
    if classes_missed >= 3:
        name = student["name"]
        absent_students[name] = classes_missed

print()
print("Here are all the students with three absences: ")
for student, absences in absent_students.items():
    if absences == 3:
        print(f"    {student}: {absences}")

print()
print("Here are all the students with four or more absences: ")
for student, absences in absent_students.items():
    if absences >= 4:
        print(f"    {student}: {absences}")

print()
input("Press ENTER to quit.")