document.addEventListener('DOMContentLoaded', () => {
    const signupForm = document.getElementById('signup-form');
    const loginForm = document.getElementById('login-form');
    const authForms = document.getElementById('auth-forms');
    const content = document.getElementById('content');
    let token = null;
    let userRole = null;

    signupForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const username = document.getElementById('signup-username').value;
        const password = document.getElementById('signup-password').value;
        const role = document.getElementById('signup-role').value;
        const response = await fetch('/signup', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password, role })
        });
        const data = await response.json();
        alert(data.message);
    });

    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const username = document.getElementById('login-username').value;
        const password = document.getElementById('login-password').value;
        const response = await fetch('/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });
        const data = await response.json();
        if (data.token) {
            token = data.token;
            const decodedToken = JSON.parse(atob(token.split('.')[1]));
            userRole = decodedToken.role;
            authForms.style.display = 'none';
            content.style.display = 'block';
            loadDashboard();
        } else {
            alert(data.message);
        }
    });

    function loadDashboard() {
        if (userRole === 'teacher') {
            fetch('/templates/teacher.html')
                .then(response => response.text())
                .then(html => {
                    content.innerHTML = html;
                    loadAssignments();
                    const assignmentForm = document.getElementById('assignment-form');
                    assignmentForm.addEventListener('submit', createAssignment);
                });
        } else if (userRole === 'student') {
            fetch('/templates/student.html')
                .then(response => response.text())
                .then(html => {
                    content.innerHTML = html;
                    loadAssignments();
                });
        }
    }

    async function loadAssignments() {
        const response = await fetch('/assignments', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const data = await response.json();
        const assignmentsList = document.getElementById('assignments');
        assignmentsList.innerHTML = '';
        data.assignments.forEach(assignment => {
            const li = document.createElement('li');
            li.innerHTML = `<span>${assignment.title}</span>`;
            if (userRole === 'teacher') {
                const viewSubmissionsButton = document.createElement('button');
                viewSubmissionsButton.textContent = 'View Submissions';
                viewSubmissionsButton.onclick = () => loadSubmissions(assignment.id);
                li.appendChild(viewSubmissionsButton);
            } else {
                const submitButton = document.createElement('button');
                submitButton.textContent = 'Submit';
                submitButton.onclick = () => showSubmissionForm(assignment.id);
                li.appendChild(submitButton);
            }
            assignmentsList.appendChild(li);
        });
    }

    async function createAssignment(e) {
        e.preventDefault();
        const title = document.getElementById('assignment-title').value;
        const description = document.getElementById('assignment-description').value;
        const response = await fetch('/assignments', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ title, description })
        });
        const data = await response.json();
        alert(data.message);
        loadAssignments();
    }

    async function loadSubmissions(assignmentId) {
        const response = await fetch(`/assignments/${assignmentId}/submissions`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const data = await response.json();
        const submissionsList = document.getElementById('submissions');
        submissionsList.innerHTML = '';
        data.submissions.forEach(submission => {
            const li = document.createElement('li');
            li.textContent = `Submission by student ${submission.student_id}: ${submission.file_path}`;
            submissionsList.appendChild(li);
        });
        document.getElementById('submissions-list').style.display = 'block';
    }

    function showSubmissionForm(assignmentId) {
        const submissionForm = document.getElementById('submit-assignment-form');
        submissionForm.style.display = 'block';
        submissionForm.onsubmit = async (e) => {
            e.preventDefault();
            const fileInput = document.getElementById('submission-file');
            const formData = new FormData();
            formData.append('file', fileInput.files[0]);
            const response = await fetch(`/assignments/${assignmentId}/submit`, {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${token}` },
                body: formData
            });
            const data = await response.json();
            alert(data.message);
            submissionForm.style.display = 'none';
        };
    }
});
