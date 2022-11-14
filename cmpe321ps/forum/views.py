from django.shortcuts import render
from django.http import HttpResponse,HttpResponseRedirect
from pymysql import NULL
from .forms import *
from .db_utils import run_statement
import hashlib

def welcome(req):
    return render(req, "accounts.html")

def student_index(req):
    #Logout the user if logged 
    if req.session:
        req.session.flush()
    
    isFailed=req.GET.get("fail",False) #Check the value of the GET parameter "fail"
    
    loginForm=UserLoginForm() #Use Django Form object to create a blank form for the HTML page

    return render(req,'loginStudent.html',{"login_form":loginForm,"action_fail":isFailed})

def student_login(req):
    #Retrieve data from the request body
    username=req.POST["username"]
    temp_password_1=req.POST["password"]
    temp_password_2=hashlib.sha256(temp_password_1.encode())
    password = temp_password_2.hexdigest()

    result=run_statement(f"SELECT * FROM simpleboun_db.Student WHERE username='{username}' and password='{password}';") #Run the query in DB

    if result: #If a result is retrieved
        req.session["username"]=username #Record username into the current session
        return HttpResponseRedirect('../student-home') #Redirect user to home page
    else:
        return HttpResponseRedirect('../login-student?fail=true')

def student_home(req):
    return render(req, "studentHome.html")

def view_all_courses(req):
    result=run_statement(f"SELECT c.c_id, c.c_name, i.surname, i.d_id, c.credit, c.class_id, c.time_slot, c.quota, GROUP_CONCAT(p.before_id) FROM ((Course c LEFT JOIN Prerequisite p ON p.after_id = c.c_id) INNER JOIN Instructor i ON i.username=c.ins_username) GROUP BY c.c_id ORDER BY c.c_id ASC")
    isFailed=req.GET.get("fail",False)
    return render(req,'viewAllCourses.html',{"results":result,"action_fail":isFailed})

def take_course(req):
    isFailed=req.GET.get("fail",False)
    return render(req,'takeCourse.html',{"action_fail":isFailed})

def takeCourse(req):
    username=req.session["username"]
    course_id=req.POST["course_id"]
    temp_sid_1=run_statement(f"SELECT s_id FROM Student WHERE username='{username}'")
    temp_sid_2=temp_sid_1[0]
    sid=temp_sid_2[0]
    score=run_statement(f"SELECT score FROM Received_Grade WHERE c_id='{course_id}' AND s_id='{sid}'")
    if len(score) > 0:
        return HttpResponseRedirect('../simpleboun/take-course?fail=true')
    else:
        rec_list_1=run_statement(f"SELECT c_id FROM Received_Grade WHERE s_id='{sid}'")
        rec_list = []
        for i in range(len(rec_list_1)):
            rec_list.append(rec_list_1[i][0])
        pre_list_1=run_statement(f"SELECT before_id FROM Prerequisite WHERE after_id='{course_id}'")
        pre_list = []
        for i in range(len(pre_list_1)):
            pre_list.append(pre_list_1[i][0])
        prereq_flag = 0
        if(all(x in rec_list for x in pre_list)):
            prereq_flag = 1
        if (prereq_flag):
            temp_stu_1=run_statement(f"SELECT COUNT(s_id) FROM Added WHERE c_id='{course_id}'")
            temp_stu_2=temp_stu_1[0]
            stu=temp_stu_2[0]
            temp_quota_1=run_statement(f"SELECT quota FROM Course WHERE c_id='{course_id}'")
            temp_quota_2=temp_quota_1[0]
            quota=temp_quota_2[0]
            quota = int(quota)
            if stu < quota:
                run_statement(f"CALL TakeCourse('{sid}','{course_id}')")
                return HttpResponseRedirect("../simpleboun/take-course")
            else:
                return HttpResponseRedirect('../simpleboun/take-course?fail=true')
        else:
            return HttpResponseRedirect('../simpleboun/take-course?fail=true')

def view_taken_courses(req):
    username=req.session["username"]
    temp_sid_1=run_statement(f"SELECT s_id FROM Student WHERE username='{username}'")
    temp_sid_2=temp_sid_1[0]
    sid=temp_sid_2[0]
    result=run_statement(f"SELECT a.c_id, c.c_name, rg.score FROM ((Added a LEFT JOIN Received_Grade rg ON a.s_id = rg.s_id AND a.c_id = rg.c_id) LEFT JOIN Course c ON a.c_id=c.c_id) WHERE a.s_id = '{sid}'")
    isFailed=req.GET.get("fail",False)
    return render(req,'viewTakenCourses.html',{"results":result,"action_fail":isFailed})

