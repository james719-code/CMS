# University Club Management System - Setup Instructions

This guide provides instructions on how to set up and run the University Club Management System (CMS) locally. The system consists of a Django backend and a React frontend.

## Prerequisites

*   **Python 3.8+**
*   **Node.js 14+** and **npm**

## Backend Setup

1.  Navigate to the backend directory:
    ```bash
    cd backend
    ```

2.  (Optional but recommended) Create and activate a virtual environment:
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
    *Dependencies include: Django 5.2.x, DRF, SimpleJWT, CORS Headers, Django Filter, and Pillow.*

4.  Configure backend environment variables as needed:
    ```bash
    # Windows PowerShell examples
    $env:DJANGO_SECRET_KEY="change-this-to-a-long-random-value"
    $env:DJANGO_DEBUG="true"
    $env:DJANGO_ALLOWED_HOSTS="127.0.0.1,localhost"
    $env:CORS_ALLOWED_ORIGINS="http://localhost:5173,http://127.0.0.1:5173"
    ```
    For deployment, set `DJANGO_DEBUG=false`, set a real `DJANGO_SECRET_KEY`, and configure exact allowed hosts/origins.

5.  Run database migrations:
    ```bash
    python3 manage.py makemigrations club
    python3 manage.py migrate
    ```
    The app migrations were cleaned to match the current backend models. For an old local SQLite database created from previous migrations, back up needed data, remove `backend/db.sqlite3`, then run `python3 manage.py migrate` fresh.

6.  Create a superuser (for accessing the Django Admin interface):
    ```bash
    python3 manage.py createsuperuser
    ```
    Follow the prompts to set an email and password.

7.  Run the development server:
    ```bash
    python3 manage.py runserver
    ```
    The backend API will be available at `http://127.0.0.1:8000/`.

## Frontend Setup

1.  Open a new terminal window and navigate to the frontend directory:
    ```bash
    cd frontend
    ```

2.  Install dependencies:
    ```bash
    npm install
    ```

3.  Start the React application (Vite):
    ```bash
    npm run dev
    ```
    The application will open in your browser at `http://localhost:5173/`.

## Accessing the Application

*   **Frontend User Interface:** `http://localhost:5173/` - Login and Dashboard.
*   **Backend Admin Interface:** `http://127.0.0.1:8000/admin/` - Log in with your superuser credentials to manage data.
*   **API Root:** `http://127.0.0.1:8000/api/` - Explore the REST API.

## Features Implemented

*   **One Student, One Org:** Strict enforcement that a student can lead only one organization.
*   **Organization Registration:** Workflow for students to register orgs and admins to approve them.
*   **Role-Based Access:** Different views for Admins, Leaders, and Members.
*   **Modern Frontend:** React + Vite + Tailwind CSS v4.

## Backend Security and Operations Notes

*   API lists are paginated using DRF's standard `count`, `next`, `previous`, and `results` response shape.
*   Login/register/token-heavy endpoints are throttled. Adjust rates with `DRF_AUTH_THROTTLE`, `DRF_USER_THROTTLE`, and `DRF_ANON_THROTTLE`.
*   Uploaded avatars/logos/documents/receipts are limited by size and extension. Uploaded media is untrusted and should be served as static files, never executed.
*   SQLite is acceptable for local use and small/private deployments only. It is not ideal for high-concurrency production workloads.
*   Before deploying with SQLite, schedule regular backups of `backend/db.sqlite3` and uploaded `backend/media/` files. A simple backup is a timestamped copy while the app is stopped.
*   For better SQLite reliability in a small deployment, enable WAL on the deployed database once:
    ```bash
    sqlite3 backend/db.sqlite3 "PRAGMA journal_mode=WAL;"
    ```
*   Run checks before deployment:
    ```bash
    python3 manage.py check
    python3 manage.py check --deploy
    python3 manage.py test club
    ```
