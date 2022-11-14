import mysql.connector
import environ

env = environ.Env()
environ.Env.read_env()

connection = mysql.connector.connect(
  host=env("MYSQL_HOST"),
  user=env("MYSQL_USER"),
  password=env("MYSQL_PASSWORD"),
  database=env("MYSQL_DATABASE"),
  auth_plugin='mysql_native_password'
)

cursor= connection.cursor()
#Create tables
cursor.execute("""
CREATE TABLE IF NOT EXISTS Department (
d_id CHAR(255) NOT NULL,    #department id
d_name CHAR(255) NOT NULL,  #department name
PRIMARY KEY (d_id),
UNIQUE (d_name)
);""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS Student (
username CHAR(255) NOT NULL,  #username
s_id INTEGER NOT NULL,    #student id
password CHAR(255) NOT NULL,  #password
name CHAR(255) NOT NULL,    #name of the student
surname CHAR(255) NOT NULL, #surname of the student
email CHAR(255) NOT NULL, #email
d_id CHAR(255) NOT NULL,    #department id
gpa REAL,  #gpa of the student
comp_credit INTEGER, #total credits earned from completed courses
PRIMARY KEY (username),
FOREIGN KEY (d_id) REFERENCES Department(d_id),
UNIQUE (s_id)
);""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS Instructor (
username CHAR(255) NOT NULL,  #username
password CHAR(255) NOT NULL,  #password
name CHAR(255) NOT NULL,    #name
surname CHAR(255) NOT NULL, #surname
email CHAR(255) NOT NULL, #email
d_id CHAR(255) NOT NULL,    #department id
title CHAR(255) CHECK(STRCMP(title, 'Assistant Professor') = 0 OR STRCMP(title, 'Associate Professor') = 0 OR STRCMP(title, 'Professor') = 0) NOT NULL,  #title
PRIMARY KEY (username),
FOREIGN KEY (d_id) REFERENCES Department(d_id)
);""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS AssociatedStudent (
username CHAR(255) NOT NULL,      #username
d_id CHAR(255) NOT NULL,  #department id and all users need to be associated with a department
PRIMARY KEY(username),
FOREIGN KEY(username) REFERENCES Student(username),
FOREIGN KEY(d_id) REFERENCES Department(d_id)
);""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS AssociatedInstructor (
username CHAR(255) NOT NULL,      #username
d_id CHAR(255) NOT NULL,  #department id and all users need to be associated with a department
PRIMARY KEY(username),
FOREIGN KEY(username) REFERENCES Instructor(username),
FOREIGN KEY(d_id) REFERENCES Department(d_id)
);""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS Classroom (
class_id CHAR(255) NOT NULL,  #classroom id
capacity INTEGER NOT NULL,  #capacity of the classroom
campus CHAR(255) NOT NULL,  #campus of the classroom
PRIMARY KEY (class_id)
);""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS Course (
c_id CHAR(255) NOT NULL,      #course id
c_name CHAR(255) NOT NULL,    #course name
credit INTEGER NOT NULL,      #credit of the course
ins_username CHAR(255) NOT NULL,  #username of the instructor
class_id CHAR(255) NOT NULL,
time_slot INTEGER CHECK(1 <= time_slot AND time_slot <= 10) NOT NULL,
quota INTEGER NOT NULL,     #quota of the course
PRIMARY KEY(c_id),
FOREIGN KEY(ins_username) REFERENCES Instructor(username),
FOREIGN KEY(class_id) REFERENCES Classroom(class_id),
UNIQUE(c_name),
UNIQUE(class_id, time_slot)
);""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS Received_Grade (
c_id CHAR(255) NOT NULL,        #course id
s_id INTEGER NOT NULL,    #student id and score can only exists with a s_id and c_id pair
score REAL NOT NULL,          #grade received from the course
PRIMARY KEY (s_id, c_id),
FOREIGN KEY (s_id) REFERENCES Student(s_id),
FOREIGN KEY (c_id) REFERENCES Course(c_id) ON UPDATE CASCADE ON DELETE CASCADE  #weak entity specification
);""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS Added (
s_id INTEGER NOT NULL,  #student id
c_id CHAR(255) NOT NULL,  #course id
PRIMARY KEY (s_id, c_id),
FOREIGN KEY (s_id) REFERENCES Student(s_id),
FOREIGN KEY (c_id) REFERENCES Course(c_id)
);""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS Prerequisite (
before_id CHAR(255) NOT NULL, #course id of the course, which is a prerequisite, named after
after_id CHAR(255) NOT NULL,  #course id of the course, which has a prerequisite, named before
PRIMARY KEY (before_id, after_id),
CONSTRAINT FKbefore_id CHECK(STRCMP(before_id, after_id) = -1), #checks if the id of the before is less than the id of after
FOREIGN KEY (before_id) REFERENCES Course(c_id),
FOREIGN KEY (after_id) REFERENCES Course(c_id)
);""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS Teaches (
username CHAR(255) NOT NULL,  #username of the teacher and each course must be teached by a teacher
c_id CHAR(255) NOT NULL,          #course id
PRIMARY KEY (c_id),
FOREIGN KEY (username) REFERENCES Instructor(username),
FOREIGN KEY (c_id) REFERENCES Course(c_id) ON DELETE NO ACTION
);""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS Database_Manager (
username CHAR(255) NOT NULL, #username
password CHAR(255) NOT NULL, #password
PRIMARY KEY (username)
);""")