def search_course(req):
    isFailed=req.GET.get("fail",False)
    return render(req,'searchCourse.html',{"action_fail":isFailed})

def searchCourse(req):
    keyword=req.POST["keyword"]
    result=run_statement(f"SELECT c.c_id, c.c_name, i.surname, ai.d_id, c.credit, c.class_id, c.time_slot, c.quota, GROUP_CONCAT(p.before_id ORDER BY p.before_id) AS Prerequisites FROM (((Course c LEFT JOIN Prerequisite p ON c.c_id=p.after_id) LEFT JOIN Instructor i ON c.ins_username=i.username) LEFT JOIN AssociatedInstructor ai ON c.ins_username=ai.username) WHERE(c.c_name LIKE '%{keyword}%') GROUP BY c.c_id ORDER BY c.c_id ASC;")
    isFailed=req.GET.get("fail",False)
    return render(req, 'searchCourseTable.html',{"results":result,"action_fail":isFailed,"keyword":keyword})

def filter_courses(req):
    isFailed=req.GET.get("fail",False)
    return render(req,'filterCourse.html',{"action_fail":isFailed})

def filterCourses(req):
    d_id=req.POST["d_id"]
    campus=req.POST["campus"]
    min_c=req.POST["min_c"]
    max_c=req.POST["max_c"]
    isFailed=req.GET.get("fail",False)
    try:
        result=run_statement(f"CALL FilterCourses('{d_id}','{campus}','{min_c}','{max_c}')")
        return render(req, 'filterCoursesTable.html',{"results":result,"action_fail":isFailed,"department_id":d_id,"campus":campus,"min_c":min_c,"max_c":max_c})
    except Exception as e:
        print(str(e))
        return HttpResponseRedirect('../simpleboun/filter-courses?fail=true')

def instructor_index(req):
    #Logout the user if logged 
    if req.session:
        req.session.flush()
    
    isFailed=req.GET.get("fail",False) #Check the value of the GET parameter "fail"
    
    loginForm=UserLoginForm() #Use Django Form object to create a blank form for the HTML page

    return render(req,'loginInstructor.html',{"login_form":loginForm,"action_fail":isFailed})

def instructor_login(req):
    #Retrieve data from the request body
    username=req.POST["username"]
    temp_password_1=req.POST["password"]
    temp_password_2=hashlib.sha256(temp_password_1.encode())
    password = temp_password_2.hexdigest()

    result=run_statement(f"SELECT * FROM simpleboun_db.Instructor WHERE username='{username}' and password='{password}';") #Run the query in DB

    if result: #If a result is retrieved
        req.session["username"]=username #Record username into the current session
        return HttpResponseRedirect('../instructor-home') #Redirect user to home page
    else:
        return HttpResponseRedirect('../login-instructor?fail=true')

def instructor_home(req):
    return render(req, "instructorHome.html")

def view_avl_classroom(req):
    isFailed=req.GET.get("fail",False)
    return render(req,'viewAvlClassroom.html',{"action_fail":isFailed})

def viewAvlClassroom(req):
    time_slot=req.POST["i_time_slot"]
    try:
        time_slot = int(time_slot)
        if time_slot <= 10 and time_slot >= 1:
            result=run_statement(f"SELECT c.class_id, c.campus, c.capacity FROM Classroom c WHERE class_id NOT IN (SELECT class_id FROM Course WHERE time_slot ='{time_slot}')")
            isFailed=req.GET.get("fail",False)
            return render(req, 'viewAvlClassroomTable.html',{"results":result,"action_fail":isFailed,"time_slot":time_slot})
        else:
            return render(req,'viewAvlClassroom.html',{"action_fail":True})
    except Exception as e:
        print(str(e))
        return render(req,'viewAvlClassroom.html',{"action_fail":True})

def add_course(req):
    isFailed=req.GET.get("fail",False)
    return render(req,'addCourse.html',{"action_fail":isFailed})

