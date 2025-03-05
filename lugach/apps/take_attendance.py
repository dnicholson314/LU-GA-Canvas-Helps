import requests
import lugach.thutils as thu

def main():
    auth_header = thu.get_auth_header_for_session()

    course = thu.prompt_user_for_th_course(auth_header)
    course_id = course["course_id"]

    attendance_item, _ = thu.create_attendance(auth_header, course_id)

    prompt_to_close = input("Would you like to close attendance? (y/n) ")
    if prompt_to_close != "y":
        return

    attendance_item_id = attendance_item["id"]
    thu.close_attendance(auth_header, course_id, attendance_item_id)
