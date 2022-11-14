# Simple University Registration System

This repository is for the third project of **CMPE 321 Introduction to Database Systems** course.

As the scope of this project, a simple university registration system is built, called SimpleBOUN (Simple Bogazici University), which is concerned with the instructors, students, courses, departments, grades, classrooms etc. Before the implementation, conceptual database design is examined, and drew ER diagrams, converted these ER diagrams into relational tables, and performed schema refinement for SimpleBounDB (Simple Bogazici University Database). Using this structure, designed, a course registration database with a web-based user interface is implemented.

## Table of Contents
1. Project Requirements
2. User Types
3. Database
4. Development
5. How to Run

### Project Requirements
1. Database managers shall be able to log in to the system with their credentials (username and password).
2. Database managers shall be able to add new Users (Students or Instructors) to the system.
3. Database managers shall be able to delete students by providing Student ID. When a student is deleted, all personal data regarding that student must be deleted including previous grades and currently added courses.
4. Database managers shall be able to update titles of the instructors by providing instructor username and title.
5. Database managers shall be able to view all students in ascending order of completed credits. The list must include the following attributes: username, name, surname, email, department, completed credits and GPA.
6. Database managers shall be able to view all instructors. The list must include the following attributes: username, name, surname, email, department, title.
7. Database managers shall be able to view all grades of a specific student by providing Student ID. The list must include the following information: Course ID, course name, grade.
8. Database managers shall be able to view all courses of a specific instructor by providing instructor user- name. The list must include the following attributes: Course ID, course name, classroom ID, campus, time slot.
9. Database managers shall be able to view the grade average of a course by providing Course ID. The list must include the following attributes: Course ID, course name, grade average.
10. Instructors shall be able to log in to the system with their credentials (username and password).
11. Instructors shall be able to list all of the classrooms available for a given slot. The list must include the following attributes: Classroom ID, campus, classroom capacity.
12. Instructors shall be able to add courses by providing Course ID, name, credits, Classroom ID, time slot and quota. The Department ID of the course should be the same as the instructor’s department. A course quota may not be greater than the capacity of the classroom.
13. Instructors shall be able to add a prerequisite to a course by providing its Course ID and the Course ID of the prerequisite.
14. Instructors shall be able to view all courses that they give in ascending order of Course IDs. The list must include the following attributes: Course ID, course name, classroom ID, time slot, quota and prerequisite list. Prerequisite list must be a string in the form “prerequisite1, prerequisite2, ...”
15. Instructors shall be able to view all students who added a specific course given by themselves. To view this information, the instructor should provide a Course ID. The list must include the following attributes: username, Student ID, email, name and surname.
16. Instructors shall be able update the name of a course given by themselves by providing a Course ID and course name.
17. Instructors shall be able to give grades to a student if he/she has added their courses. The instructor should provide Course ID, Student ID and grade for this operation. The grade should be stored. We will not test the case of an instructor updating a previous grade. You can assume the instructors will only enter new grades.
18. Students shall be able to list all the given courses. The list must include the following attributes: Course ID, course name, instructor surname, department, credits, classroom ID, time slot, quota and prerequisite list. Prerequisite list must be a string in the form “prerequisite1, prerequisite2, ...”
19. Students shall be able to add a course by providing a course ID. There are several constraints:
(a) Students cannot take a course twice, that is, if a student has received a grade from the course, she/he cannot add that course.
(b) To take the course, student must have a grade from all of its prerequisites. We will not test the case of an instructor adding a prerequisite for a course after a student has added the course.
(c) Students cannot add a course if the quota is full. At the beginning, added courses of students will be provided. The quota for a course is the maximum number of students who can take that course.
20. Students shall be able to view the courses that they’re currently taking and have taken previously. The list must include the following attributes: Course ID, course name and grade. If the student is taking the course this semester, the grade field will be null.
21. Students shall be able to search a keyword and view the courses that contain this keyword in their names. The list must include the following attributes: Course ID, course name, instructor surname, department, credits, classroom ID, time slot, quota and prerequisite list. Prerequisite list must be a string in the form “prerequisite1, prerequisite2, ...”
22. Students shall be able to filter courses of a specific department with respect to its campus, and an inclusive range between minimum and maximum credits (e.g., courses belonging to Computer Engineering Department, given at the North Campus, with a minimum of 3 and a maximum of 5 credits). This must be implemented as a stored procedure. Parameters of this procedure are department ID, campus, minimum credits, and maximum credits.
23. You must handle the following cases with triggers:
(a) When an instructor grades a student from a course, the completed credits of the student will be incremented by the credits of that course. When an instructor grades a student, the student’s GPA must be updated.
(b) When an instructor adds a course, the quota must not exceed the classroom capacity. If that’s not the case, the system must prevent the operation.

### User Types

There are three types of users: students, instructors, and database managers. Each user can log in to the system from their respective log in interfaces that are chosen from `accounts.html`. Database manager's accounts are predetermined and only database managers can create the other two user types. So, there is no signing up process for this simple system. After logging in each user can perform wide range of actions according to the project requirements specified above.

### Database

For this project a relational database system is chosen to work with, which is MySQL. Both the web interface and the database of the project runs in the local system. So, it is not a public project that can be accessible from the web. So, MySQL needs to be installed in your computer to run the project.

### Development

For the development of the project, Python is chosen to implement the backend of the system, while Django is chosen to implement the frontend. With the SQL queries in the `create_db.py` file, the backend of the system and the database is initialized. Because the scope of this project is only related with the database and the backend of the application, nothing but pure HTML is used for the frontend development.

### How to Run

### Requirements ###
* MySQL
* Python(>3.8) and pip module.

If you have these, then run the following code:
```pip install -r requirements.txt```

Then set up a virtual environment with the following code:
```
# Linux
sudo apt-get install python3-venv    # If needed
python3 -m venv .venv
source .venv/bin/activate

# macOS
python3 -m venv .venv
source .venv/bin/activate

# Windows
py -3 -m venv .venv
.venv\scripts\activate
```

### Deployment ###
First, create an .env file in cmpe321ps folder (folder with the settings.py file), and insert:
```
MYSQL_DATABASE=<YOUR_DB_NAME>
MYSQL_USER=<YOUR_USERNAME>
MYSQL_ROOT_PASSWORD=<YOUR_PASSWORD>
MYSQL_PASSWORD=<YOUR_PASSWORD>
MYSQL_HOST="localhost"
```

On virtual environment, ensure that environment variables are set. To double check, run below commands:
```
export MYSQL_DATABASE=<YOUR_DB_NAME>
export MYSQL_USER=<YOUR_USERNAME>
export MYSQL_ROOT_PASSWORD=<YOUR_PASSWORD>
export MYSQL_PASSWORD=<YOUR_PASSWORD>
export MYSQL_HOST="localhost"
```

After that, to prevent any errors when connecting your MySql database to the project, run below commands:
```
import MySQLdb
mySQLdb
<module 'pymysql' from '/.../site-packages/pymysql/__init__.py'>
```

After that, ensure that your database server is up and run these commands to set up the database to Django configurations:
```
cd cmpe321ps
python manage.py makemigrations
python manage.py migrate
```
This will create some Django related tables on the database (Do not alter them otherwise framework may fail).

Then, you can run this command to create up and fill relevant tables:
``` python cmpe321ps/create_db.py ```

Finally, run the command:
```python manage.py runserver```
and check whether the website is accessible at: [http://127.0.0.1:8000/simpleboun/](http://127.0.0.1:8000/simpleboun/)
