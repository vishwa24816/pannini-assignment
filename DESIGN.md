# System Design: EdTech Assignment Tracking System

## 1. Core Entities and Relationships

The system will have three core entities: `User`, `Assignment`, and `Submission`.

### User
- `id`: Unique identifier for the user (Primary Key)
- `username`: User's username
- `password`: Hashed password for the user
- `role`: User's role ('teacher' or 'student')

### Assignment
- `id`: Unique identifier for the assignment (Primary Key)
- `title`: Title of the assignment
- `description`: Description of the assignment
- `created_by`: ID of the teacher who created the assignment (Foreign Key to User)
- `created_at`: Timestamp when the assignment was created

### Submission
- `id`: Unique identifier for the submission (Primary Key)
- `assignment_id`: ID of the assignment being submitted to (Foreign Key to Assignment)
- `student_id`: ID of the student who submitted the assignment (Foreign Key to User)
- `file_path`: Path to the submitted file
- `submitted_at`: Timestamp when the assignment was submitted

### Relationships

- A `User` (teacher) can create multiple `Assignments`.
- An `Assignment` is created by one `User` (teacher).
- A `User` (student) can make multiple `Submissions`.
- A `Submission` is made by one `User` (student) for one `Assignment`.
- An `Assignment` can have multiple `Submissions`.

## 2. API Endpoints

### Authentication
- `POST /signup`: User registration (teacher or student).
- `POST /login`: User login to get a JWT token.

### Assignments
- `POST /assignments`: Teacher creates a new assignment.
  - Requires teacher role.
- `GET /assignments`: List all assignments (for both teachers and students).
- `GET /assignments/{id}`: Get details of a specific assignment.

### Submissions
- `POST /assignments/{id}/submit`: Student submits an assignment.
  - Requires student role.
  - Supports file uploads.
- `GET /assignments/{id}/submissions`: Teacher views all submissions for a specific assignment.
  - Requires teacher role.

## 3. Authentication Strategy

We will use JSON Web Tokens (JWT) for authentication.

- **Signup**: Users will register with a username, password, and role (teacher or student).
- **Login**: Upon successful login, the server will generate a JWT containing the user's ID and role. This token will be sent to the client.
- **Authenticated Requests**: The client will include the JWT in the `Authorization` header for all protected endpoints. The server will validate the token and check the user's role to authorize the requested action.

## 4. Scaling Suggestions

- **Database**:
  - Use a more robust database like PostgreSQL or MySQL in a production environment.
  - Implement database indexing on frequently queried columns (e.g., `created_by` in `Assignment`, `assignment_id` and `student_id` in `Submission`).
  - Use a database connection pool to manage database connections efficiently.
- **Application Layer**:
  - Use a production-ready WSGI server like Gunicorn or uWSGI to run the Flask application.
  - Run multiple instances of the application behind a load balancer to distribute traffic.
- **File Storage**:
  - Instead of storing files on the local filesystem, use a cloud storage service like Amazon S3 or Google Cloud Storage. This will make the application stateless and easier to scale horizontally.
- **Caching**:
  - Use a caching layer like Redis or Memcached to cache frequently accessed data (e.g., assignment details, user profiles).
- **Asynchronous Tasks**:
  - For long-running tasks like processing large file uploads, use a task queue like Celery with a message broker like RabbitMQ or Redis.
