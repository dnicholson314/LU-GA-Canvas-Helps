__all__ = [
    "setup",
    "identify_absent_students",
    "identify_quiz_concerns",
    "modify_due_dates",
    "modify_time_limits",
    "post_final_grades",
    "search_student_by_name",
    "update_attendance_verification",
    "modify_attendance",
]

import importlib

def lint_app_name(app_name: str) -> bool:
    if type(app_name) is not str:
        raise TypeError(f"Expected a string for the app name: {app_name}.")
    if app_name not in __all__:
        raise ValueError(f"The app name given ({app_name}) was not found in __all__.")

    return True

def title_from_app_name(app_name: str) -> str:
    lint_app_name(app_name)

    title = app_name \
        .replace("_", " ") \
        .title()
    return title

def run_app_from_app_name(app_name: str):
    lint_app_name(app_name)

    app = importlib.import_module(f"lugach.apps.{app_name}")
    app.main()