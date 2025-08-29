# MoodMate Backend

AI-powered mood tracking and wellness platform backend built with Django REST Framework.

## Features

- 🔐 **JWT Authentication** - Secure user registration, login, and logout
- 📊 **Mood Tracking** - CRUD operations for personal mood logs
- 🤖 **AI Emotion Analysis** - Hugging Face integration for emotion detection
- 🎵 **Music Recommendations** - Curated Spotify playlists by mood
- 💳 **Payment Integration** - IntaSend checkout and webhook handling
- 📈 **Subscription Management** - Free and Premium plans with quota limits
- 📚 **API Documentation** - OpenAPI/Swagger documentation
- 🛡️ **Security** - CORS, rate limiting, and proper permissions

## Tech Stack

- **Backend**: Django 5.x, Django REST Framework
- **Authentication**: djangorestframework-simplejwt
- **Database**: MySQL (production), SQLite (development)
- **AI**: Hugging Face Inference API
- **Payments**: IntaSend Python SDK
- **Documentation**: drf-spectacular (OpenAPI)
- **Deployment**: Railway/Render ready

## Quick Start

### 1. Environment Setup

```bash
# Clone and navigate to project
cd moodmate_backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env
```

### 2. Configure Environment

Edit `.env` file with your settings:

```env
DJANGO_SECRET_KEY=your_secret_key_here
DJANGO_DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

# Database (MySQL for production, SQLite for local dev)
DB_NAME=moodmate_db
DB_USER=root
DB_PASSWORD=your_password
DB_HOST=127.0.0.1
DB_PORT=3306

# External APIs
HUGGINGFACE_API_TOKEN=hf_your_token_here
INTASEND_TOKEN=your_intasend_token
INTASEND_PUBLISHABLE_KEY=your_intasend_pub_key
INTASEND_TEST_MODE=True

# Frontend CORS
FRONTEND_ORIGINS=http://localhost:3000,https://your-frontend.com
```

### 3. Database Setup

```bash
# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Seed demo data
python manage.py shell -c "exec(open('scripts/seed_demo.py').read())"
```

### 4. Run Development Server

```bash
python manage.py runserver
```

The API will be available at `http://127.0.0.1:8000`

## API Documentation

- **Swagger UI**: http://127.0.0.1:8000/api/docs/
- **OpenAPI Schema**: http://127.0.0.1:8000/api/schema/
- **Admin Panel**: http://127.0.0.1:8000/admin/

## Demo Credentials

After running the seed script:
- **Username**: `demo`
- **Password**: `password`
- **Email**: `demo@demo.com`

## API Endpoints

### Authentication
- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - User login
- `POST /api/auth/logout/` - User logout
- `POST /api/auth/token/refresh/` - Refresh JWT token

### User Profile
- `GET /api/users/me/` - Get current user profile

### Mood Logs
- `GET /api/moods/` - List user's mood logs
- `POST /api/moods/` - Create new mood log
- `GET /api/moods/{id}/` - Get specific mood log
- `DELETE /api/moods/{id}/` - Delete mood log

### AI Analysis
- `POST /api/ai/analyze/` - Analyze emotion in text
- `GET /api/music/recommend/?mood=happy` - Get music recommendations

### Payments
- `GET /api/payments/plans/` - List subscription plans
- `POST /api/payments/create_checkout/` - Create payment checkout
- `GET /api/payments/payments/` - List user payments
- `POST /api/payments/webhook/` - IntaSend webhook (public)

## Frontend Integration

### Login and Token Usage

```javascript
// Login
const loginResponse = await fetch("http://127.0.0.1:8000/api/auth/login/", {
  method: "POST",
  headers: {"Content-Type": "application/json"},
  body: JSON.stringify({username: "demo", password: "password"})
});
const loginData = await loginResponse.json();
localStorage.setItem("token", loginData.access);

// Use token for authenticated requests
const token = localStorage.getItem("token");
const response = await fetch("http://127.0.0.1:8000/api/moods/", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    "Authorization": `Bearer ${token}`
  },
  body: JSON.stringify({
    mood: "stressed", 
    intensity: 7, 
    note: "Big presentation tomorrow"
  })
});
```

