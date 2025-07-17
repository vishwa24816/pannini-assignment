import os
import jwt
from functools import wraps
from flask import Blueprint, request, jsonify, current_app
from app.app import db
from app.models.assignment import Assignment, Submission
from app.models.user import User

bp = Blueprint('assignment', __name__)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = User.query.get(data['user_id'])
        except:
            return jsonify({'message': 'Token is invalid!'}), 401
        return f(current_user, *args, **kwargs)
    return decorated

def teacher_required(f):
    @wraps(f)
    def decorated(current_user, *args, **kwargs):
        if current_user.role != 'teacher':
            return jsonify({'message': 'Teacher role required!'}), 403
        return f(current_user, *args, **kwargs)
    return decorated

@bp.route('/assignments', methods=['POST'])
@token_required
@teacher_required
def create_assignment(current_user):
    """
    Create a new assignment (teacher only)
    ---
    parameters:
      - name: Authorization
        in: header
        type: string
        required: true
        description: JWT token
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            title:
              type: string
            description:
              type: string
    responses:
      201:
        description: Assignment created successfully
      400:
        description: Bad request
      401:
        description: Unauthorized
      403:
        description: Forbidden
    """
    data = request.get_json()
    title = data.get('title')
    description = data.get('description')
    if not title or not description:
        return jsonify({'message': 'Missing title or description'}), 400
    new_assignment = Assignment(title=title, description=description, created_by=current_user.id)
    db.session.add(new_assignment)
    db.session.commit()
    return jsonify({'message': 'Assignment created successfully'}), 201

@bp.route('/assignments', methods=['GET'])
@token_required
def get_assignments(current_user):
    """
    Get all assignments
    ---
    parameters:
      - name: Authorization
        in: header
        type: string
        required: true
        description: JWT token
    responses:
      200:
        description: List of assignments
      401:
        description: Unauthorized
    """
    assignments = Assignment.query.all()
    output = []
    for assignment in assignments:
        assignment_data = {}
        assignment_data['id'] = assignment.id
        assignment_data['title'] = assignment.title
        assignment_data['description'] = assignment.description
        output.append(assignment_data)
    return jsonify({'assignments': output})

@bp.route('/assignments/<int:assignment_id>/submit', methods=['POST'])
@token_required
def submit_assignment(current_user, assignment_id):
    """
    Submit an assignment (student only)
    ---
    parameters:
      - name: Authorization
        in: header
        type: string
        required: true
        description: JWT token
      - name: assignment_id
        in: path
        type: integer
        required: true
      - name: file
        in: formData
        type: file
        required: true
    responses:
      201:
        description: Assignment submitted successfully
      400:
        description: Bad request
      401:
        description: Unauthorized
      403:
        description: Forbidden
    """
    if current_user.role != 'student':
        return jsonify({'message': 'Student role required!'}), 403
    if 'file' not in request.files:
        return jsonify({'message': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'message': 'No selected file'}), 400
    if file:
        upload_folder = os.path.join(current_app.root_path, 'uploads')
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
        file_path = os.path.join(upload_folder, file.filename)
        file.save(file_path)
        new_submission = Submission(assignment_id=assignment_id, student_id=current_user.id, file_path=file_path)
        db.session.add(new_submission)
        db.session.commit()
        return jsonify({'message': 'Assignment submitted successfully'}), 201

@bp.route('/assignments/<int:assignment_id>/submissions', methods=['GET'])
@token_required
@teacher_required
def get_submissions(current_user, assignment_id):
    """
    Get all submissions for an assignment (teacher only)
    ---
    parameters:
      - name: Authorization
        in: header
        type: string
        required: true
        description: JWT token
      - name: assignment_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: List of submissions
      401:
        description: Unauthorized
      403:
        description: Forbidden
    """
    submissions = Submission.query.filter_by(assignment_id=assignment_id).all()
    output = []
    for submission in submissions:
        submission_data = {}
        submission_data['id'] = submission.id
        submission_data['student_id'] = submission.student_id
        submission_data['file_path'] = submission.file_path
        submission_data['submitted_at'] = submission.submitted_at
        output.append(submission_data)
    return jsonify({'submissions': output})
