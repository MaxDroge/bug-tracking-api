# Bug Tracking API

This project is a simple RESTful API for managing bug reports. It allows users to create, view, update, and delete bugs, making it a good example of backend development with Python.

## Features

- Create bug reports
- View all bugs
- View a single bug by ID
- Update bug details, status, and priority
- Delete bug reports

## Tech Used

- Python
- FastAPI
- SQLite
- SQLAlchemy

## How to Run

1. Install dependencies:
   pip install -r requirements.txt

2. Start the server:
   uvicorn main:app --reload

3. Open API docs:
   http://127.0.0.1:8000/docs