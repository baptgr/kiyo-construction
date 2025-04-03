# Kiyo Construction - Bid Leveling Automation

A web-based bid leveling automation solution with real-time visualization, guided workflow, and high accuracy. The system automates the extraction of bid data from PDFs, performs intelligent leveling, and provides results in standardized Excel formats.

## Project Structure

```
kiyo-construction/
├── frontend/     # Next.js application
└── backend/      # Django application
```

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

4. Run migrations:
   ```bash
   python manage.py migrate
   ```

5. Start the development server:
   ```bash
   python manage.py runserver
   ```

The backend API will be available at `http://localhost:8000`

## Environment Variables

Create `.env` files in both frontend and backend directories. Example variables needed:

### Frontend (.env.local)
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Backend (.env)
```
DEBUG=True
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://localhost/kiyo_construction
```

## Development

- Frontend: Next.js with Material-UI
- Backend: Django with PostgreSQL
- API Documentation: Available at `http://localhost:8000/api/docs/` when running the backend server 