def addCourse(req):
    c_id=req.POST["course_id"]
    c_name=req.POST["course_name"]
    credit=req.POST["credits"]
    ins_username=req.session["username"]
    class_id=req.POST["classroom_id"]
    time_slot=req.POST["timeslot"]
    quota=req.POST["quota"]
    try:
        run_statement(f"CALL AddCourse('{c_id}','{c_name}','{credit}','{ins_username}','{class_id}','{time_slot}','{quota}')")
        return HttpResponseRedirect("../simpleboun/add-course")
    except Exception as e:
        print(str(e))
        return HttpResponseRedirect('../simpleboun/add-course?fail=true')

def add_prereq(req):
    isFailed=req.GET.get("fail",False)
    return render(req,'addPrereq.html',{"action_fail":isFailed})

def addPrereq(req):
    username=req.session["username"]
    c_id_after=req.POST["c_id_after"]
    c_id_before=req.POST["c_id_before"]
    course_check=run_statement(f"SELECT c_id FROM Course WHERE ins_username = '{username}' AND c_id = '{c_id_after}'")
    if len(course_check) > 0:
        try:
            run_statement(f"CALL AddPrereq('{c_id_before}','{c_id_after}')")
            return HttpResponseRedirect("../simpleboun/add-prereq")
        except Exception as e:
            print(str(e))
            return HttpResponseRedirect('../simpleboun/add-prereq?fail=true')
    else:
        return HttpResponseRedirect('../simpleboun/add-prereq?fail=true')

def view_given_courses(req):
    username=req.session["username"]
    result=run_statement(f"SELECT c.c_id, c.c_name, c.class_id, c.time_slot, c.quota, GROUP_CONCAT(p.before_id ORDER BY p.before_id) FROM (Course c LEFT JOIN Prerequisite p ON p.after_id = c.c_id) WHERE c.ins_username = '{username}' GROUP BY c.c_id ORDER BY c.c_id ASC;")
    isFailed=req.GET.get("fail",False)
    return render(req,'viewGivenCourses.html',{"results":result,"action_fail":isFailed})

def view_all_stu(req):
    isFailed=req.GET.get("fail",False)
    return render(req,'viewAllStudents.html',{"action_fail":isFailed})

def viewAllStudents(req):
    c_id=req.POST["course_id"]
    username=req.session["username"]
    course_check=run_statement(f"SELECT c_id FROM Course WHERE ins_username = '{username}' AND c_id = '{c_id}'")
    if len(course_check) > 0:
        result=run_statement(f"SELECT s.username, a.s_id, s.email, s.name, s.surname FROM ((Added a INNER JOIN Course c ON c.c_id=a.c_id) INNER JOIN Student s ON s.s_id=a.s_id) WHERE c.ins_username='{username}' AND c.c_id='{c_id}';")
        isFailed=req.GET.get("fail",False)
        return render(req, 'viewAllStudentsTable.html',{"results":result,"action_fail":isFailed,"course_id":c_id})
    else:
        return render(req,'viewAllStudents.html',{"action_fail":True})

def update_course_name(req):
    isFailed=req.GET.get("fail",False)
    return render(req,'updateCourseName.html',{"action_fail":isFailed})

def updateCourseName(req):
    username=req.session["username"]
    course_id=req.POST["course_id"]
    n_course_name=req.POST["n_course_name"]
    course_check=run_statement(f"SELECT c_id FROM Course WHERE ins_username = '{username}' AND c_id = '{course_id}'")
    if len(course_check) > 0:
        try:
            run_statement(f"CALL UpdateCourseName('{course_id}','{n_course_name}')")
            return HttpResponseRedirect("../simpleboun/update-course-name")
        except Exception as e:
            print(str(e))
            return HttpResponseRedirect('../simpleboun/update-course-name?fail=true')
    else:
        return HttpResponseRedirect('../simpleboun/update-course-name?fail=true') 

def give_grade(req):
    isFailed=req.GET.get("fail",False)
    return render(req,'giveGrade.html',{"action_fail":isFailed})

