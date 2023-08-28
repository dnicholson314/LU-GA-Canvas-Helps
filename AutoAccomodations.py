"""
A command line script that automatically applies quiz/test time limit accomodations for a given student in a given Canvas course.

Imports the following modules:

* `canvasapi`: to access information from Canvas courses
* `dotenv`: to load variables containing Canvas API information from an .env file
* `os`: to collect the values of the environment variables in the .env file 
"""

from canvasapi import Canvas
from dotenv import load_dotenv
from os import getenv

def select_course(canvas):
    """
    Uses a simple command line interface to prompt the user to choose a modifiable course. In order for a user to select a course, they must be added as a Designer to the course in Canvas.

    Parameters
    ----------
    `canvas`: [Canvas](https://canvasapi.readthedocs.io/en/stable/canvas-ref.html).
        Provides access to the Canvas API, from which the function collects course data.

    Returns
    -------
    [Course](https://canvasapi.readthedocs.io/en/stable/course-ref.html)
        Points to the course the user chose.
    """

    course_results = canvas.get_courses(enrollment_type="designer")

    while True:
        print("Which course would you like to access?")
        print("The options are: ")
        for course in course_results:
            print(f"- {course.name}")

        course_input = input("Choose one of the above options: ")
        course_query = course_input.strip().upper()
        course_results = list(filter(lambda course: course_query in course.name.strip().upper(), course_results))

        if len(course_results) == 0:
            print("No such course was found.")
            course_results = canvas.get_courses(enrollment_type="designer")
        elif len(course_results) == 1:
            course = course_results[0]
            print(f"You chose {course.name}.")
            return course

def select_student_in_course(course):
    """
    Uses a simple command line interface to prompt the user to choose a student from a given course.

    Parameters
    ----------
    `course`: [Course](https://canvasapi.readthedocs.io/en/stable/course-ref.html)
        The course to pull student information from.

    Returns
    -------
    [User](https://canvasapi.readthedocs.io/en/stable/user-ref.html)
        Points to the student the user chose.
    """

    students = course.get_users(enrollment_type="student")

    student_results = students

    while True:
        student_input = input("Search for the name of the student with accomodations: ")
        student_query = student_input.strip().lower()
        student_results = list(filter(lambda student: student_query in student.name.strip().lower(), student_results))

        student_results_len = len(student_results)

        if student_results_len == 0:
            print("No such student was found.")
            student_results = students
            continue
        elif student_results_len == 1:
            selected_student = student_results[0]
            print(f"You chose {selected_student.name}.")
            return selected_student

        print(f"Your query returned {student_results_len} students.")
        print("Here are their names:")
        for student in student_results:
            print(f"- {student.name}")

def modify_extensions_for_quizzes(course, student, time_multiplier):
    """
    Updates the time limit extensions for all quizzes in the given course for the given student, setting them equal to `time_multiplier` times the time limit for the quiz.

    Parameters
    ----------
    `course`: [Course](https://canvasapi.readthedocs.io/en/stable/course-ref.html)
        The course to pull quiz information from.

    `student`: [User](https://canvasapi.readthedocs.io/en/stable/user-ref.html)
        The student to modify time limit extensions for.
    
    `time_multiplier`: float
        The proportion of the time limit that should be added as a time limit extension for each quiz.
    """

    quizzes = course.get_quizzes()

    for quiz in quizzes:
        if quiz.time_limit == None:
            continue

        extra_time = quiz.time_limit * time_multiplier

        print(f"Updating {quiz.title} (current time limit is {quiz.time_limit} minutes)...")

        quiz.set_extensions([
            {
                "user_id": student.id,
                "extra_time": extra_time
            }
        ])

        print(f"{quiz.title} updated! {student.name} now has {extra_time} minutes extra on this quiz.")

# Load .env file from folder.
load_dotenv()

# Load the Canvas API variables from the .env file.
API_URL = getenv("CANVAS_API_URL")
API_KEY = getenv("CANVAS_API_KEY")

canvas = Canvas(API_URL, API_KEY)

course = select_course(canvas)

while True:
    print("\n\n\n")
    student = select_student_in_course(course)

    print("\n\n\n")
    time_multiplier = int(input("Enter the percentage of time to add (e.g. '50' for 50%): "))/100
    modify_extensions_for_quizzes(course, student, time_multiplier)

    print("\n\n\n")
    keep_looping = input(f"\n Would you like to modify accomodations for another student in {course.name}? (y/n): ")
    if keep_looping != "y":
        break