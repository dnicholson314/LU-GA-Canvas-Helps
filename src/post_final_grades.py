import _lhutils as lhu
import _cvutils as cvu
import requests
import _constants as cs

canvas = cvu.create_canvas_object()
course = cvu.prompt_for_course(canvas)

username, password = lhu.get_liberty_credentials_from_env_file()
course_sis_id, lh_auth_header = lhu.get_lh_auth_credentials_for_session(course, username, password)

students = lhu.get_lh_students(course_sis_id, lh_auth_header)

def post_final_grade(course_sis_id, lh_auth_header, student, grade):
    if grade not in ["A", "B", "C", "D", "F"]:
        raise TypeError("Expected a letter grade (A, B, C, D, or F) for the grade parameter.")

    id = student["id"]
    grades_url = f"https://lighthouse.okd.liberty.edu/rest/enrollments/{id}/grade?courseSisId={course_sis_id}&sis=banner&lms=canvas_lu"
    payload = {
        "grade": grade
    }

    for i in range(1, cs.RELOAD_ATTEMPTS + 1):
        response = requests.post(url=grades_url, json=payload, headers=lh_auth_header)
        if response.status_code != 200:
            print(f"{response.request.method} request returned with code {response.status_code}; retrying... ({i} of {cs.RELOAD_ATTEMPTS} attempts so far)")
            continue

        break
    else:
        raise PermissionError("Failed to log into Lighthouse.")

    return True

for i, student in enumerate(students):
    name = student["firstName"] + " " + student["lastName"]

    status = student["status"]
    if status == "REMOVED":
        print(f"Student {name} was removed from the course... ({i} so far)")
        continue

    activity = student["daysSinceLastActivity"]
    if activity >= 21:
        print(f"Student {name} had 21 days of inactivity... ({i} so far)")
        continue

    points = student["points"]
    if points == 0:
        print(f"Student {name} had 0 points... ({i} so far)")
        continue
    
    grade = student["finalGrade"]
    if grade:
        print(f"Student {name} already has grade {grade} assigned... ({i} so far)")
        continue

    if points >= 895:
        grade = "A"
    elif points >= 795:
        grade = "B"
    elif points >= 695:
        grade = "C"
    elif points >= 595:
        grade = "D"
    else:
        grade = "F"

    final_grade_posted = post_final_grade(course_sis_id, lh_auth_header, student, grade)
    if not final_grade_posted:
        print(f"Final grade failed to post for {student}... ({i} so far)")
        continue

    print(f"Posted final grade {grade} for student {name} with {points} points... ({i} so far)")