def giveGrade(req):
    username=req.session["username"]
    course_id=req.POST["course_id"]
    stu_id=req.POST["stu_id"]
    grade=req.POST["grade"]
    try:
        grade = float(grade)
        if grade==0 or grade==0.5 or grade==1 or grade==1.5 or grade==2 or grade==2.5 or grade==3 or grade==3.5 or grade==4:
            course_check=run_statement(f"SELECT c_id FROM Course WHERE ins_username = '{username}' AND c_id = '{course_id}'")
            if len(course_check) > 0:
                student_check=run_statement(f"SELECT s_id FROM Added WHERE c_id='{course_id}' AND s_id='{stu_id}'")
                if len(student_check) > 0:
                    try:
                        run_statement(f"CALL GiveGrade('{course_id}','{stu_id}','{grade}')")
                        return HttpResponseRedirect("../simpleboun/give-grade")
                    except Exception as e:
                        print(str(e))
                        return HttpResponseRedirect('../simpleboun/give-grade?fail=true')
                else:
                    return HttpResponseRedirect('../simpleboun/give-grade?fail=true') 
            else:
                return HttpResponseRedirect('../simpleboun/give-grade?fail=true')
        else:
            return HttpResponseRedirect('../simpleboun/give-grade?fail=true')
    except Exception as e:
        print(str(e))
        return HttpResponseRedirect('../simpleboun/give-grade?fail=true')

def dbmanager_index(req):
    #Logout the user if logged 
    if req.session:
        req.session.flush()
    
    isFailed=req.GET.get("fail",False) #Check the value of the GET parameter "fail"
    
    loginForm=UserLoginForm() #Use Django Form object to create a blank form for the HTML page

    return render(req,'loginDBManager.html',{"login_form":loginForm,"action_fail":isFailed})

def dbmanager_login(req):
    #Retrieve data from the request body
    username=req.POST["username"]
    temp_password_1=req.POST["password"]
    temp_password_2=hashlib.sha256(temp_password_1.encode())
    password = temp_password_2.hexdigest()

    result=run_statement(f"SELECT * FROM simpleboun_db.Database_Manager WHERE username='{username}' and password='{password}';") #Run the query in DB

    if result: #If a result is retrieved
        req.session["username"]=username #Record username into the current session
        return HttpResponseRedirect('../dbmanager-home') #Redirect user to home page
    else:
        return HttpResponseRedirect('../login-dbmanager?fail=true')

def dbmanager_home(req):
    return render(req, "dbmanagerHome.html")

def add_student(req):
    isFailed=req.GET.get("fail",False)
    return render(req,'addStudent.html',{"action_fail":isFailed})

def addStudent(req):
    username=req.POST["s_username"]
    s_id=req.POST["s_student_id"]
    temp_password_1=req.POST["s_password"]
    temp_password_2=hashlib.sha256(temp_password_1.encode())
    password=temp_password_2.hexdigest()
    name=req.POST["s_name"]
    surname=req.POST["s_surname"]
    email=req.POST["s_email"]
    d_id=req.POST["s_department_id"]
    gpa=0
    comp_credit=0
    try:
        run_statement(f"CALL AddStudent('{username}','{s_id}','{password}','{name}','{surname}','{email}','{d_id}','{gpa}','{comp_credit}')")
        return HttpResponseRedirect("../simpleboun/add-student")
    except Exception as e:
        print(str(e))
        return HttpResponseRedirect('../simpleboun/add-student?fail=true')

def add_instructor(req):
    isFailed=req.GET.get("fail",False)
    return render(req,'addInstructor.html',{"action_fail":isFailed})

def addInstructor(req):
    username=req.POST["i_username"]
    temp_password_1=req.POST["i_password"]
    temp_password_2=hashlib.sha256(temp_password_1.encode())
    password=temp_password_2.hexdigest()
    name=req.POST["i_name"]
    surname=req.POST["i_surname"]
    email=req.POST["i_email"]
    d_id=req.POST["i_department_id"]
    title=req.POST["i_title"]
    try:
        run_statement(f"CALL AddInstructor('{username}','{password}','{name}','{surname}','{email}','{d_id}','{title}')")
        return HttpResponseRedirect("../simpleboun/add-instructor")
    except Exception as e:
        print(str(e))
        return HttpResponseRedirect('../simpleboun/add-instructor?fail=true')

def delete_student(req):
    isFailed=req.GET.get("fail",False)
    return render(req,'deleteStudent.html',{"action_fail":isFailed})
    
