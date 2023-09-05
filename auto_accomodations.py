"""
A command line script that automatically applies quiz/test time limit accomodations 
for a given student in a given Canvas course.

Imports from the following modules:

* `canvasapi`: to access information from Canvas courses
* `dotenv`: to load variables containing Canvas API information from an .env file
* `dateutil`: to parse datetime strings denoting the start dates of Canvas courses
* `os`: to collect the values of the environment variables in the .env file
"""

from canvasapi import Canvas
from dateutil.parser import parse
from dotenv import load_dotenv
from os import getenv

def create_canvas_object_from_env_file():
    # Load .env file from folder.
    if not load_dotenv():
        print("No API details found. Did you create a .env file with the Canvas URL and your API key?")
        raise FileNotFoundError()

    # Load the Canvas API variables from the .env file.
    try:
        API_URL = getenv("CANVAS_API_URL")
        API_KEY = getenv("CANVAS_API_KEY")
    except Exception as e:
        print("Failed to load the URL and API key from the .env file.")
        raise(e)

    try:
        canvas = Canvas(API_URL, API_KEY)
    except Exception as e:
        print("Invalid URL or API key. Check your .env file to make sure you typed the values properly.")
        raise(e)
    
    return canvas

def select_course(canvas):
    """
    Uses a simple command line interface to prompt the user to choose a modifiable course. 
    In order for a user to select a course, they must be added as a Designer to the course in Canvas.

    Parameters
    ----------
    `canvas`: [Canvas](https://canvasapi.readthedocs.io/en/stable/canvas-ref.html).
        Provides access to the Canvas API, from which the function collects course data.

    Returns
    -------
    [Course](https://canvasapi.readthedocs.io/en/stable/course-ref.html)
        Points to the course the user chose.
    """
    
    all_course_results = canvas.get_courses(enrollment_type="designer")
    INIT_COURSE_RESULTS = list(filter(lambda course: course.start_at != None, all_course_results))
    course_results = INIT_COURSE_RESULTS

    def match_course(course_query, course):
        sanitized_name = course.name.strip().upper()
        start_date = parse(course.start_at)
        course_name_with_date = f"- {course.name} ({start_date.month}-{start_date.year})"

        return course_query in course_name_with_date

    while True:
        print("Which course would you like to access?")
        print("The options are: \n")
        for course in course_results:
            start_date = parse(course.start_at)
            print(f"    {course.name} ({start_date.month}-{start_date.year})")

        course_input = input("\nChoose one of the above options: ")
        course_query = course_input.strip().upper()
        course_results = list(filter(lambda course: match_course(course_query, course), course_results))

        if len(course_results) == 0:
            print("No such course was found.")
            course_results = INIT_COURSE_RESULTS
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

    ALL_STUDENTS = course.get_users(enrollment_type="student")

    student_results = ALL_STUDENTS

    def match_student(student_query, student):
        global students_searched
        students_searched += 1
        print(f"Searching students ({students_searched} so far)...", end="\r")

        return student_query in student.name.strip().lower()

    while True:
        global students_searched
        students_searched = 0

        student_input = input("Search for the name of the student with accomodations: ")
        student_query = student_input.strip().lower()
        student_results = list(filter(lambda student: match_student(student_query, student), student_results))

        student_results_len = len(student_results)

        if student_results_len == 0:
            print("\nNo such student was found.")
            student_results = ALL_STUDENTS
            continue
        elif student_results_len == 1:
            selected_student = student_results[0]
            print(f"\nYou chose {selected_student.name}.")
            return selected_student

        print(f"\nYour query returned {student_results_len} students.")
        print("Here are their names:\n")
        for student in student_results:
            print(f"    {student.name}")
        print()

def modify_extensions_for_quizzes(course, student, time_multiplier):
    """
    Updates the time limit extensions for all quizzes in the given course 
    for the given student, setting them equal to `time_multiplier` times 
    the time limit for the quiz.

    Parameters
    ----------
    `course`: [Course](https://canvasapi.readthedocs.io/en/stable/course-ref.html)
        The course to pull quiz information from.

    `student`: [User](https://canvasapi.readthedocs.io/en/stable/user-ref.html)
        The student to modify time limit extensions for.
    
    `time_multiplier`: float
        The proportion of the time limit that should be added as a time limit 
        extension for each quiz.
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

canvas = create_canvas_object_from_env_file()
course = select_course(canvas)

while True:
    print()
    student = select_student_in_course(course)

    print()
    while True:
        try:
            time_multiplier = int(input("Enter the percentage of time to add (e.g. '50' for 50%): "))/100
            break
        except ValueError:
            print("Invalid input, try again.")

    modify_extensions_for_quizzes(course, student, time_multiplier)

    print()
    keep_looping = input(f"\n Would you like to modify accomodations for another student in {course.name}? (y/n): ")
    if keep_looping != "y":
        break