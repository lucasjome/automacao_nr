from sqlalchemy import Column, Integer, Unicode, UnicodeText, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from db_base import Base


class Course(Base):
    __tablename__ = 'courses'
    course_id = Column(Integer, primary_key=True)
    name = Column(Unicode(50),)
    description = Column(UnicodeText, nullable=True)
    hours = Column(Float)

    def __init__(self, name=None, description=None, hours=None):
        self.name = name
        self.description = description
        self.hours = hours


class Employee(Base):
    __tablename__ = 'employees'
    employee_id = Column(Integer, primary_key=True)
    name = Column(Unicode(50))
    completedcourses = relationship(
        "CompletedCourse", back_populates='employee')

    def __init__(self, name=None):
        self.name = name


class CompletedCourse(Base):
    __tablename__ = 'completedcourses'
    completedcourse_id = Column(Integer, primary_key=True)

    employee_id = Column(Integer, ForeignKey('employees.employee_id'))
    employee = relationship("Employee", foreign_keys=[employee_id])
    course_id = Column(Integer, ForeignKey('courses.course_id'))
    course = relationship("Course", foreign_keys=[course_id])

    donein = Column(DateTime)

    def __init__(self, employee_id=None, course_id=None, donein=None):
        self.employee_id = employee_id
        self.course_id = course_id
        self.donein = donein
