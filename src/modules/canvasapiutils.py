from datetime import datetime
from os import getenv

from canvasapi import Canvas
from canvasapi.assignment import Assignment
from canvasapi.course import Course
from canvasapi.exceptions import BadRequest
from canvasapi.quiz import Quiz
from canvasapi.user import User
from dateutil.parser import parse
from dotenv import load_dotenv


def printif(string: str, logging: bool) -> None:
    if logging:
        print(string)

def sanitize_string(string: str) -> str:
    """
    Returns a lowercase, whitespace-trimmed version of a given string.

    Parameters
    ----------
    `str`: string
        The string to sanitize.

    Returns
    -------
    string
        The result after sanitizing.
    """
    return string.strip().lower()

def course_name_with_date(course: Course) -> str:
    """
    Prepares courses to be queried by creating a string
    containing the course name and the start date.

    Parameters
    ----------
    `course`: [Course](https://canvasapi.readthedocs.io/en/stable/course-ref.html)
        The course to be converted to a name/date string representation.

    Returns
    -------
    string
        The string containing the course name and start date in the format "NNNNNNNNN (mm-yyyy)."
    """

    start_date = parse(course.start_at)
    return f"{course.name} ({start_date.month}-{start_date.year})" 

def match_course(query: str, course: Course) -> bool:
    sanitized_query = sanitize_string(query)
    sanitized_course_name_with_date = sanitize_string(course_name_with_date(course))

    return sanitized_query in sanitized_course_name_with_date

def create_env_file(api_key: str, api_url="https://canvas.liberty.edu", path=".env") -> None:
    with open(path, "w") as env_file:
        env_file.write(f"CANVAS_API_URL={api_url}" "\n" f"CANVAS_API_KEY={api_key}")

def get_canvas_object_from_env_file(path=".env") -> Canvas:
    load_dotenv(path)
    API_URL = getenv("CANVAS_API_URL")
    API_KEY = getenv("CANVAS_API_KEY")

    canvas = Canvas(API_URL, API_KEY)

    return canvas

def create_canvas_object() -> Canvas:
    while True:
        try:
            canvas = get_canvas_object_from_env_file()
            canvas.get_courses()[0]
            return canvas
        except Exception as e:
            print("Failed to auto-load the URL and API key.")
            api_key = input("Enter your API key from Canvas: ")
            create_env_file(api_key)

def get_courses_from_canvas_object(canvas: Canvas, logging = True, enrolled_as = "designer", **kwargs) -> list[Course]:
    printif("Loading courses from Canvas...", logging)
    courses = canvas.get_courses(enrollment_type=enrolled_as, **kwargs)

    return courses

def filter_courses_by_query(courses: list[Course], query: str) -> list[Course]:
    init_courses = [course for course in courses if course.start_at]
    course_results = [course for course in init_courses if match_course(query, course)]

    return course_results

def prompt_for_course(canvas: Canvas) -> Course:
    """
    Uses a simple command line interface to prompt the user to choose a modifiable course. 
    In order for a user to select a course, they must be added as a Designer to the course in Canvas.
    Additionally, the course must have a start date.

    Parameters
    ----------
    `canvas`: [Canvas](https://canvasapi.readthedocs.io/en/stable/canvas-ref.html).
        Provides access to the Canvas API, from which the function collects course data.

    Returns
    -------
    [Course](https://canvasapi.readthedocs.io/en/stable/course-ref.html)
        Points to the course the user chose.
    """
    
    all_course_results = get_courses_from_canvas_object(canvas)
    course_results = all_course_results

    while True:
        print("Which course would you like to access?")
        print("The options are: \n")
        for course in course_results:
            print(f"    {course_name_with_date(course)}")

        query = input("\nChoose one of the above options: ")
        course_results = filter_courses_by_query(course_results, query)

        if len(course_results) == 0:
            print("No such course was found.")
            course_results = all_course_results
        elif len(course_results) == 1:
            course = course_results[0]
            print(f"You chose {course.name}.")
            return course

