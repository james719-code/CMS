# Club Management System (CMS)

A comprehensive web-based platform for managing university clubs and student organizations at Partido State University. The system streamlines club registration, membership management, event coordination, and administrative oversight.

## Description

The Club Management System is a full-stack web application designed to simplify club administration. It provides students with tools to register organizations, manage members, and track activities, while giving administrators the ability to oversee all clubs, approve registrations, and manage system-wide operations.

## Features

- **Organization Management**
  - Student-led organization registration and approval workflow
  - Organization profiles with leadership and membership tracking
  - One-student-one-org enforcement policy

- **Role-Based Access Control**
  - Admin: Full system control and oversight
  - Organization Leaders: Manage their club and members
  - Members: View club information and participate in activities

- **Member Management**
  - Membership requests and approvals
  - Member profiles with avatars
  - Member statistics and engagement tracking

- **Events & Activities**
  - Event creation and scheduling
  - Event details and descriptions

- **Documentation**
  - Document upload and management
  - Document sharing within organizations

- **Financial Tracking**
  - Budget management and tracking
  - Receipt uploads and expense documentation

- **Announcements**
  - Organization-wide announcements
  - Communication between leaders and members

- **Analytics**
  - Club statistics and metrics
  - Membership trends and engagement data

## Tech Stack

### Backend
- **Framework**: Django 5.2
- **API**: Django REST Framework (DRF)
- **Authentication**: JWT (djangorestframework-simplejwt)
- **Database**: SQLite (development) / TODO (production)
- **CORS**: django-cors-headers
- **File Handling**: Pillow (image processing)
- **Filtering**: django-filter
- **Language**: Python 3.8+

### Frontend
- **Framework**: React 19
- **Build Tool**: Vite
- **Styling**: Tailwind CSS v4
- **UI Components**: shadcn/ui, Radix UI
- **HTTP Client**: Axios
- **Routing**: React Router v7
- **Icons**: Lucide React
- **Theme**: next-themes
- **Language**: JavaScript/JSX
- **Runtime**: Node.js 14+

## Installation

### Prerequisites
- Python 3.8 or higher
- Node.js 14 or higher and npm
- Git (optional)

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create and activate a virtual environment (recommended):
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run database migrations:
   ```bash
   python manage.py makemigrations club
   python manage.py migrate
   ```

5. Create a superuser account for admin access:
   ```bash
   python manage.py createsuperuser
   ```
   Follow the prompts to set username, email, and password.

6. Start the development server:
   ```bash
   python manage.py runserver
   ```
   The API will be available at `http://127.0.0.1:8000/`

### Frontend Setup

1. Open a new terminal and navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install Node dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```
   The application will be available at `http://localhost:5173/`

## Usage

### Accessing the Application

- **Frontend**: http://localhost:5173/
  - Login with a student or admin account
  - Dashboard view depends on user role

- **Backend API**: http://127.0.0.1:8000/api/
  - Explore available endpoints
  - See API documentation at `/api/` endpoint

- **Django Admin**: http://127.0.0.1:8000/admin/
  - Login with superuser credentials
  - Manage all data models directly

### User Workflows

**Student User**:
1. Sign up for an account
2. Register a new organization (if admin approves)
3. Invite members to join
4. Create events and announcements
5. Upload documents and manage budget

**Admin User**:
1. Review pending organization registrations
2. Approve or reject registration requests
3. Monitor all organizations and members
4. View system-wide statistics
5. Manage throttling and permissions

## Environment Variables

### Backend (.env or set in system)
```
DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_DEBUG=true
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
DRF_AUTH_THROTTLE=25/hour
DRF_USER_THROTTLE=100/hour
DRF_ANON_THROTTLE=10/hour
```

### Frontend (.env)
```
VITE_API_BASE_URL=http://127.0.0.1:8000/api
```

### Environment Setup Examples (Windows PowerShell)
```powershell
$env:DJANGO_SECRET_KEY="your-long-random-secret-key"
$env:DJANGO_DEBUG="true"
$env:DJANGO_ALLOWED_HOSTS="127.0.0.1,localhost"
$env:CORS_ALLOWED_ORIGINS="http://localhost:5173"
```

**Note**: For production, set `DJANGO_DEBUG=false`, use a strong SECRET_KEY, and configure exact allowed hosts/origins.

## Project Structure

```
WebApp-ClubManagementSystem/
├── backend/                      # Django backend
│   ├── manage.py                # Django management script
│   ├── db.sqlite3               # SQLite database
│   ├── requirements.txt          # Python dependencies
│   ├── backend/                 # Django settings
│   │   ├── settings.py          # Project configuration
│   │   ├── urls.py              # URL routing
│   │   ├── wsgi.py              # WSGI configuration
│   │   └── asgi.py              # ASGI configuration
│   ├── club/                    # Main app
│   │   ├── models.py            # Database models
│   │   ├── views.py             # API views
│   │   ├── serializers.py       # DRF serializers
│   │   ├── permissions.py       # Custom permissions
│   │   ├── auth_backend.py      # Authentication backend
│   │   ├── urls.py              # App URL routing
│   │   ├── tests.py             # Tests
│   │   └── migrations/          # Database migrations
│   └── media/                   # Uploaded files (avatars, documents, etc.)
├── frontend/                     # React frontend
│   ├── index.html               # Entry HTML
│   ├── package.json             # Node dependencies
│   ├── vite.config.js           # Vite configuration
│   ├── eslint.config.js         # ESLint configuration
│   ├── src/
│   │   ├── main.jsx             # React entry point
│   │   ├── App.jsx              # Root component
│   │   ├── api/                 # API client configuration
│   │   ├── components/          # Reusable React components
│   │   │   └── ui/              # shadcn/ui components
│   │   ├── context/             # React context (Auth, etc.)
│   │   ├── hooks/               # Custom React hooks
│   │   ├── pages/               # Page components
│   │   │   └── officer/         # Officer-specific pages
│   │   └── lib/                 # Utility functions
│   └── public/                  # Static assets
├── INSTRUCTIONS.md              # Setup instructions
├── README.md                    # This file
└── package.json                 # Root package.json
```

## Scripts

### Backend Scripts
```bash
# Run development server
python manage.py runserver

# Create database migrations
python manage.py makemigrations club

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Open interactive shell
python manage.py shell

# Run tests
python manage.py test
```

### Frontend Scripts
```bash
# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Run ESLint
npm run lint
```

## License

TODO - Add your license information here

## Contact

**Project**: Club Management System (CMS)
**TODO**: Add maintainer contact information

---

**For detailed setup instructions, refer to [INSTRUCTIONS.md](INSTRUCTIONS.md)**
