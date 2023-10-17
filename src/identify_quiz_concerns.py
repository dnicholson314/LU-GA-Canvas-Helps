import modules.cvutils as cvu

CHUNK_SIZE = 20
TOLERANCE = 3

canvas = cvu.create_canvas_object()
course = cvu.prompt_for_course(canvas)
print()
name = input("Enter your name (this will go in the signature of the email): ")
print()

CONCERN_SUBJECT = f"Quiz concern - {course.name}"
CONCERN_MESSAGE = f"Hello, I've noticed that you've missed multiple quizzes this semester. Make sure to keep up with the class announcements and modules in Canvas. There are two extra credit opportunities that can help you make up the points missed due at the end of the semester.\n\nLet me know if you have any questions!\n{name}"

def find_quiz_concern_students(course):
    student_ids = [student.id for student in course.get_users(enrollment_type="student")]
    quiz_ids = [assn.id for assn in course.get_assignments(bucket="past", order_by="due_at") if "online_quiz" in assn.submission_types]

    quiz_concern_students = {}

    for i in range(0, len(student_ids), CHUNK_SIZE):
        print(f"Checking students ({i} so far)...")
        
        chunk = student_ids[i: i + CHUNK_SIZE]
        student_groups = course.get_multiple_submissions(student_ids = chunk, assignment_ids = quiz_ids, grouped = True)

        for student_group in student_groups:
            missed_assignments = [submission.missing for submission in student_group.submissions]

            if missed_assignments.count(True) >= TOLERANCE:
                submission = student_group.submissions[0]
                student = course.get_user(submission.user_id)
                quiz_concern_students[student] = False
    
    return quiz_concern_students

def print_selected_students(quiz_concern_students):
    for i, (student, selected) in enumerate(quiz_concern_students.items()):
        indicator = "*" if selected else " "
        print(f"{indicator} {i+1}. {student.name}")

def confirm_students_for_msg(quiz_concern_students):
    print(f"\nThe following students have missed {TOLERANCE} or more quizzes:")

    while True:
        print_selected_students(quiz_concern_students)

        while True:
            try:
                user_selection = input("Choose the students to message by index (or 'q' to quit): ")
                if user_selection == "q":
                    return quiz_concern_students

                selected_student_index = int(user_selection) - 1
                if not (0 <= selected_student_index < len(quiz_concern_students)):
                    raise ValueError

                break
            except ValueError:
                print("Expected 'q' or an index within range. Try again.")
        
        selected_student = list(quiz_concern_students)[selected_student_index]
        quiz_concern_students[selected_student] = not quiz_concern_students[selected_student]

def send_msg(quiz_concern_students, course):
    quiz_concern_students = confirm_students_for_msg(quiz_concern_students)
    print("------MESSAGE------")
    print()
    print(f"{CONCERN_SUBJECT}")
    print()
    print(f"{CONCERN_MESSAGE}")
    print()
    print("-------------------")
    print_selected_students(quiz_concern_students)
    final_confirmation = input("FINAL CONFIRMATION: Do you want to message these students? (y/n) ")
    if final_confirmation != "y":
        return

    canvas.create_conversation(recipients = [student.id for student in quiz_concern_students],
                               subject = CONCERN_SUBJECT,
                               body = CONCERN_MESSAGE,
                               context_code=f"course_{course.id}")
    print("Message sent!")

quiz_concern_students = find_quiz_concern_students(course)

if len(quiz_concern_students) == 0:
    print("No students need quiz concern emails sent!")
    input("Press ENTER to quit.")
else:
    send_msg(quiz_concern_students, course)