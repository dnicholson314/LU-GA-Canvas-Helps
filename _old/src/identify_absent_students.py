import requests

import modules.thutils as thu

def get_absent_students(auth_header, course, tolerance):
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
    
        if classes_missed >= 1:
            name = student["name"]
            absent_students[name] = classes_missed

    return absent_students

auth_header = thu.get_auth_header_for_session()
course = thu.prompt_user_for_th_course(auth_header)
tolerance = int(input("Enter the max number of absences for the course (generally 4): "))

absent_students = get_absent_students(auth_header, course, tolerance)

s = "s" if tolerance - 1 != 1 else ""
print()
print(f"Here are all the students with {tolerance - 1} absence{s}: ")
for student, absences in absent_students.items():
    if absences == tolerance - 1:
        print(f"    {student}: {absences}")

s = "s" if tolerance != 1 else ""
print()
print(f"Here are all the students with {tolerance} or more absence{s}: ")
for student, absences in absent_students.items():
    if absences >= tolerance:
        print(f"    {student}: {absences}")

print()
input("Press ENTER to quit.")