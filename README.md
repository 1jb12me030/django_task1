# django_task1

This project is a Django-based RESTful API for task management with CRUD functionality, task filtering, and auto-scaling logic to manage worker processes efficiently. A simulated AWS Lambda integration sends notifications when tasks are completed.

## 🚀 Setup Instructions

### Prerequisites
- Python 3.10 or above
- Django 4.x
- PostgreSQL (or compatible Aurora DB)
- Redis (optional for improved caching)

### Installation Steps
1. Clone the repository:
   ```bash
   git clone <repository_url>
   cd task_manager
   ```
2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate   # On Windows use 'venv\Scripts\activate'
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set up the environment variables:
   Create a `.env` file with the following details:
   ```env
   DATABASE_URL=postgres://<user>:<password>@<host>:<port>/<database>
   AWS_LAMBDA_SIMULATED=true
   ```
5. Run database migrations:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```
6. Create a superuser to access the admin panel:
   ```bash
   python manage.py createsuperuser
   ```
7. Start the development server:
   ```bash
   python manage.py runserver
   ```

## 📋 API Endpoints

| Endpoint                  | Method | Description                         |
|---------------------------|---------|-------------------------------------|
| `api/tasks/`                  | GET     | List all tasks                     |
| `api/tasks/<id>/`             | GET     | Retrieve a specific task            |
| `api/tasks/`                  | POST    | Create a new task                   |
| `api/tasks/<id>/`             | PUT     | Update an existing task             |
| `api/tasks/<id>/`             | DELETE  | Delete a specific task              |
| 'rate-limited/'               | GET     | Get rate-limited or exceeded rate-limit|


### Sample Payload (POST `/tasks/`)
```json
{
    "title": "New Task",
    "description": "Sample task description",
    "status": "pending"
}
```

### Sample Response (200 OK)
```json
{
    "id": 1,
    "title": "New Task",
    "status": "completed"
}
```

## 🧠 Design Choices

### Auto-Scaling Logic
- Workers automatically scale up when pending tasks exceed a defined threshold.
- Workers scale down when pending tasks reduce to zero, ensuring optimal resource usage.
- Immediate scale-down logic is triggered when no pending tasks are detected.

### AWS Lambda Simulation
- Simulated AWS Lambda function sends notifications when a task is marked as 'completed'.
- Mimics asynchronous event-driven architecture for scalability.

## 📂 SQL Schema Overview
The database schema is designed with:
- **Task Table:** Tracks task details, statuses, and timestamps.
- **Indexing:** Optimized indexing on `status` for efficient filtering.

### Sample Table Schema
```sql
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_status ON tasks (status);
```

## 📋 Evaluation Criteria
- **PEP 8 Compliance:** Code follows best practices for readability and maintainability.
- **Django ORM:** Efficient use of ORM for data queries.
- **AWS Concepts:** Simulated Lambda logic ensures scalability and efficient notifications.
- **Documentation Quality:** Clear instructions, design reasoning, and endpoint details provided.

For any issues or contributions, please create a pull request or raise an issue. 😊

