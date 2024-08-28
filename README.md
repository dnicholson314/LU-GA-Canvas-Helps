# LUGACH

LU GA Canvas Helps (or LUGACH for short) is a Python application that provides a
number of utilities designed to make daily tasks more efficient for GAs at Liberty
University.

It synchronizes across Canvas, Top Hat, and Lighthouse to automate tasks such as
confirming student enrollment, retrieving emails, modifying due dates/time limits
on quizzes/assignments, and more.

## Requirements

The project currently requires Python 3.12.0 to be installed, as well as a number
of packages listed in `requirements.txt`.

It's also helpful to have Git installed on your machine so that you can get
updates to the project without having to redownload the whole thing to your
computer every time.

## Installation

First, use git to clone the project to a local folder:

```bash
git clone https://github.com/dnicholson314/LU-GA-Canvas-Helps.git
```

(If you don't have Git, you can just download a ZIP file of the code and extract
it to a folder on your computer.)

Next, you'll have to install the dependencies. I recommend using a virtual
environment to reduce the chances for bugs. Within the working directory, then...

```bash
python -m venv .venv # Create a virtual environment (recommended)
python -m pip install -r requirements.txt
```

Lastly, once all the modules are installed, you can run the project using

```bash
python main.py
```

**The first time you run the project, you should open the Setup application**:

```
    Welcome to LUGACH! Please choose one of the following options (or 'q' to quit): 
        (1) Setup **this option here**
        (2) Identify Absent Students
        (3) Identify Quiz Concerns
        (4) Modify Due Dates
        (5) Modify Time Limits
        (6) Post Final Grades
        (7) Search Student By Name
        (8) Update Attendance Verification
        (9) Modify Attendance
```

That application will let you add the various authentication details you need
for various aspects of the project.
