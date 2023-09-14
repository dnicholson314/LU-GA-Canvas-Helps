"""
A command line script that automatically applies quiz/test time limit accomodations 
for a given student in a given Canvas course.

Imports from the following modules:

* `canvasapi`: to access information from Canvas courses
* `dotenv`: to load variables containing Canvas API information from an .env file
* `dateutil`: to parse datetime strings denoting the start dates of Canvas courses
* `os`: to collect the values of the environment variables in the .env file
"""
import cvapiutils

canvas = cvapiutils.create_canvas_object()
course = cvapiutils.prompt_for_course(canvas)

while True:
    print()
    student = cvapiutils.prompt_for_student(course)
    
    print()
    while True:
        try:
            time_multiplier = int(input("Enter the percentage of time to add (e.g. '50' for 50%): "))/100
            break
        except ValueError:
            print("Invalid input, try again.")

    cvapiutils.set_time_limits_for_quizzes(course, student, time_multiplier)

    print()
    keep_looping = input(f"Would you like to modify accomodations for another student in {course.name}? (y/n): ")
    if keep_looping != "y":
        break