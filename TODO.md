
To-do List
==========

Phase 2: Generalizing processes
-------------------------------

* ~~Fix setup process for Mac~~
  * ~~Figure out how to do navigation on Mac~~
  * Rename .env file so that it doesn't create an infinite loop on error
* Custom exception classes (see [link](https://stackoverflow.com/questions/9054820/python-requests-exception-handling))
  * Connection timed out
  * Failed to get credentials from .env file
  * TH auth refused
  * LH auth refused
* Top Hat API for python
  * Create analogue for Paginated List except to handle large lists of students
  * Use the process that `canvasapi` uses to create course/student objects
  * Handle error codes from server (what to do when we receive no data)
* Lighthouse API
  * Create student objects
  * ✅ Handle error codes from server
* Create unified student object that combines Canvas/TH/LH

Phase 3: Implementing GUI
-------------------------

* Encrypting sensitive information
  * ~~Encrypt LH API endpoints (to be especially careful since student information is at stake here)~~
* Config application
  * Credentials
    * Get user's Canvas API key
    * Get user's TH jwt refresh token
    * Get user's LH login credentials (and save cookie)
    * Save all of those to a .env file (and encrypt)
  * Classes
    * Unify Canvas/TH/LH student objects
    * Have user manually resolve discrepancies
    * Use SQL database to store these
  * Network (optional)
    * Number of API call attempts
    * Seconds to wait before retrying request
  * Logging for errors
    * Have a console in the app as well as a file that errors are put to
* Application features
  * Implement a routine update process (either on app open or every few hours)
  * Implement Feedback API (upload console log)
    * Every function that runs should print to console so that I can see the trace
* Shell for application
  * Tkinter?
  * Textual?
  * ~~Git website?~~ **Off limits because of Canvas's TOS**
* Write documentation
