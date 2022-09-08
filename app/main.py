
from fastapi import FastAPI, Depends, status, HTTPException, UploadFile, File, Form

from app.schema import ( ClassNoticeForm, UserForm, StudentForm, TeacherForm, 
                        AddStudentToClass, StudentAddedByTeacherResponse,
                        AssignmentForm, StudentMarks, UpdateStudentMarks, 
                        StudentMarksResponse, MessageToTeacher, Message, ClassNoticeForm , 
                        ClassNoticeResponse, SubmitAssignmentForm)

from . import models
from typing import List

from .database import engine, get_db
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import UnmappedInstanceError

models.Base.metadata.create_all(bind=engine)


app = FastAPI(title="Class Manager App Backend")


@app.post("/users")
def users(add_user_form: UserForm, db: Session = Depends(get_db)):
    try:
        query = models.Users(**add_user_form.__dict__)
        db.add(query)
        db.commit()
        db.refresh(query)
        

    except IntegrityError as e:
        db.rollback()
        if "UNIQUE constraint failed: users.email" in str(e):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="email address already exisy in database") from e

        elif " UNIQUE constraint failed: users.username" in str(e):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="username address already exisy in database") from e

        else:
            raise e
    
    return query


@app.delete("/users/{id}")
def users(id: int, db: Session = Depends(get_db)):
    try:
        query = db.query(models.Users).filter(models.Users.id == id).first()
        db.delete(query)    
        db.commit()

    except UnmappedInstanceError as e:
        db.rollback()
        if "is not mapped" in str(e):    
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
        detail="user with id of {id} not found") from e

    return status.HTTP_204_NO_CONTENT    



@app.put("/users/{id}")
def users(user_form: UserForm, id: int, db: Session = Depends(get_db)):

    query = db.query(models.Users).filter(models.Users.id == id)
    if not query.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
        detail="user with id of {id} not found")
        
    query.update(user_form.__dict__, synchronize_session=False)   
    db.commit()
    return query.first()   


#######################################################################################################

@app.get("/student")
def student(db: Session = Depends(get_db)):
    return db.query(models.Student).all()


@app.post("/student")
def student(add_student_form: StudentForm, db: Session = Depends(get_db)):
    try:
        if check_user_query := db.query(models.Users).filter(models.Users.id == add_student_form.user_id).first():
            if check_user_query.is_student != True:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Not registered as student")

        query = models.Student(**add_student_form.__dict__)
        db.add(query)
        db.commit()
        db.refresh(query)
        

    except IntegrityError as e:
        db.rollback()
        if "UNIQUE constraint failed: users.email" in str(e):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="email address already exisy in database") from e

        elif " UNIQUE constraint failed: users.username" in str(e):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="username address already exisy in database") from e

        else:
            raise e
    
    return query



@app.delete("/student/{id}")
def student(id: int, db: Session = Depends(get_db)):
    try:
        query = db.query(models.Student).filter(models.Student.id == id).first()
        db.delete(query)    
        db.commit()

    except UnmappedInstanceError as e:
        db.rollback()
        if "is not mapped" in str(e):    
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
        detail="student with id of {id} not found") from e

    return status.HTTP_204_NO_CONTENT    



@app.put("/student/{id}")
def student(user_form: UserForm, id: int, db: Session = Depends(get_db)):

    query = db.query(models.Student).filter(models.Student.id == id)
    if not query.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
        detail="student with id of {id} not found")
        
    query.update(user_form.__dict__, synchronize_session=False)   
    db.commit()
    return query.first()   


#######################################################################################################

@app.get("/teacher/all")
def teacher(db: Session = Depends(get_db)):
    return db.query(models.Teacher).all()


