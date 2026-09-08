# Tambua Afrika Studios

**Tambua Afrika Studios** is a multidisciplinary creative ecosystem for African storytellers, supporting publishing, theatre, comics, and digital media.

This Django-based platform provides content management, creator profiles, submission management, user authentication, and a foundation for future crowdfunding initiatives.

## Features

* **Department-based content system** — Studios, Ink, Stage, Comics, and Shop
* **User authentication** — Email authentication and Google OAuth
* **Creator profiles** — User profiles with role-based dashboards
* **Submission management** — Open calls for anthologies, plays, comics, and other creative works
* **Newsletter subscription** — Newsletter management and subscription functionality
* **Cookie consent** — User privacy and consent management
* **Responsive design** — Premium editorial-inspired interface across desktop and mobile
* **Internationalization** — Language switching and multilingual support
* **Crowdfunding foundation** — Optional crowdfunding modules planned for future development

## Tech Stack

| Technology     | Purpose                      |
| -------------- | ---------------------------- |
| Python 3.11+   | Backend programming language |
| Django 5.x     | Web framework                |
| django-allauth | Authentication and OAuth     |
| Bootstrap 5    | Frontend framework           |
| SQLite         | Development database         |
| PostgreSQL     | Production database          |
| WhiteNoise     | Static file serving          |
| Gmail SMTP     | Email delivery               |

## Local Development

### Prerequisites

Make sure you have the following installed:

* Python 3.11 or later
* pip
* Git

### 1. Clone the Repository

```bash
git clone https://github.com/Benjamin-Swaka/Tambua-Afrika.git
cd Tambua-Afrika
```

### 2. Create a Virtual Environment

**macOS / Linux:**

```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows:**

```powershell
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root.

If the project includes an `.env.example` file, you can copy it:

```bash
cp .env.example .env
```

Then configure the required variables:

```env
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL="Tambua Afrika <your-email@gmail.com>"

GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
```

> **Security:** Never commit your `.env` file or expose secret keys, email passwords, OAuth credentials, or other sensitive configuration in the repository.

### 5. Run Database Migrations

```bash
python manage.py migrate
```

### 6. Create a Superuser

```bash
python manage.py createsuperuser
```

### 7. Start the Development Server

```bash
python manage.py runserver
```

The application will be available at:

```text
http://127.0.0.1:8000/
```

## Project Structure

```text
Tambua-Afrika/
├── config/             # Project configuration and main URLs
├── core/               # Core application and shared functionality
├── ink/                # Publishing department
├── stage/              # Theatre department
├── comics/             # Comics department
├── shop/               # Merchandise and store
├── submissions/        # Creator submissions
├── journal/            # Newsletter and editorial content
├── users/              # User profiles and dashboards
├── templates/          # HTML templates
├── static/             # CSS, JavaScript, and static assets
├── media/              # User-uploaded media (ignored by Git)
├── requirements.txt    # Python dependencies
└── manage.py            # Django management utility
```

## Deployment

The project is designed to support deployment on **Render**.

For deployment instructions, refer to `DEPLOYMENT.md` if available.

Production deployments should use appropriate environment variables, a production database such as PostgreSQL, and `DEBUG=False`.

## Contributing

Contributions are welcome.

For significant changes, please open an issue first to discuss the proposed change before submitting a pull request.

When submitting a pull request:

1. Create a dedicated branch for your changes.
2. Keep commits focused and descriptive.
3. Test your changes before submitting.
4. Update documentation where appropriate.

## License

This project is licensed under the MIT License.

## Copyright

© 2026 Tambua Afrika Studios Ltd. All rights reserved.
