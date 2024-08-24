__all__ = [
    "identify_absent_students",
    "identify_quiz_concerns",
    "modify_due_dates",
    "modify_time_limits",
    "post_final_grades",
    "search_student_by_name",
    "update_attendance_verification",
    "modify_attendance"
]

def title_from_app_name(app_name: str) -> str:
    if type(app_name) is not str:
        raise TypeError("Expected a string for the app name.")
    if app_name not in __all__:
        raise ValueError("The app name given was not found in __all__.")

    title = app_name \
        .replace("_", " ") \
        .title()
    return title