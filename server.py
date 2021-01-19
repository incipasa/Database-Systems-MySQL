from flask import Flask, render_template,redirect,  request, url_for, session
from flask_mysqldb import MySQL, MySQLdb
import os


app = Flask(__name__)
lists = []
courses = []
departments = []
assignments = []
studentCourses = []
courseList = []
studentsList = []
studentMail = []
instructorCourse = []
registered_course = []
edit_assi = []
register_list = []
studentID = 0
instid = 0
course_id = 0
dep_id = 0
reg_number = ''

app.secret_key = os.urandom(24)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Abcd.1234'
app.config['MYSQL_DB'] = 'db'
app.config['MYSQL_CURSORCLASS'] = "DictCursor"
mysql = MySQL(app)


@app.route('/')

def home():
    return render_template ("home.html")

@app.route('/instructorRegister', methods = ["GET","POST"])

def instructor_register():
    if request.method == 'GET':
        return render_template ("instructorRegister.html")    
    else:

        instructor_mail = request.form['e_mail']
        instructor_pass = request.form['pass_word'].encode('utf-8')
        
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO mailpassword (email, password) VALUES ( %s, %s)", (instructor_mail, instructor_pass))
        mysql.connection.commit()

        session['instructor_email'] = instructor_mail
        session['instructor_password'] = instructor_pass
        
        return redirect(url_for('home'))
   

@app.route('/studentRegister', methods = ["GET","POST"])

def student_register():
    if request.method == 'GET':
        return render_template ("studentRegister.html")    
    
    else:

        student_pass = request.form['stu_password'].encode('utf-8')
        student_mail = request.form['stu_email']
        student_id = request.form['stu_id']
        student_name = request.form['stu_name']  
        
        #for mail in studentMail:
        #   if student_mail == mail:
        #      return render_template ("validationMail.html",row=student_mail)
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute ("SELECT student.studentmail,student.studentname,student.studentid,mailpassword.email FROM student JOIN mailpassword ON student.studentmail=mailpassword.email WHERE student.studentmail = %s ",(student_mail,))
        results = cursor.fetchone()  
        if results is not None:
            return render_template ("validationMail.html",row=student_mail)
          
        
        else:
               
            #    studentMail.append(student_mail)    
            curStu = mysql.connection.cursor()
            curStu.execute("INSERT INTO mailpassword (email, password) VALUES ( %s, %s)", (student_mail, student_pass))
            curStu.execute("INSERT INTO student (studentid, studentname, studentmail) VALUES ( %s, %s, %s)", (student_id, student_name, student_mail))
            mysql.connection.commit()

            session['student_email'] = student_mail
            session['student_password'] = student_pass
            session['studentid'] = student_id
            session['studentname'] = student_name
                
                #session['studentname'] = results['studentname']
                #session['studentid'] = results['studentid']
                #session['studentmail'] = results['studentmail']            
                            
                
            return render_template ("loginPageStudent.html")   

@app.route('/studentCourseRegister', methods = ["GET","POST"])

def student_course_register():
    if request.method == 'GET':
        cursor2 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor2.execute ("SELECT instructor.instructorname, instructorcourse.instructorid, instructorcourse.courseid, instructorcourse.building FROM instructor JOIN instructorcourse ON instructor.instructorid=instructorcourse.instructorid ")
        row = cursor2.fetchone()  
        instructorCourse.clear()        
        
        while row is not None:
            instructorCourse.append(row)
            row = cursor2.fetchone()
        
        return render_template ("studentCourseRegister.html", row=instructorCourse) 

    else:
        
        check_stu_id = request.form['stud_id']
        course_id = request.form['cou_id']
        instructor_id = request.form['inst_id']       
        
        #for course in registered_course:
        #   if course == course_id:
        #      return "Bu kursa kayit oldunuz"   
        
        curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        curl.execute("SELECT * FROM studentcourse WHERE studentid = %s AND courseid = %s",(check_stu_id,course_id) )
        check = curl.fetchone()
        curl.close()           
        
        if check:
              return render_template("checkCourseRegistration.html",row1=check_stu_id,row2=course_id)
        
        curCourse = mysql.connection.cursor()
        curCourse.execute("INSERT INTO studentcourse ( studentid, courseid, instructorid) VALUES ( %s, %s, %s)", (check_stu_id, course_id, instructor_id))
        curCourse.connection.commit()
        
        registered_course.append(course_id)
        
        cur = mysql.connection.cursor()
        cur.execute ("SELECT COUNT(*) FROM studentcourse WHERE instructorid=%s AND courseid=%s",(instructor_id,course_id))
        result = cur.fetchone()
        number_of_rows = result['COUNT(*)'] 
        
        cursor2 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor2.execute ("SELECT  studentcourse.courseid FROM studentcourse JOIN student ON studentcourse.studentid=student.studentid  WHERE student.studentid = %s AND studentcourse.courseid=%s ",(check_stu_id,course_id,) )
        selectCourse = cursor2.fetchone()       
        studentCourses.clear() 
        
        while selectCourse is not None:
            register_list.append(selectCourse)
            selectCourse = cursor2.fetchone()                     
        
        return render_template ("forCountRegister.html",data=number_of_rows,row=register_list)         


