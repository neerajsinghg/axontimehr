how to run this
11:05 AM
The hostname http://frontend:3000 is an internal Docker service name used by containers (like Nginx) to talk to each other inside the Docker network.

From your computer's browser, you access the application using localhost.

Option 1: Running with Docker (Recommended)
Run the entire multi-container stack (Frontend, Backend, PostgreSQL, Redis, Celery) with a single command:

Open PowerShell in d:\axontimehr
Execute:
powershell
docker compose up -d --build
Open your browser:
Frontend UI Dashboard: http://localhost:3000
Backend Health Check: http://localhost:8000/api/v1/health
Swagger API Docs: http://localhost:8000/api/v1/docs
Option 2: Running Locally (Without Docker)
If you prefer to run services natively on your machine:

1. Start the Backend API (Terminal 1)
powershell
cd d:\axontimehr\backend
python -m uvicorn app.main:app --reload --port 8000
2. Start the Frontend Dashboard (Terminal 2)
powershell
cd d:\axontimehr\frontend
npm run dev
3. Open Browser
Navigate to http://localhost:3000 in your web browser.