@app.post("/teacher/add")
def teacher(add_teacher_form: TeacherForm, db: Session = Depends(get_db)):
    try:
        if check_user_query := db.query(models.Users).filter(models.Teacher.id == add_teacher_form.user_id).first():
            if check_user_query.is_teacher != True:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Not registered as teacher")
        query = models.Teacher(**add_teacher_form.__dict__)
        db.add(query)
        db.commit()
        db.refresh(query)
        return query    

    except IntegrityError as e:
        db.rollback()
        if "UNIQUE constraint failed: users.email" in str(e):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="email address already exisy in database") from e

        elif " UNIQUE constraint failed: users.username" in str(e):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="username address already exisy in database") from e
        else:
            raise e


@app.delete("/teacher/{id}")
def student(id: int, db: Session = Depends(get_db)):
    try:
        query = db.query(models.Teacher).filter(models.Teacher.id == id).first()
        db.delete(query)    
        db.commit()

    except UnmappedInstanceError as e:
        db.rollback()
        if "is not mapped" in str(e):    
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
        detail="teacher with id of {id} not found") from e

    return status.HTTP_204_NO_CONTENT    



@app.put("/teacher/{id}")
def teacher(user_form: UserForm, id: int, db: Session = Depends(get_db)):

    query = db.query(models.Teacher).filter(models.Teacher.id == id)
    if not query.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
        detail="teacher with id of {id} not found")
        
    query.update(user_form.__dict__, synchronize_session=False)   
    db.commit()
    return query.first()   

#######################################################################################################

@app.post("/add_student")
def add_student_to_class(add_student_form: AddStudentToClass, db: Session = Depends(get_db)):
    find_student = db.query(models.Student).filter(models.Student.id == add_student_form.student).first()
    find_teacher = db.query(models.Teacher).filter(models.Teacher.id == add_student_form.teacher).first()

    if not find_student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
        detail="student with id of {id} not found")
    
    if not find_teacher:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
        detail="teacher with id of {id} not found")
    
    query = models.StudentsInClass(**add_student_form.__dict__)

    db.add(query)
    db.commit()
    db.refresh(query)
    return "Successfully Added"



@app.get("/teacher/{id}/all_student", response_model=List[StudentAddedByTeacherResponse])
def student_added_by_teacher(id: int, db: Session = Depends(get_db)):
    if get_teacher := db.query(models.Teacher).filter(models.Teacher.id == id).first():
        return ( db.query(models.StudentsInClass)
        .filter(models.Teacher.id == id)
        .filter(models.StudentsInClass.student_table).all())
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="teacher with id of {id} not found")


@app.get("/teacher/get_student/all")
def get_student(db: Session = Depends(get_db)):
    return db.query(models.StudentsInClass).all()



@app.post("/teacher/add_student_mark")
def add_student_mark(add_student_mark: StudentMarks, db: Session = Depends(get_db)):
    find_student = db.query(models.Student).filter(models.Student.id == add_student_mark.student).first()
    find_teacher = db.query(models.Teacher).filter(models.Teacher.id == add_student_mark.teacher).first()

    if not find_student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
        detail="student with id of {id} not found")
    
    if not find_teacher:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
        detail="teacher with id of {id} not found")
    
    query = models.StudentMarks(**add_student_mark.__dict__)

    db.add(query)
    db.commit()
    db.refresh(query)
    return { "response": "Marks uploaded successfully!",
        "results": query}


@app.get("/teacher/{id}/mark_list", response_model=List[StudentMarksResponse])
def teacher_list_of_student_mark(id: int, db: Session = Depends(get_db)):
    """It's best practice to obtain student id from jwt when they are logged in
    """
    if get_teacher := db.query(models.Teacher).filter(models.Teacher.id == id).first():
        return (db.query(models.Teacher).filter(models.Teacher.id == id)
        .filter(models.Teacher.student_mark_table)
        .all())
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="teacher with id of {id} not found")


@app.get("/student/{id}/mark_list", response_model=List[StudentMarksResponse])
def all_student_mark_list(id: int, db: Session = Depends(get_db)):  
    """It's best practice to obtain student id from jwt when they are logged in
    """
    return (db.query(models.StudentsInClass).filter(models.StudentsInClass.id==id)
        .filter(models.StudentsInClass.student_mark_table)
        .all())

