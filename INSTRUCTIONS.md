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
    pip install django djangorestframework django-cors-headers djangorestframework-simplejwt
    ```
    *Note: If a requirements.txt file exists, you can run `pip install -r requirements.txt` instead.*

4.  Run database migrations:
    ```bash
    python3 manage.py makemigrations
    python3 manage.py migrate
    ```

5.  Create a superuser (for accessing the Django Admin interface):
    ```bash
    python3 manage.py createsuperuser
    ```
    Follow the prompts to set a username, email, and password.

6.  Run the development server:
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

3.  Start the React application:
    ```bash
    npm start
    ```
    The application will open in your browser at `http://localhost:3000/`.

## Accessing the Application

*   **Frontend User Interface:** `http://localhost:3000/` - View the list of departments.
*   **Backend Admin Interface:** `http://127.0.0.1:8000/admins/` - Log in with your superuser credentials to manage departments, programs, users, and other data.
*   **API Root:** `http://127.0.0.1:8000/api/` - Explore the REST API.