@app.route('/logout')

def logout():
    session.clear()
    return render_template ("home.html") 

@app.route('/instructorLogin', methods = ["GET","POST"])

def instructor_login():
    if request.method == 'POST':
        check_mail = request.form['e_mail']
        check_password = request.form['pass_word'].encode('utf-8')
        
        curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        curl.execute("SELECT * FROM mailpassword WHERE email = %s AND password = %s",(check_mail,check_password) )
        check = curl.fetchone()
        curl.close()
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute ("SELECT instructor.mail,instructor.instructorname,instructor.instructorid,mailpassword.email FROM instructor JOIN mailpassword ON instructor.mail=mailpassword.email WHERE instructor.mail = %s ",(check_mail,))
        results = cursor.fetchone() 
        
        if check is None:
            return render_template  ("wrongMailPage.html")
        
        if results is not None:
            session['instructorname'] = results['instructorname']
            session['instructorid'] = results['instructorid']
            session['instructor_email'] = results['email']
        else:
            return render_template ("noInstructorPage.html")
        
        cursor2 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor2.execute ("SELECT instructor.mail,instructor.instructorid,instructor.instructorname,instructorcourse.courseid,instructorcourse.building FROM instructor JOIN instructorcourse ON instructor.instructorid=instructorcourse.instructorid WHERE instructor.mail = %s ",(check_mail,))
        row = cursor2.fetchone()  
        lists.clear()
        
        cursor3 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor3.execute ("SELECT course.courseid,course.coursename,course.departmentid,course.lessonhour,course.assignmentnumber FROM course JOIN instructorcourse ON course.courseid=instructorcourse.courseid JOIN instructor ON instructorcourse.instructorid=instructor.instructorid WHERE instructor.mail = %s ",(check_mail,) )
        selectCourse = cursor3.fetchone()
        courses.clear()
        
        cursor4 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor4.execute ("SELECT department.departmentid,department.departmentname FROM department JOIN course ON department.departmentid=course.departmentid JOIN instructorcourse ON instructorcourse.courseid=course.courseid JOIN instructor ON instructorcourse.instructorid=instructor.instructorid WHERE instructor.mail = %s ",(check_mail,) )
        selectDepartment = cursor4.fetchone()  
        departments.clear()
        
        #if selectDepartment is not None:
        #    session['departmentid'] = selectDepartment['departmentid']
        #    session['departmentname'] = selectDepartment['departmentname']        
        #    departments.clear()

        cursor5 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor5.execute ("SELECT assignment.courseid, assignment.assignmentid, assignment.time, assignment.assignmnettype, assignment.average FROM assignment JOIN course ON assignment.courseid=course.courseid JOIN instructorcourse ON instructorcourse.courseid=course.courseid JOIN instructor ON instructorcourse.instructorid=instructor.instructorid WHERE instructor.mail = %s ",(check_mail,) )
        selectAssignment = cursor5.fetchone()       
        assignments.clear() 
        
        cursor6 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor6.execute ("SELECT instructorcourse.instructorid, studentcourse.attendencehours, studentcourse.studentid, student.studentname,studentcourse.courseid, course.coursename, studentcourse.coursegrade FROM student JOIN studentcourse ON student.studentid=studentcourse.studentid JOIN course ON studentcourse.courseid=course.courseid JOIN instructorcourse ON instructorcourse.courseid=studentcourse.courseid JOIN instructor ON instructor.instructorid=instructorcourse.instructorid WHERE instructor.mail = %s ",(check_mail,) )
        getStudents = cursor6.fetchone()       
        studentsList.clear()                       
        
        while row is not None:
            lists.append(row)
            row = cursor2.fetchone()

        while selectCourse is not None:
            courses.append(selectCourse)
            selectCourse = cursor3.fetchone()  

        while selectAssignment is not None:
            assignments.append(selectAssignment)
            selectAssignment = cursor5.fetchone()      

        while getStudents is not None:
            studentsList.append(getStudents)
            getStudents = cursor6.fetchone()   

        while selectDepartment is not None:
            departments.append(selectDepartment)
            selectDepartment = cursor4.fetchone()                     
                                       
        
        if check:
            session['instructor_email'] = check['email']
            session['instructor_password'] = check['password']
            
            return render_template("loginPageInstructors.html")


               
    else:    
        return render_template ("instructorLogin.html") 
 
