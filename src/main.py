import traceback as tb

try:
    import identify_absent_students, identify_quiz_concerns, modify_due_dates, modify_time_limits, post_final_grades, search_student_by_name, update_attendance_verification
except Exception as e:
    print()
    print("Encountered exception ----------------------------------")
    print(e.args[0])
    tb.print_tb(e.__traceback__)
    print("--------------------------------------------------------")
    input("Press ENTER to continue.")

menu = """\
Welcome to LUGACH! Please choose one of the following options:
    (1) Identify Absent Students
    (2) Identify Quiz Concerns
    (3) Modify Due Dates
    (4) Modify Time Limits
    (5) Post Final Grades
    (6) Search Student by Name
    (7) Update Attendance Verification
    (999) Quit application
"""
def process_choice(choice):
    match choice:
        case 1:
            identify_absent_students.main()
        case 2:
            identify_quiz_concerns.main()
        case 3:
            modify_due_dates.main()
        case 4:
            modify_time_limits.main()
        case 5:
            post_final_grades.main()
        case 6:
            search_student_by_name.main()
        case 7:
            update_attendance_verification.main()
        case 999:
            quit()
        case _:
            print("Please enter one of the options")

def main():
    while True:
        print(menu)
        choice = 0
        try:
            choice = int(input("Choose an option: "))
        except ValueError:
            print("Please enter a number.")
        
        try:
            process_choice(choice)
        except Exception as e:
            print()
            print("Encountered exception ----------------------------------")
            print(e.args[0])
            tb.print_tb(e.__traceback__)
            print("--------------------------------------------------------")
            input("Press ENTER to continue.")

if __name__ == "__main__":
    main()