cursor.execute("""
DROP PROCEDURE IF EXISTS AddStudent
""")
cursor.execute("""
CREATE PROCEDURE AddStudent(IN username VARCHAR(256), IN s_id INTEGER, IN password VARCHAR(256), IN name VARCHAR(256), IN surname VARCHAR(256), IN email VARCHAR(256), IN d_id VARCHAR(256), IN gpa REAL, IN comp_credit INTEGER)
BEGIN
INSERT INTO Student VALUES (username, s_id, password, name, surname, email, d_id, gpa, comp_credit);
INSERT INTO AssociatedStudent VALUES (username, d_id);
END;
""")

cursor.execute("""
DROP PROCEDURE IF EXISTS AddInstructor
""")
cursor.execute("""
CREATE PROCEDURE AddInstructor(IN username VARCHAR(256), IN password VARCHAR(256), IN name VARCHAR(256), IN surname VARCHAR(256), IN email VARCHAR(256), IN d_id VARCHAR(256), IN title VARCHAR(256))
BEGIN
INSERT INTO Instructor VALUES (username, password, name, surname, email, d_id, title);
INSERT INTO AssociatedInstructor VALUES (username, d_id);
END;
""")

cursor.execute("""
DROP PROCEDURE IF EXISTS DeleteStudent
""")
cursor.execute("""
CREATE PROCEDURE DeleteStudent(IN param_s_id INTEGER, IN param_username VARCHAR(256))
BEGIN
DELETE FROM AssociatedStudent WHERE username = param_username;
DELETE FROM Added WHERE s_id = param_s_id;
DELETE FROM Received_Grade WHERE s_id = param_s_id;
DELETE FROM Student WHERE s_id = param_s_id;
END
""")

cursor.execute("""
DROP PROCEDURE IF EXISTS UpdateTitle
""")
cursor.execute("""
CREATE PROCEDURE UpdateTitle(IN param_username VARCHAR(256), IN param_title VARCHAR(256))
BEGIN
UPDATE Instructor SET title = param_title WHERE username = param_username;
END;
""")

cursor.execute("""
DROP PROCEDURE IF EXISTS AddCourse
""")
cursor.execute("""
CREATE PROCEDURE AddCourse(IN c_id VARCHAR(256), IN c_name VARCHAR(256), IN credit INTEGER, IN ins_username VARCHAR(256), IN class_id VARCHAR(256), IN time_slot INTEGER, IN quota INTEGER)
BEGIN
INSERT INTO Course VALUES (c_id, c_name, credit, ins_username, class_id, time_slot, quota);
END;
""")