@app.route('/editAssignment', methods = ["GET","POST"])

def assignment_edit():
    if request.method == 'GET':
        return render_template ("editAssignment.html",row=assignments) 
    
    else:    
        instru_id = request.form['ins_id']
        assignment_id = request.form['assi_id']
        assignment_time = request.form['assi_time']
        assignment_type = request.form['assi_type']
        assignment_average = request.form['assi_average']         
        
        mycursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        mycursor.execute ("UPDATE assignment SET assignmentid = %s, time=%s, assignmnettype=%s, average=%s WHERE assignmentid = %s", (assignment_id,assignment_time, assignment_type, assignment_average, assignment_id ) )
        mysql.connection.commit()      
        
        #cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        #cursor.execute ("SELECT assignment.courseid,assignment.assignmentid,assignment.time,assignment.assignmnettype, assignment.average FROM assignment WHERE assignment.courseid=%s",(checkStudent_mail,))
        #results = cursor.fetchone()        
        
        #while results is not None:
        #    edit_assi.append(results)
        #    results = cursor.fetchone()            

        cursor6 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor6.execute ("SELECT assignment.courseid,assignment.assignmentid,assignment.time,assignment.assignmnettype, assignment.average FROM assignment JOIN instructorcourse ON assignment.courseid=instructorcourse.courseid JOIN instructor ON instructorcourse.instructorid=instructor.instructorid WHERE instructor.instructorid = %s ",(instru_id,) )
        assi = cursor6.fetchone()       
        assignments.clear()   

        while assi is not None:
            assignments.append(assi)
            assi = cursor6.fetchone()          
        
        return render_template ("assignments.html")

@app.route('/editCourse', methods = ["GET","POST"])

def edit_course():
    if request.method == 'GET':
        return render_template ("edit_course.html") 

    else:    
        #instructorid = request.form['ins_id']
        course_id = request.form['cour_id']
        new_course_id = request.form['new_cour_id']
        course_name = request.form['cour_name']
        department_id = request.form['dep_id']
        lesson_hour = request.form['les_hour']
        assignment_number = request.form['assi_num']     
        
        mycursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        mycursor.execute ("UPDATE course SET coursename = %s, courseid = %s, departmentid = %s, lessonhour = %s, assignmentnumber = %s WHERE courseid = %s", (course_name, new_course_id, department_id, lesson_hour, assignment_number, course_id ) )
        mysql.connection.commit()
        
        return render_template ("home.html")   
    
           
@app.route('/deleteCourse', methods = ["GET","POST"])

def delete_course():
    if request.method == 'GET':
        return render_template ("delete_course.html") 
    
    else:
        
        delete_course = request.form['delete_cour']
        
        mycursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        mycursor.execute ("DELETE FROM course WHERE courseid = %s", (delete_course, ) )
        mysql.connection.commit()             
        
        return render_template ("home.html")

@app.route('/addCourse', methods = ["GET","POST"])

