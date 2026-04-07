# MzansiBuilds

A platform for developers to build in public, collaborate, and celebrate completed projects together.

**Built for the Derivco Code Skills Challenge**

## Tech Stack

- **Backend:** Python / Flask
- **Database:** PostgreSQL
- **Frontend:** HTML, CSS (custom), JavaScript
- **Theme:** Green, White, and Black

## Features

- **Account Management** — Register, login, update profile with bio, skills, and GitHub link
- **Project Creation** — Share what you're building with stage tracking and support requests
- **Live Feed** — Browse all projects with stage filtering and pagination
- **Comments** — Leave feedback and encouragement on any project
- **Collaboration Requests** — Raise your hand to collaborate; project owners can accept/decline
- **Milestone Tracking** — Log progress milestones as you build
- **Celebration Wall** — Completed projects are showcased on a dedicated wall of honour

## Setup Instructions

### Prerequisites

- Python 3.10+
- PostgreSQL installed and running

### 1. Clone / Download

```bash
cd "Mzansi Builds"
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate       # Windows
# source venv/bin/activate  # macOS/Linux
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Create the PostgreSQL Database

```sql
CREATE DATABASE mzansibuilds;
```

### 5. Configure Environment

Copy `.env.example` to `.env` and update the values:

```bash
copy .env.example .env
```

Edit `.env`:
```
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/mzansibuilds
```

### 6. Initialize the Database

```bash
flask init-db
```

### 7. (Optional) Seed with Sample Data

```bash
flask seed-db
```

### 8. Run the Application

```bash
flask run
```

Visit **http://127.0.0.1:5000** in your browser.

## Project Structure

```
Mzansi Builds/
├── app.py                  # Main Flask application with routes
├── config.py               # Configuration settings
├── models.py               # Database models (User, Project, Milestone, etc.)
├── forms.py                # WTForms form classes
├── requirements.txt        # Python dependencies
├── .env.example            # Environment variables template
├── static/
│   ├── css/
│   │   └── style.css       # Green/White/Black themed styles
│   └── js/
│       └── main.js         # Frontend interactivity
└── templates/
    ├── base.html            # Base layout with navbar + footer
    ├── index.html           # Landing page
    ├── celebration.html     # Celebration Wall
    ├── auth/
    │   ├── login.html
    │   ├── register.html
    │   ├── profile.html
    │   └── developer.html
    ├── projects/
    │   ├── _card.html       # Reusable project card
    │   ├── create.html
    │   ├── detail.html
    │   ├── edit.html
    │   ├── feed.html
    │   ├── my_projects.html
    │   └── collaborations.html
    └── errors/
        ├── 403.html
        └── 404.html
```