cursor.execute("""
DROP PROCEDURE IF EXISTS AddPrereq
""")
cursor.execute("""
CREATE PROCEDURE AddPrereq(IN before_id VARCHAR(256), IN after_id VARCHAR(256))
BEGIN
INSERT INTO Prerequisite VALUES (before_id, after_id);
END;
""")

cursor.execute("""
DROP PROCEDURE IF EXISTS UpdateCourseName
""")
cursor.execute("""
CREATE PROCEDURE UpdateCourseName(IN param_id VARCHAR(256), IN param_name VARCHAR(256))
BEGIN
UPDATE Course SET c_name = param_name WHERE c_id = param_id;
END;
""")

cursor.execute("""
DROP PROCEDURE IF EXISTS GiveGrade
""")
cursor.execute("""
CREATE PROCEDURE GiveGrade(IN c_id VARCHAR(256), IN s_id INTEGER, IN score REAL)
BEGIN
INSERT INTO Received_Grade VALUES (c_id, s_id, score);
END;
""")

cursor.execute("""
DROP PROCEDURE IF EXISTS TakeCourse
""")
cursor.execute("""
CREATE PROCEDURE TakeCourse(IN s_id INTEGER, IN c_id VARCHAR(256))
BEGIN
INSERT INTO Added VALUES(s_id, c_id);
END;
""")

cursor.execute("""
DROP PROCEDURE IF EXISTS FilterCourses
""")
cursor.execute("""
CREATE PROCEDURE FilterCourses(IN param_d_id VARCHAR(256), IN param_campus VARCHAR(256), IN param_min_c INTEGER, IN param_max_c INTEGER)
BEGIN
SELECT c.c_id, c.c_name, i.surname, i.d_id, c.credit, c.class_id, c.time_slot, c.quota, GROUP_CONCAT(p.before_id) AS Prerequisites
FROM (((Course c
INNER JOIN Classroom cl ON c.class_id=cl.class_id)
INNER JOIN Instructor i ON c.ins_username=i.username)
LEFT JOIN Prerequisite p ON c.c_id=p.after_id)
WHERE cl.campus = param_campus AND c.credit >= param_min_c AND c.credit <= param_max_c AND i.d_id=param_d_id
GROUP BY c.c_id ORDER BY c.c_id ASC;
END;
""")

cursor.execute("""
DROP TRIGGER IF EXISTS CourseInsert
""")
cursor.execute("""
CREATE TRIGGER CourseInsert
BEFORE INSERT ON Course
FOR EACH ROW
BEGIN
    IF (SELECT capacity FROM Classroom WHERE class_id = new.class_id) < new.quota THEN
    SIGNAL SQLSTATE '45000';
    END IF;
END;
""")

cursor.execute("""
DROP TRIGGER IF EXISTS UpdateStudentCredit
""")
cursor.execute("""
CREATE TRIGGER UpdateStudentCredit
BEFORE INSERT ON Received_Grade
FOR EACH ROW
BEGIN
    DECLARE add_credit INTEGER;
    SET @add_credit := (SELECT credit FROM Course WHERE c_id = new.c_id);
    UPDATE Student SET comp_credit = comp_credit + @add_credit WHERE s_id = new.s_id;
END;
""")

cursor.execute("""
DROP TRIGGER IF EXISTS UpdateStudentGpa
""")
cursor.execute("""
CREATE TRIGGER UpdateStudentGpa
AFTER INSERT ON Received_Grade
FOR EACH ROW
BEGIN
    DECLARE grade_sum REAL;
    DECLARE tot_cred INTEGER;
    SET @grade_sum := (SELECT SUM(rg.score * c.credit) FROM (Received_Grade rg INNER JOIN Course c ON rg.c_id = c.c_id) WHERE s_id = new.s_id);
    SET @tot_cred := (SELECT comp_credit FROM Student WHERE s_id = new.s_id);
    UPDATE Student SET gpa = (@grade_sum) / (@tot_cred) WHERE s_id = new.s_id;
END;
""")

connection.commit()