def add_course():
    if request.method == 'GET':
        return render_template ("add_course.html") 
    
    else:    
        instructorid = request.form['ins_id']
        course_id = request.form['cour_id']
        course_name = request.form['cour_name']
        department_id = request.form['dep_id']
        lesson_hour = request.form['les_hour']
        assignment_number = request.form['assi_num']   
        building = "med"
        
        curCourse = mysql.connection.cursor()
        curCourse.execute("INSERT INTO course ( coursename, courseid, departmentid, lessonhour, assignmentnumber) VALUES ( %s, %s, %s, %s, %s)", (course_name, course_id, department_id,lesson_hour, assignment_number ))
        curCourse.execute("INSERT INTO instructorcourse (  courseid, instructorid, building) VALUES ( %s, %s, %s)", (course_id, instructorid, building ))
        
        curCourse.connection.commit()          
        
        return render_template ("home.html")
    

@app.route('/deleteAssignment', methods = ["GET","POST"])

def assignment_delete():
    if request.method == 'GET':
        return render_template ("deleteAssignment.html",row=assignments) 
    
    else:    
        delete_assignment_id = request.form['delete_assi']
        instru_id = request.form['ins_id']
        
        mycursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        mycursor.execute ("DELETE FROM assignment WHERE assignmentid = %s", (delete_assignment_id, ) )
        mysql.connection.commit()              
        
        cursor6 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor6.execute ("SELECT assignment.courseid,assignment.assignmentid,assignment.time,assignment.assignmnettype, assignment.average FROM assignment JOIN instructorcourse ON assignment.courseid=instructorcourse.courseid JOIN instructor ON instructorcourse.instructorid=instructor.instructorid WHERE instructor.instructorid = %s ",(instru_id,) )
        assi = cursor6.fetchone()       
        assignments.clear()   

        while assi is not None:
            assignments.append(assi)
            assi = cursor6.fetchone()        
        
        return render_template ("assignments.html",row=assignments)    
    
@app.route('/addAssignment', methods = ["GET","POST"])

def assignment_add():
    if request.method == 'GET':
        return render_template ("addAssignment.html",row=assignments)      
    
    else:
        course_id = request.form['co_id']
        assignment_id = request.form['assi_id']
        assignment_time = request.form['assi_time']
        assignment_type = request.form['assi_type']
        assignment_average = request.form['assi_average']   
        
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO assignment (courseid, assignmentid, time, assignmnettype, average) VALUES ( %s, %s, %s, %s, %s)", (course_id, assignment_id, assignment_time, assignment_type, assignment_average  ))
        mysql.connection.commit()        
        
        return render_template ("home.html")
        
                      

@app.route('/editStudents', methods = ["GET","POST"])

def student_edit():
    if request.method == 'GET':
        return render_template ("editStudents.html",row=studentsList) 
    
    else:    
        instructor_id = request.form['inst_id'] 
        inst_course_id = request.form['c_id']
        inst_student_id = request.form['s_id']
        student_attendence = request.form['stu_attendence']
        student_grade = request.form['stu_grade']
        student_average = request.form['assi_average'] 
        
        mycursor2 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        mycursor2.execute ("UPDATE studentcourse SET coursegrade = %s, attendencehours=%s, assignmentaverage=%s WHERE courseid = %s AND studentid=%s", (student_grade, student_attendence, student_average, inst_course_id, inst_student_id ) )
        mysql.connection.commit()     
        
        cursor6 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor6.execute ("SELECT studentcourse.assignmentaverage,instructorcourse.instructorid, studentcourse.attendencehours, studentcourse.studentid, student.studentname,studentcourse.courseid, course.coursename, studentcourse.coursegrade FROM student JOIN studentcourse ON student.studentid=studentcourse.studentid JOIN course ON studentcourse.courseid=course.courseid JOIN instructorcourse ON instructorcourse.courseid=studentcourse.courseid JOIN instructor ON instructor.instructorid=instructorcourse.instructorid WHERE instructor.instructorid = %s ",(instructor_id,) )
        getStudents = cursor6.fetchone()       
        studentsList.clear()   

        while getStudents is not None:
            studentsList.append(getStudents)
            getStudents = cursor6.fetchone()                  
        
        return render_template ("studentlist.html",row=studentsList) 

@app.route('/deleteStudents', methods = ["GET","POST"])

