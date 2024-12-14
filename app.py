from flask import Flask, request, jsonify
from db import db  # Import db from db.py
from models import Course, Student, User  # Import models from models.py
from functools import wraps

# Initialize the Flask app
app = Flask(__name__)

# Configure the database (MySQL)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:Patel%40123@localhost/backend_task'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db.init_app(app)


# Basic route to test the app
@app.route('/')
def home():
    """
    Basic route to check if the app is running.
    """
    return "Backend Task API is Running!"


# Role-based access control decorator
def requires_role(role):
    """
    A decorator to ensure the user has the correct role (admin or student).
    """
    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            user_id = request.headers.get('id')  # Get user_id from the header
            if not user_id:
                return jsonify({"error": "User not authenticated"}), 403

            # Fetch the user from the database
            user = User.query.get(user_id)
            if not user:
                return jsonify({"error": "User not found!"}), 403

            # Check if the user has the expected role
            if user.role != role:
                return jsonify({"error": f"Permission denied. Must be {role}"}), 403

            return fn(*args, **kwargs)  # Proceed to the actual route function

        return decorated_view
    return wrapper


# Route to add a new student (only for Admin)
@app.route('/students', methods=['POST'])
@requires_role('admin')  # Only admin can add students
def add_student():
    """
    Add a new student with course assignment.
    """
    data = request.get_json()

    # Check if the student email already exists
    existing_student = Student.query.filter_by(email=data['email']).first()
    if existing_student:
        return jsonify({"error": "Student with this email already exists!"}), 400

    # Get the course by course code
    course = Course.query.filter_by(course_code=data['course_code']).first()
    if not course:
        return jsonify({"error": "Course not found!"}), 404

    # Create a new student instance and add to database
    new_student = Student(
        student_name=data['student_name'],
        email=data['email'],
        course_id=course.id
    )

    db.session.add(new_student)
    db.session.commit()

    return jsonify({"message": "Student added successfully!"}), 201


# Route to retrieve students by course
@app.route('/courses/<string:course_code>/students', methods=['GET'])
@requires_role('admin')  # Only admin can access this route
def get_students_by_course(course_code):
    """
    Retrieve all students enrolled in a given course.
    """
    course = Course.query.filter_by(course_code=course_code).first()
    if not course:
        return jsonify({"error": "Course not found!"}), 404

    students = Student.query.filter_by(course_id=course.id).all()
    student_data = []
    for student in students:
        student_info = {
            "student_name": student.student_name,
            "email": student.email,
            "course_name": course.course_name,
            "course_code": course.course_code
        }
        student_data.append(student_info)

    return jsonify(student_data)  # Return student data as JSON


# Route to update a student's details (only for Admin)
@app.route('/students/<int:student_id>', methods=['PUT'])
@requires_role('admin')  # Only admin can update students
def update_student(student_id):
    """
    Update the details of an existing student.
    """
    data = request.get_json()

    # Get the student by ID
    student = Student.query.get(student_id)
    if not student:
        return jsonify({"error": "Student not found!"}), 404

    # Check if the course exists
    course = Course.query.filter_by(course_code=data['course_code']).first()
    if not course:
        return jsonify({"error": "Course not found!"}), 404

    # Update student details
    student.student_name = data['student_name']
    student.email = data['email']
    student.course_id = course.id
    db.session.commit()

    return jsonify({"message": "Student updated successfully!"})


# Route to delete a student (only for Admin)
@app.route('/students/<int:student_id>', methods=['DELETE'])
@requires_role('admin')  # Only admin can delete students
def delete_student(student_id):
    """
    Delete a student by ID.
    """
    student = Student.query.get(student_id)
    if not student:
        return jsonify({"error": "Student not found!"}), 404

    db.session.delete(student)
    db.session.commit()

    return jsonify({"message": "Student deleted successfully!"})


# Route to retrieve all students with their associated course details
@app.route('/students', methods=['GET'])
@requires_role('admin')  # Only admin can access this route
def get_all_students():
    """
    Retrieve all students with their course details.
    """
    students = Student.query.all()
    student_data = []

    for student in students:
        course = Course.query.get(student.course_id)
        student_info = {
            "student_name": student.student_name,
            "email": student.email,
            "course_name": course.course_name,
            "course_code": course.course_code
        }
        student_data.append(student_info)

    return jsonify(student_data)  # Return student data as JSON


# Route to get a student's details (only for Student)
@app.route('/students/<int:student_id>', methods=['GET'])
@requires_role('student')  # Only students can view their details
def get_student(student_id):
    """
    Retrieve a specific student's details along with course information.
    """
    student = Student.query.get(student_id)
    if not student:
        return jsonify({"error": "Student not found!"}), 404

    course = Course.query.get(student.course_id)

    return jsonify({
        "student_name": student.student_name,
        "email": student.email,
        "course_name": course.course_name,
        "course_code": course.course_code
    })


# Start the Flask app
if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Create all tables in the database
        print("Tables created successfully!")
    app.run(debug=False)  # Run the app
