from db import db  # Import db from db.py

# User Table
class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(50), nullable=False)  # admin or student

    def __repr__(self):
        return f"<User {self.username}>"

# Course Table
class Course(db.Model):
    __tablename__ = 'courses'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    course_name = db.Column(db.String(100), nullable=False)
    course_code = db.Column(db.String(50), unique=True, nullable=False)
    course_duration = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"<Course {self.course_name}>"

# Student Table
class Student(db.Model):
    __tablename__ = 'students'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=True)

    # Relationship with Course
    course = db.relationship('Course', backref='students')

    def __repr__(self):
        return f"<Student {self.student_name}>"