def student_delete_from_course():
    if request.method == 'GET':
        return render_template ("deleteStudents.html")    
    
    else:
        course_id = request.form['delete_cour'] 
        student_id = request.form['delete_stu']   
            
        mycursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        mycursor.execute ("DELETE FROM studentcourse WHERE courseid = %s AND studentid= %s", (course_id, student_id,) )
        mysql.connection.commit()    
        
        return render_template ("home.html")     

@app.route('/addStudents', methods = ["GET","POST"])

def student_add():
    if request.method == 'GET':
        return render_template ("add_student.html") 
    
    else:
        student_id = request.form['s_id'] 
        course_id = request.form['c_id']
        inst_id = request.form['inst_id']
        student_grade = request.form['stu_grade']
        student_attendence = request.form['stu_attendence']
        student_average = request.form['assi_average']   
        
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO studentcourse (studentid, courseid, instructorid, coursegrade, attendencehours, assignmentaverage) VALUES ( %s, %s, %s, %s, %s, %s)", (student_id, course_id, inst_id, student_grade, student_attendence, student_average ))
        mysql.connection.commit() 
        
        return render_template ("home.html")           
        
                  
         
@app.route('/courseInstructor')    
def course_instructor_page():           
    return render_template("courseViaInstructor.html",row=lists) 

@app.route('/courses')    
def course_page():           
    return render_template("courses.html",row=courses) 

@app.route('/departments')    
def departments_page():           
    return render_template("departments.html",row=departments) 

@app.route('/assignments')    
def assignments_page():   
    #value = 92         
        
    #cursor7 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    #result = cursor7.execute ("SELECT MAX (average) FROM assignment" )
    #result = cursor7.fetchall()
    #number_of_rows = result             
    return render_template("assignments.html",row=assignments) 

@app.route('/studentlist')    
def students_list_page():           
    return render_template("studentlist.html",row=studentsList) 

@app.route('/studentLogin', methods = ["GET","POST"])

def student_login():
    if request.method == 'POST':
        checkStudent_mail = request.form['stu_email']
        checkInstructor_password = request.form['stu_password'].encode('utf-8')
        
        curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        curl.execute("SELECT * FROM mailpassword WHERE email = %s AND password = %s",(checkStudent_mail,checkInstructor_password) )
        check = curl.fetchone()
        curl.close()
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute ("SELECT student.studentmail,student.studentname,student.studentid,mailpassword.email FROM student JOIN mailpassword ON student.studentmail=mailpassword.email WHERE student.studentmail = %s ",(checkStudent_mail,))
        results = cursor.fetchone() 
        
        cursor2 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor2.execute ("SELECT studentcourse.courseid, studentcourse.studentid, studentcourse.coursegrade, studentcourse.attendencehours,studentcourse.assignmentaverage FROM studentcourse JOIN student ON studentcourse.studentid=student.studentid  WHERE student.studentmail = %s ",(checkStudent_mail,) )
        selectCourse = cursor2.fetchone()       
        studentCourses.clear()      

        cursor3 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor3.execute ("SELECT course.courseid,course.coursename,course.departmentid,course.lessonhour,course.assignmentnumber FROM course JOIN studentcourse ON course.courseid=studentcourse.courseid JOIN student ON studentcourse.studentid=student.studentid WHERE student.studentmail = %s ",(checkStudent_mail,) )
        courseTuple = cursor3.fetchone()
        courseList.clear()          
        
        if check is None:
            return render_template ("wrongMailPage.html")
        
        if results is not None:
            session['studentname'] = results['studentname']
            session['studentid'] = results['studentid']
            session['studentmail'] = results['studentmail']
        else:
            return render_template ("noStudentPage.html")   
        
        while selectCourse is not None:
            studentCourses.append(selectCourse)
            selectCourse = cursor2.fetchone() 

        while courseTuple is not None:
            courseList.append(courseTuple)
            courseTuple = cursor3.fetchone()                        
        
        if check:
            session['student_email'] = check['email']
            session['student_password'] = check['password']
            
            return render_template("loginPageStudent.html")
               
    else:    
        return render_template ("studentLogin.html")
    
@app.route('/courseStudent')    
def course_student_page():           
    return render_template("courseStudent.html",row=studentCourses) 

@app.route('/courseProperty')    
def course_property_page():           
    return render_template("courseProperty.html",row=courseList) 
    
if __name__ == '__main__':
    app.run(debug=True)
    

    
