import cvapiutils

CHUNK_SIZE = 20
TOLERANCE = 3

canvas = cvapiutils.create_canvas_object()
course = cvapiutils.prompt_for_course(canvas)
print()

student_ids = [student.id for student in course.get_users(enrollment_type="student")]
quiz_ids = [assn.id for assn in course.get_assignments(bucket="past", order_by="due_at") if "online_quiz" in assn.submission_types]
quiz_concern_students = []

for i in range(0, len(student_ids), CHUNK_SIZE):
    print(f"Checking students ({i} so far)...")
    
    chunk = student_ids[i: i + CHUNK_SIZE]
    student_groups = course.get_multiple_submissions(student_ids = chunk, assignment_ids = quiz_ids, grouped = True)

    for student_group in student_groups:
        missed_assignments = [submission.missing for submission in student_group.submissions]

        if missed_assignments.count(True) >= TOLERANCE:
            submission = student_group.submissions[0]
            student = course.get_user(submission.user_id)
            quiz_concern_students.append(student)

print(f"\nThe following students have missed {TOLERANCE} or more quizzes:")
for student in quiz_concern_students:
    print(f"    {student.name}")