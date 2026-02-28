# QuizMaster API

A RESTful API built with Django Rest Framework for managing online quizzes and leaderboards.

## Features
- Custom User Roles (Teacher/Student)
- Token-based Authentication
- Real-time Grading Engine (Coming Soon)
- Global Leaderboard (Coming Soon)

## Tech Stack
- **Framework:** Django 5.x
- **API Engine:** Django Rest Framework (DRF)
- **Database:** PostgreSQL (Production) / SQLite (Development)

## 🏁 Getting Started

### 1. Clone the repository
git clone https://github.com/capsunlock/quizmaster_backend.git
cd quizmaster_backend

### 2. Set up Virtual Environment
python -m venv venv
#### Windows:
venv\Scripts\activate
#### Mac/Linux:
source venv/bin/activate

### 3. Install Dependencies
pip install -r requirements.txt

### 4. Database Setup
python manage.py makemigrations
python manage.py migrate

### 5. Run the Server
python manage.py runserver

## 🧪 Testing
Run the automated test suite to verify the Quiz engine and API endpoints:

python manage.py test quizzes

## 📂 Project Structure
- **/core**: Project configuration and settings.
- **/quizzes**: Core logic, including quiz taking, grading, and leaderboard.
- **/accounts**: User registration and authentication logic.
- **/static**: Global CSS and Vanilla JS logic.