# Kiyo Construction - Bid Leveling Automation

A web-based bid leveling automation solution with real-time visualization, guided workflow, and high accuracy. The system automates the extraction of bid data from PDFs, performs intelligent leveling, and provides results in standardized Excel formats.

## Project Structure

```
kiyo-construction/
├── frontend/     # Next.js application with Material UI
└── backend/      # Django application with REST API
```

## Features

- Modern UI with responsive design
- Fullscreen layout with spreadsheet and chat panels
- API endpoints for document management
- PostgreSQL database integration

## Setup Instructions

### Frontend Setup (Next.js)

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Run the development server:
   ```bash
   npm run dev
   ```

The frontend will be available at `http://localhost:3000`

### Backend Setup (Django)

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create and activate virtual environment using uv:
   ```bash
   uv venv
   source .venv/bin/activate  # On Unix or MacOS
   # or
   .venv\Scripts\activate     # On Windows
   ```

3. Install dependencies:
   ```bash
   uv pip install -r requirements.txt
   ```

4. Make sure PostgreSQL is running and create the database:
   ```bash
   createdb kiyo_construction
   ```

5. Run migrations:
   ```bash
   python manage.py migrate
   ```

6. Start the development server:
   ```bash
   python manage.py runserver
   ```

The backend API will be available at `http://localhost:8000/api/`

## API Endpoints

- `GET /api/` - Hello World endpoint

## Environment Variables

Create `.env` files in both frontend and backend directories:

### Frontend (.env.local)
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Backend (.env)
```
DEBUG=True
SECRET_KEY=your-secret-key
DB_USER=your_database_username
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ORIGIN_WHITELIST=http://localhost:3000
```

## Development

- Frontend: Next.js with Material-UI
- Backend: Django with PostgreSQL
- API Documentation: Available at `http://localhost:8000/api/docs/` when running the backend server 