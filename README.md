# Tambua Afrika Studios

A multidisciplinary creative ecosystem for African storytellers — publishing, theatre, comics, and digital media.  
This Django-based platform supports content management, submissions, user authentication, and (optionally) crowdfunding.

## Features

- **Department-based content system** (Studios, Ink, Stage, Comics, Shop)
- **User authentication** with email and Google OAuth
- **Creator profiles** and role-based dashboards
- **Submission management** for open calls (anthologies, plays, comics)
- **Newsletter subscription** and cookie consent
- **Premium editorial design** with responsive layouts
- **Internationalization** support (language switcher)
- **Optional crowdfunding modules** (planned)

## Tech Stack

- Python 3.11+
- Django 5.x
- django-allauth (authentication)
- Bootstrap 5 (frontend)
- SQLite (development) / PostgreSQL (production)
- WhiteNoise (static files)
- Gmail SMTP (email sending)

## Local Setup

### Prerequisites

- Python 3.11+
- pip
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/tambua-afrika.git
   cd tambua-afrika
Create a virtual environment

bash
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
Install dependencies

bash
pip install -r requirements.txt
Set up environment variables
Create a .env file in the project root:

text
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=Tambua Afrika <your-email@gmail.com>
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
You can copy .env.example if provided.

Run migrations

bash
python manage.py migrate
Create a superuser

bash
python manage.py createsuperuser
Run the development server

bash
python manage.py runserver
Visit http://127.0.0.1:8000/

Deployment
The project is configured to work on Render free tier.
See DEPLOYMENT.md (if available) or contact the maintainers for deployment instructions.

Project Structure
text
tambua-afrika/
├── config/          # Project settings & main URLs
├── core/            # Core app (home, auth, models)
├── ink/             # Publishing department
├── stage/           # Theatre department
├── comics/          # Comics department
├── shop/            # Merchandise & store
├── submissions/     # User submissions
├── journal/         # Newsletter & articles
├── users/           # User profiles & dashboards
├── templates/       # HTML templates
├── static/          # CSS, JS, images
├── media/           # User uploads (ignored by Git)
└── requirements.txt
Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

License
MIT

© 2026 Tambua Afrika Studios Ltd. All rights reserved.