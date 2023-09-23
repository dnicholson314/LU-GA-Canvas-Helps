import modules.canvasapiutils as cvu

from dateutil.parser import parse
from dateutil.parser._parser import ParserError

canvas = cvu.create_canvas_object()
course = cvu.prompt_for_course(canvas)

while True:
    print()
    student = cvu.prompt_for_student(course)
    print()
    assignment = cvu.prompt_for_assignment(course)
    print()
    
    due_date = parse(assignment.due_at)
    print(f"The current due date is {due_date.date()}.")
    try:
        date_query = input(f"Type a value for the new due date (mm-dd-YYYY): ")
        due_date = parse(date_query)
    except ParserError as pe:
        print(pe.args[0])

    assignment.create_override(assignment_override={"student_ids": [student.id], "title": student.name, "due_at": due_date, "lock_at": due_date})

    keep_looping = input(f"Would you like to modify accomodations for another student in {course.name}? (y/n): ")
    if keep_looping != "y":
        break