def filter_users_by_query(source: Course | list[User], query: str, enrolled_as = "student") -> list[User]:
    if type(source) == Course:
        return list(source.get_users(search_term = query, enrollment_type = enrolled_as))
    elif type(source) == list:
        sanitized_query = sanitize_string(query)
        return [user for user in source if sanitized_query in sanitize_string(user.name)]
    else:
        raise TypeError("Expected Course object or list")

def process_bad_request(e: BadRequest) -> bool:
    args_string = e.args[0]
    if type(args_string) != str:
        raise e
            
    if "2 or more characters is required" not in args_string:
        raise e
            
    print("Too few characters, try again")
    return True

def prompt_for_student(course: Course) -> User:
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

    source = course
    while True:
        while True:
            try:
                query = input("Search for the student by name: ")
                source = filter_users_by_query(source, query)
                break
            except BadRequest as e:
                process_bad_request(e)

        source_len = len(source)
        if source_len == 0:
            print("\nNo such student was found.")
            source = course
            continue
        elif source_len == 1:
            selected_student = source[0]
            print(f"\nYou chose {selected_student.name}.")
            return selected_student

        print(f"\nYour query returned {source_len} students.")
        print("Here are their names:\n")
        for student in source:
            print(f"    {student.name}")
        print()

def filter_assignments_by_query(source: list[Assignment], query: str, has_due_date = True) -> list[Assignment]:
    sanitized_query = sanitize_string(query)
    return [assignment for assignment in source if sanitized_query in sanitize_string(assignment.name)]

def prompt_for_assignment(course: Course, has_due_date = True) -> Assignment:
    all_assignments = [assignment for assignment in course.get_assignments() if not has_due_date or assignment.due_at]
    source = all_assignments
    
    while True:
        print("Which assignment would you like to access?")
        print("The options are:")
        print()
        for assignment in source:
            print(f"    {assignment.name}")
        print()

        query = input("Choose one of the above options: ")
        source = filter_assignments_by_query(source, query)

        if len(source) == 0:
            print("No such course was found.")
            source = all_assignments
        elif len(source) == 1:
            assignment = source[0]
            print(f"You chose {assignment.name}.")
            return assignment

def set_time_limit_for_quiz(course: Course,
                            student: User, 
                            quiz: Quiz, 
                            time_multiplier: float, 
                            logging = True) -> None:

    if not quiz.time_limit:
        printif(f"{quiz.title} has no time limit.", logging)
        return
    
    extra_time = quiz.time_limit * time_multiplier

    printif(f"Updating {quiz.title} (default time limit is {quiz.time_limit} minutes)...", logging)

    quiz.set_extensions([
        {
            "user_id": student.id,
            "extra_time": extra_time
        }
    ])

    printif(f"{quiz.title} updated! {student.name} now has {extra_time} minutes extra on this quiz.", logging)

def set_time_limits_for_quizzes(course: Course, student: User, time_multiplier: float, logging = True) -> None:
    """
    Updates the time limit extensions for all timed quizzes in the given course 
    for the given student. They are set to `time_multiplier` times the default 
    time limit for the quiz.

    Parameters
    ----------
    `course`: [Course](https://canvasapi.readthedocs.io/en/stable/course-ref.html)
        The course to pull quiz information from.

    `student`: [User](https://canvasapi.readthedocs.io/en/stable/user-ref.html)
        The student to modify time limit extensions for.
    
    `time_multiplier`: float
        The proportion of the time limit that should be added as a time limit 
        extension for each quiz.
    
    `logging`: bool
        Whether or not the function should log to the console for each updated quiz.
    """

    quizzes = [quiz for quiz in course.get_quizzes() if quiz.time_limit]

    for quiz in quizzes:
        set_time_limit_for_quiz(course, student, quiz, time_multiplier, logging)

def get_assignment_or_quiz_due_date(course: Course, assignment: Assignment) -> datetime:
    if assignment.is_quiz_assignment:
        quiz_id = assignment.quiz_id
        quiz = course.get_quiz(quiz_id)
        due_date = parse(quiz.due_at)
    else:
        due_date = parse(assignment.due_at)
    
    return due_date