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

## Setup Instructions
1. Clone the repo: `git clone <your-repo-url>`
2. Create virtual env: `python -m venv venv`
3. Install requirements: `pip install -r requirements.txt`
4. Run migrations: `python manage.py migrate`
5. Start server: `python manage.py runserver`