@app.put("/teacher/update_student_mark/{id}")
def update_student_mark(update_student_mark_form: UpdateStudentMarks, 
                        id: int, db: Session = Depends(get_db)):

    find_student = (db.query(models.Student)
    .filter(models.Student.id == update_student_mark_form.student).first())

    find_teacher = db.query(models.Teacher).filter(models.Teacher.id == id).first()

    if not find_student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
        detail="student with id of {id} not found")
    
    if not find_teacher:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
        detail="teacher with id of {id} not found")
    
    query = db.query(models.StudentMarks).filter(models.StudentMarks.id)
    if not query.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
        detail="Mark with id of {id} not found")

    query.update(update_student_mark_form.__dict__)
    db.commit()
    return { "response": "Marks successfully Updated!",
        "results": query.first()}


#################################################################################
@app.get("/get_class_assignment_by_id/{id}")
def get_class_assignment(id: int, db: Session = Depends(get_db)):
    return db.query(models.ClassAssignment).filter(models.ClassAssignment.id==id).first()


@app.get("/get_class_assignment")
def get_all_class_assignment(limit: int=5, db: Session = Depends(get_db)):
    return db.query(models.ClassAssignment).filter(models.ClassAssignment.id).limit(limit).all()


@app.get("/get_class_assignment/{name}")
def get_all__class_assignment_by_name(name:str, limit: int=5, db: Session = Depends(get_db)):
    return db.query(models.ClassAssignment).filter(models.ClassAssignment.assignment_name.ilike(f"%{name}%")).limit(limit).all()


@app.get("/get_all_assignment_by_teacher/{id}")
def get_all_assignment_by_teacher(id: int, limit: int=5, db: Session = Depends(get_db)):
    return db.query(models.ClassAssignment).filter(models.ClassAssignment.teacher==id).limit(limit).all()



@app.get("/student_get_all_assignment_by_teacher", response_model=List[AssignmentForm])
def student_get_all_assignment_by_teacher(limit: int=5, db: Session = Depends(get_db)):
    return db.query(models.StudentsInClass).filter(models.StudentsInClass.assignment_table).limit(limit).all()


@app.post("/teacher/add_assignment")
async def add_assignment(db: Session = Depends(get_db),
                        file: UploadFile = File(...)):

    """_summary_
    Get teachers id from jwt token and perfrom validation
   
    """
    # find_teacher = db.query(models.Teacher).filter(models.Teacher.id == add_assignment.teacher).first()
    
    # if not find_teacher:
    #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
    #     detail="teacher with id of {id} not found")
    # db.query(models.class_assignment)

    student = (db.query(models.StudentsInClass)
    .filter(models.StudentsInClass.teacher==1)
    .filter(models.StudentsInClass.student).all())

    query = models.ClassAssignment(teacher=1, assignment_name=file.filename, assignment_url=f"http:www.{file.filename}.com", student=[*student])

    print(query)

    db.add(query)
    db.commit()
    db.refresh(query)
    return { "response": "Assignment uploaded successfully!",
        "results": query}


@app.put("/teacher/update_assignment/{id}")
async def update_assignment(id: int, db: Session = Depends(get_db),
                        file: UploadFile = File(...)):
    find_assignment = db.query(models.ClassAssignment).filter(models.ClassAssignment.id==id)
    
    if not find_assignment.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
        detail="assignment with id of {id} not found")


    query = dict({"assignment_name": file.filename, "assignment_url": f"http:www.{file.filename}.com"})

    ass_update = find_assignment.update(query, synchronize_session=False)
    db.commit()
    return {"success_response":"Assignment updated successfully",
      "results": ass_update.first()}