### AI Analysis

```javascript
const analysisResponse = await fetch("http://127.0.0.1:8000/api/ai/analyze/", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    "Authorization": `Bearer ${token}`
  },
  body: JSON.stringify({
    text: "Didn't sleep well last night, feeling anxious",
    persist: true
  })
});
const analysis = await analysisResponse.json();
// analysis.emotion.label, analysis.advice, analysis.music_recommendations
```

### Payment Checkout

```javascript
const checkoutResponse = await fetch("http://127.0.0.1:8000/api/payments/create_checkout/", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    "Authorization": `Bearer ${token}`
  },
  body: JSON.stringify({
    plan_code: "PREMIUM_MONTHLY",
    phone: "0712345678",
    email: "user@example.com"
  })
});
const checkout = await checkoutResponse.json();
// Use checkout.checkout_url to redirect user or show STK push status
```

## Testing

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test users
python manage.py test moods
python manage.py test ai
python manage.py test payments

# Run with coverage
pip install coverage
coverage run --source='.' manage.py test
coverage report
```

## Deployment

### Railway Deployment

1. Connect your GitHub repository to Railway
2. Add environment variables in Railway dashboard
3. Set `DJANGO_DEBUG=False` and update `ALLOWED_HOSTS`
4. Railway will automatically use the `Procfile`

### Render Deployment

1. Connect repository to Render
2. Choose "Web Service"
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `gunicorn moodmate_backend.wsgi:application`
5. Add environment variables

### Environment Variables for Production

```env
DJANGO_SECRET_KEY=your_production_secret_key
DJANGO_DEBUG=False
ALLOWED_HOSTS=your-domain.com,your-app.railway.app

# Database (use production MySQL)
DB_NAME=your_prod_db
DB_USER=your_prod_user
DB_PASSWORD=your_prod_password
DB_HOST=your_prod_host
DB_PORT=3306

# External APIs (production tokens)
HUGGINGFACE_API_TOKEN=hf_your_production_token
INTASEND_TOKEN=your_production_intasend_token
INTASEND_PUBLISHABLE_KEY=your_production_pub_key
INTASEND_TEST_MODE=False

# Frontend
FRONTEND_ORIGINS=https://your-frontend-domain.com
```

### IntaSend Webhook Setup

After deployment, configure your IntaSend webhook URL:
```
https://your-api-domain.com/api/payments/webhook/
```

## Project Structure

```
moodmate_backend/
├── manage.py                 # Django management script
├── requirements.txt          # Python dependencies
├── Procfile                 # Railway/Render deployment
├── Dockerfile               # Container deployment
├── moodmate_backend/        # Main Django project
│   ├── settings.py          # Django settings
│   ├── urls.py              # Main URL configuration
│   └── wsgi.py              # WSGI application
├── users/                   # User authentication & profiles
├── moods/                   # Mood tracking functionality
├── ai/                      # AI analysis services
├── payments/                # Payment & subscription handling
├── scripts/                 # Utility scripts
│   └── seed_demo.py         # Demo data seeding
└── docs/                    # Documentation
    └── postman_collection.json
```

## Security Features

- JWT token authentication with refresh tokens
- CORS configuration for frontend integration
- Rate limiting on AI endpoints (60 requests/minute)
- Input validation and sanitization
- Proper user data isolation (users only see their own data)
- Webhook signature validation ready
- SQL injection protection via Django ORM

## AI Quota System

- **Free Plan**: 5 AI calls per day
- **Premium Plan**: 200 AI calls per day
- Daily quotas reset at midnight (Africa/Nairobi timezone)
- Quota enforcement with clear error messages
- Automatic quota reset on plan upgrades

## Support

For issues or questions:
1. Check the API documentation at `/api/docs/`
2. Review the Postman collection for example requests
3. Check Django logs for detailed error information
4. Ensure all environment variables are properly configured

## License

This project is proprietary software for MoodMate platform.