# 🌞 JuaSmart — AI-Powered Solar Learning Platform

JuaSmart is a lightweight Django web application that teaches Kenyan learners about solar energy and sustainability. It features a smart, personalized AI chatbot tutor (JuaBot) that adapts to users’ learning level and course progress.

---

Features
- User registration and login system
- Personalized learning dashboard
- AI Chatbot tutor (OpenAI-powered)
- User profile and course tracking
- Dynamic, context-aware chatbot prompts
- Quiz functionality with scoring
- Responsive UI with Bootstrap
- Modular Django architecture

Tech Stack
Backend: Django 4.x
Frontend: HTML5, Bootstrap 5, JavaScript
Database: SQLite (for development)
AI Integration: OpenAI API (modular and pluggable)
Auth: Django’s built-in system

Local Setup

1. Clone the Repository
git clone https://github.com/your-username/jua-smart.git
cd jua-smart

2. Create Virtual Environment
python3 -m venv jua
source jua/bin/activate

3. Install Dependencies
pip install -r requirements.txt


Configure Settings
Edit your `settings.py` or use environment variables:


OPENAI_API_KEY = "xxx"
SECRET_KEY = "xxx"
DEBUG = True
```

Apply Migrations
python manage.py migrate


7. Run Development Server
python manage.py runserver


Then visit: [http://localhost:8000](http://localhost:8000)

---
Project Structure

jua_smart/
├── jua_smart/              # Main project settings
├── learning/               # Main app
│   ├── models.py           # UserProfile, Course, ChatMessage
│   ├── views.py            # Login, Register, Dashboard views
│   ├── services.py         # AI chatbot service using OpenAI
│   ├── templates/learning/ # HTML files (login, register, dashboard)
│   └── static/learning/    # JS and CSS files
├── manage.py
└── requirements.txt
```


JuaBot AI Integration

Uses OpenAI’s `chat.completions` endpoint to:

* Personalize replies based on user profile
* Reference completed courses and learning level
* Adapt complexity of response for beginners vs. advanced users



from openai import OpenAI

self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
```


Sample User Flows

* User registers → redirected to login
* Logs in → redirected to dashboard
* Can chat with AI tutor
* Quizzes available with instant scoring