def deleteStudent(req):
    s_id=req.POST["s_student_id"]
    temp_username=run_statement(f"SELECT username FROM Student WHERE s_id='{s_id}'")
    if len(temp_username) > 0:
        username = temp_username[0][0]
        try:
            run_statement(f"CALL DeleteStudent('{s_id}','{username}')")
            return HttpResponseRedirect("../simpleboun/delete-student")
        except Exception as e:
            print(str(e))
            return HttpResponseRedirect('../simpleboun/delete-student?fail=true')
    else:
        return HttpResponseRedirect('../simpleboun/delete-student?fail=true')

def update_ins_title(req):
    isFailed=req.GET.get("fail",False)
    return render(req,'updateTitle.html',{"action_fail":isFailed})

def updateTitle(req):
    i_username=req.POST["i_username"]
    i_title=req.POST["i_title"]
    temp_instructors=run_statement(f"SELECT username FROM Instructor")
    instructors = []
    for i in range(len(temp_instructors)):
        instructors.append(temp_instructors[i][0])
    if i_username in instructors:
        try:
            run_statement(f"CALL UpdateTitle('{i_username}','{i_title}')")
            return HttpResponseRedirect("../simpleboun/update-ins-title")
        except Exception as e:
            print(str(e))
            return HttpResponseRedirect('../simpleboun/update-ins-title?fail=true')
    else:
        return HttpResponseRedirect('../simpleboun/update-ins-title?fail=true')

def view_students(req):
    result=run_statement(f"SELECT username, name, surname, email, d_id, comp_credit, gpa FROM Student ORDER BY comp_credit ASC;")
    isFailed=req.GET.get("fail",False)
    return render(req,'viewStudents.html',{"results":result,"action_fail":isFailed})

def view_instructors(req):
    result=run_statement(f"SELECT username, name, surname, email, d_id, title FROM Instructor;")
    isFailed=req.GET.get("fail",False)
    return render(req,'viewInstructors.html',{"results":result,"action_fail":isFailed})

def view_stu_grade(req):
    isFailed=req.GET.get("fail",False)
    return render(req,'viewAllGrades.html',{"action_fail":isFailed})

def viewGrades(req):
    s_student_id=req.POST["s_student_id"]
    students=run_statement(f"SELECT s_id FROM Student WHERE s_id = '{s_student_id}'")
    if len(students) > 0:
        result=run_statement(f"SELECT rg.c_id, c.c_name, rg.score FROM Received_Grade rg INNER JOIN Course c ON rg.c_id= c.c_id WHERE rg.s_id = '{s_student_id}'")
        isFailed=req.GET.get("fail",False)
        return render(req, 'viewAllGradesTable.html',{"results":result,"action_fail":isFailed,"student_id":s_student_id})
    else:
        return render(req,'viewAllGrades.html',{"action_fail":True})

def view_inst_course(req):
    isFailed=req.GET.get("fail",False)
    return render(req,'viewInstructorCourse.html',{"action_fail":isFailed})

def viewInstructorCourse(req):
    username=req.POST["i_username"]
    instructors=run_statement(f"SELECT username FROM Instructor WHERE username = '{username}'")
    if len(instructors) > 0:
        result=run_statement(f"SELECT c.c_id, c.c_name, c.class_id, cl.campus, c.time_slot FROM (Course c INNER JOIN Classroom cl ON c.class_id = cl.class_id) WHERE c.ins_username = '{username}'")
        isFailed=req.GET.get("fail",False)
        return render(req, 'viewInstructorCourseTable.html',{"results":result,"action_fail":isFailed,"username":username})
    else:
        return render(req,'viewInstructorCourse.html',{"action_fail":True})

def view_avg_grade(req):
    isFailed=req.GET.get("fail",False)
    return render(req,'viewAvgGrade.html',{"action_fail":isFailed})

def viewAvgGrade(req):
    course_id=req.POST["course_id"]
    courses=run_statement(f"SELECT c_id FROM Course WHERE c_id = '{course_id}'")
    if len(courses) > 0:
        result=run_statement(f"SELECT rg.c_id , c.c_name, AVG(rg.score) FROM Received_Grade rg INNER JOIN Course c ON rg.c_id=c.c_id WHERE rg.c_id = '{course_id}'")
        if len(result) > 0:
            print("TRUE")
        else:
            print("FALSE")
        isFailed=req.GET.get("fail",False)
        return render(req, 'viewAvgGradeTable.html',{"results":result,"action_fail":isFailed,"course_id":course_id})
    else:
        return render(req,'viewAvgGrade.html',{"action_fail":True})
