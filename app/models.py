from email import message
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


from .database import Base

class_student = Table(
    "class_student",
    Base.metadata,
    Column("teacher_id", ForeignKey("teacher.id"), primary_key=True),
    Column("student_id", ForeignKey("student.id"), primary_key=True),

)

notice = Table(
    "notice",
    Base.metadata,
    Column("student_id", ForeignKey("studentinclass.id"), primary_key=True),
    # Column("teacher_id", ForeignKey("teacher.id"), primary_key=True),
    Column("notice_id", ForeignKey("class_notice.id"), primary_key=True),

)

assignment = Table( 
    "assignment",     
    Base.metadata,
    Column("student_id", ForeignKey("studentinclass.id"), primary_key=True),
    Column("assignment_id", ForeignKey("class_assignment.id"), primary_key=True)

)


class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=False, unique=True)
    email = Column(String, nullable=False, unique=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    password = Column(String, nullable=False)
    is_staff = Column(String, nullable=False)
    is_active = Column(String, nullable=False)
    is_student = Column(Boolean, default=False)
    is_teacher = Column(Boolean, default=False)

    student_table = relationship("Student", back_populates="student", uselist=False)    
    teacher_table = relationship("Teacher", back_populates="teacher", uselist=False)    

    
    def __iter__(self):
        return list(self.student)


class Student(Base):
    __tablename__= "student"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id",  ondelete="CASCADE"))
    roll_no = Column(String, nullable=False)
    email = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    student_profile_pic = Column(String, nullable=True)
    
    
    student = relationship("Users", back_populates="student_table")
    teacher_table = relationship("Teacher", secondary=class_student, back_populates="student_table")
    student_in_class_table = relationship("StudentsInClass", back_populates="student_table")


    def __str__(self) -> str:
        return self.email

    def __iter__(self):
        return self

class Teacher(Base):
    __tablename__= "teacher"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id",  ondelete="CASCADE"))
    name = Column(String, nullable=False)
    subject_name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    teacher_profile_pic_url = Column(String, nullable=False)
    
    teacher = relationship("Users", back_populates="teacher_table")
    student_table = relationship("Student", secondary=class_student)

    student_mark_table = relationship("StudentMarks", back_populates="teacher_table")
    teacher_for_student_in_class_table = relationship("StudentsInClass", back_populates="teacher_table")
    class_assignment_table = relationship("ClassAssignment", back_populates="teacher_table")
    message_from_student = relationship("MessageToTeacher", back_populates="message_to_teacher")
    class_notice_student_table = relationship("ClassNotice", back_populates="class_notice_teacher_table")


    def __str__(self):
        return self.name


class StudentMarks(Base):
    __tablename__ = "studentmarks"

    id = Column(Integer, primary_key=True, index=True)
    teacher = Column(Integer, ForeignKey("teacher.id",  ondelete="CASCADE"))
    student = Column(Integer, ForeignKey("studentinclass.id",  ondelete="CASCADE"))
    subject_name = Column(String, nullable=True)
    marks_obtained = Column(Integer)
    maximum_marks = Column(Integer)

    student_in_class_table = relationship("StudentsInClass", back_populates="student_mark_table")
    teacher_table = relationship("Teacher", back_populates="student_mark_table")


    def __str__(self):
        return self.subject_name


class StudentsInClass(Base):
    __tablename__ = "studentinclass"

    id = Column(Integer, primary_key=True, index=True)
    teacher = Column(Integer, ForeignKey("teacher.id", ondelete="CASCADE"))
    student = Column(Integer, ForeignKey("student.id", ondelete="CASCADE"))

    student_table = relationship("Student", back_populates="student_in_class_table")
    teacher_table = relationship("Teacher", back_populates="teacher_for_student_in_class_table")

    message = relationship("MessageToTeacher",  back_populates="student_in_class")
    student_mark_table = relationship("StudentMarks", back_populates="student_in_class_table")
    notice_table = relationship("ClassNotice", secondary=notice, back_populates="student_in_class")
    assignment_table = relationship("ClassAssignment", secondary=assignment, back_populates="student")


    def __str__(self):
        return str(self.student)

    def __iter__(self):
        return self


class MessageToTeacher(Base):
    __tablename__ = "message_to_teacher"

    id = Column(Integer, primary_key=True, index=True)
    student = Column(Integer, ForeignKey("studentinclass.id", ondelete="CASCADE"))
    teacher = Column(Integer, ForeignKey("teacher.id", ondelete="CASCADE"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    message = Column(String, nullable=False)
    message_html = Column(String, nullable=False)

    student_in_class = relationship("StudentsInClass", back_populates="message")
    message_to_teacher= relationship("Teacher", back_populates="message_from_student")

    def __str__(self):
        return f"{self.message} - {self.student}"

    class Meta:
        ordering = ['-created_at']
        unique_together = ['student', 'message']


class ClassNotice(Base):
    __tablename__="class_notice"

    id = Column(Integer, primary_key=True, index=True)
    teacher = Column(Integer, ForeignKey("teacher.id", ondelete="CASCADE"))
    # student = Column(Integer, ForeignKey("studentinclass.id", ondelete="CASCADE"))
    created_at =Column(DateTime(timezone=True), server_default=func.now())
    message = Column(String, nullable=True)
    message_html = Column(String, nullable=True)

    class_notice_teacher_table = relationship("Teacher", back_populates="class_notice_student_table")
    student_in_class = relationship("StudentsInClass", secondary=notice, back_populates="notice_table")

    def __str__(self):
        return self.message


class ClassAssignment(Base):
    __tablename__= "class_assignment"

    id = Column(Integer, primary_key=True, index=True)    
    teacher = Column(Integer, ForeignKey("teacher.id", ondelete="CASCADE"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    assignment_name = Column(String, nullable=False)
    assignment_url = Column(String, nullable=False)

    teacher_table = relationship("Teacher", back_populates="class_assignment_table")
    student = relationship("StudentsInClass", secondary=assignment, back_populates="assignment_table")



class SubmitAssignment(Base):
    __tablename__= "submit_assignment"

    id = Column(Integer, primary_key=True, index=True)
    student = Column(Integer, ForeignKey("student.id", ondelete="CASCADE"))
    teacher = Column(Integer, ForeignKey("teacher.id", ondelete="CASCADE"))
    submitted_assignment = Column(Integer, ForeignKey("class_assignment.id", ondelete="CASCADE"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    submitted_assignment_url = Column(String, nullable=False)

    student_table = relationship("Student")
    teacher_table = relationship("Teacher")
    submitted_assignment_table = relationship("ClassAssignment")
