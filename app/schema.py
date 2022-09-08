from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr

# from typing import 

class UserForm(BaseModel):
    username: str
    email: EmailStr
    first_name: str
    last_name: str
    password: str
    is_staff: bool = False
    is_active: bool = False
    is_student: bool = False
    is_teacher: bool= False


####################################################################
class StudentForm(BaseModel):    
    user_id: int
    roll_no: str
    email: EmailStr
    phone: str
    student_profile_pic: str

    class Config:
        orm_mode = True


######################################################################
class TeacherForm(BaseModel):    
    user_id:int
    name: str
    subject_name: str
    email: EmailStr
    phone: str
    teacher_profile_pic_url: str

################################################################
class AddStudentToClass(BaseModel):
    teacher:int
    student: int    

class StudentAddedByTeacherResponse(BaseModel):
    teacher: int
    # student: int
    student_table: StudentForm

    class Config:
        orm_mode = True

################################################################        
class StudentMarks(BaseModel):
    teacher: int
    student: int
    subject_name: str
    marks_obtained: int
    maximum_marks: int

    class Config:
        orm_mode = True


class UpdateStudentMarks(BaseModel):
    student: int
    marks_obtained: int
    maximum_marks: int

    class Config:
        orm_mode = True

################################################################
class StudentMark(StudentMarks):
    id: int

class StudentMarksResponse(BaseModel):
    # user_id: int
    student_table: StudentForm
    student_mark_table: list[StudentMark]

    class Config:
        orm_mode = True

####################################################################
class ClassAssignment(BaseModel):
    teacher: int
    created_at: datetime
    assignment_name: str
    assignment_url: str

    class Config:
        orm_mode = True

##################################################################################        
class AssignmentForm(BaseModel):
    # teacher: int
    assignment_table: List[ClassAssignment]

    class Config:
        orm_mode = True

################################################################################
class MessageToTeacher(BaseModel):
    student: int
    teacher: int
    message: str
    message_html: str

    class Config:
        orm_mode = True    

class Message(BaseModel):
    id: int
    subject_name: str
    phone: str
    name: str
    email: EmailStr
    teacher_profile_pic_url: str
    message_from_student: List[MessageToTeacher]        

    
    class Config:
        orm_mode = True    

###################################################################################
class ClassNoticeForm(BaseModel):
    message: str
    message_html: str
    
    class Config:
        orm_mode = True    


class ClassNoticeResponse(BaseModel):
    student: int
    notice_table: List[ClassNoticeForm]
    
    class Config:
        orm_mode = True    

########################################################################################
class SubmitAssignmentForm(BaseModel):
    student: int
    submitted_assignment: int
    # submitted_assignment_url: str
