# QuizMaster - Capstone Project

A full-stack Quiz application built with **Django** and **Vanilla JavaScript**. This platform allows teachers to create quizzes and students to take them, featuring real-time scoring, detailed result breakdowns, and leaderboard.

## Key Features
* **Dynamic Quiz Interface:** Fully responsive quiz player powered by Fetch API.
* **Detailed Results:** Instant grading with a question-by-question breakdown.
* **Leaderboard:** Ranking system based on accuracy.
* **Secure Authentication:** Role-based access for Students and Teachers.
* **RESTful API:** Clean data endpoints for quiz submission and scoring.

## Tech Stack
* **Backend:** Django 6.0, Django REST Framework
* **Frontend:** HTML5, CSS3 (Custom Variables), JavaScript (ES6+)
* **Database:** SQLite (Development)

## Getting Started

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

## Testing
Run the automated test suite to verify the Quiz engine and API endpoints:

python manage.py test quizzes

## Project Structure
- **/core**: Project configuration and settings.
- **/quizzes**: Core logic, including quiz taking, grading, and leaderboard.
- **/accounts**: User registration and authentication logic.
- **/static**: Global CSS and Vanilla JS logic.