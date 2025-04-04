# DebugMe - AI-Powered Programming Knowledge Assessment Platform

DebugMe is a web platform that helps users assess and improve their programming knowledge through AI-generated tests and personalized feedback.

## Features

- User authentication and profile management
- Topic and subtopic selection
- AI-generated adaptive tests
- Performance tracking and feedback
- Detailed progress dashboard

## Tech Stack

- Backend: Django (Python)
- Database: SQLite3 (upgradeable to PostgreSQL)
- Frontend: Django templates
- AI Integration: Gemini API

## Setup Instructions

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
Create a `.env` file in the project root with:
```
GEMINI_API_KEY=your_api_key_here
SECRET_KEY=your_django_secret_key_here
```

4. Run migrations:
```bash
python manage.py migrate
```

5. Start the development server:
```bash
python manage.py runserver
```

## Project Structure

```
debugme/
├── debugme/          # Main project settings
├── accounts/         # User authentication and profiles
├── topics/          # Topic and subtopic management
├── tests/           # Test generation and execution
├── dashboard/       # User progress tracking
└── static/          # Static files
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License 