@app.put("/teacher/delete_assignment/{id}")
async def delete_assignment(id: int, db: Session = Depends(get_db)):
    find_assignment = db.query(models.ClassAssignment).filter(models.ClassAssignment.id==id).first()
    
    if not find_assignment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
        detail="assignment with id of {id} not found")
    db.delete(find_assignment)
    db.commit()
    return status.HTTP_204_NO_CONTENT

#####################################################################################################

@app.post("/send_message_to_teacher")
def send_message_to_teacher(message_teacher: MessageToTeacher, db: Session = Depends(get_db)):
    find_student = db.query(models.StudentsInClass).filter(models.StudentsInClass.id == message_teacher.student).first()

    """"
    Best practice is to get student id from jwt token, student must log in to be able to send message to teacher
    """
    find_teacher = db.query(models.Teacher).filter(models.Teacher.id == message_teacher.teacher).first()

    if not find_student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
        detail="student with id of {id} not found")
    
    if not find_teacher:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
        detail="teacher with id of {id} not found")
    
    query = models.MessageToTeacher(**message_teacher.__dict__)

    db.add(query)
    db.commit()
    db.refresh(query)
    return { "response": "Message sent successfully!",
        "results": query}


@app.get("/teacher/get_all_messages", response_model=List[Message])
def get_all_messages(id: int, limit: int=5, db: Session = Depends(get_db)):
    return (db.query(models.Teacher)
            .filter(models.Teacher.id ==1)
            .filter(models.Teacher.message_from_student)
            .limit(limit).all())


#############################################################################################

@app.post("/send_notice")
async def send_notice(notice_form: ClassNoticeForm, db: Session = Depends(get_db)):

    """
    Get teachers id from jwt token and perfrom validation
   
    """
    # find_teacher = db.query(models.Teacher).filter(models.Teacher.id == add_assignment.teacher).first()
    
    # if not find_teacher:
    #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
    #     detail="teacher with id of {id} not found")
    # db.query(models.class_assignment)

    students = (db.query(models.StudentsInClass).filter(models.StudentsInClass.teacher==1)
    .filter(models.StudentsInClass.student).all())

    query = models.ClassNotice(teacher=2, message=notice_form.message, 
        message_html=notice_form.message_html, student_in_class=[*students])
    print(query)

    db.add(query)
    db.commit()
    db.refresh(query)
    return { "response": "Notice sent successfully!",
        "results": query}

################################################################################
@app.get("/see_all_notice_to_student{id}", response_model=List[ClassNoticeResponse])
def see_all_notice_to_student(id:int, limit: int=5, db: Session = Depends(get_db)):
    return (db.query(models.StudentsInClass)
            .filter(models.StudentsInClass.id==id)
            .filter(models.StudentsInClass.notice_table)
            .limit(limit).all())

###################################################################################
@app.post("/student/submit_assignment")            
async def submit_assignment(file: UploadFile =File(...), student: int = Form(...), assignment_id: int = Form(...), db: Session = Depends(get_db)):
    
    """
    Get student id from jwt token and perfrom validation
    """
    print(assignment_id)
    find_assignment = (db.query(models.ClassAssignment)
    .filter(models.ClassAssignment.id == assignment_id).first())
    if not find_assignment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
        detail=f"assignment with id of {assignment_id} not found")

    teacher = find_assignment.teacher    
    submit_ass = models.SubmitAssignment(student=student, submitted_assignment=find_assignment.id,  
                                        teacher=teacher,  submitted_assignment_url=f"http://www.stembucket/{file.filename}.com")

    db.add(submit_ass)
    db.commit()
    db.refresh(submit_ass)
    return { "response": "Assignment sent successfully!",
        "results": submit_ass}


@app.get("/teacher/{id}submit_assignment_list")
async def submit_assignment_list(id: int, db: Session = Depends(get_db)):
    return (db.query(models.SubmitAssignment)
    .filter(models.SubmitAssignment.teacher == id)
    .filter(models.SubmitAssignment.id).all())