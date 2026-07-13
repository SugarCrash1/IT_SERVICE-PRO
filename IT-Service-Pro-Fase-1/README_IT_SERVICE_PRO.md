# IT Service Pro

## Requisitos
- Python 3.11
- PostgreSQL
- Node.js 20 o 22 LTS

## Base de datos
```sql
CREATE USER itservice_user WITH PASSWORD 'ChangeMe123!';
CREATE DATABASE it_service_pro OWNER itservice_user;
```

## Backend
```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
alembic upgrade head
python -m app.seed.run_seed
uvicorn app.main:app --reload
```

Swagger: `http://localhost:8000/docs`

## Frontend
```powershell
cd frontend
npm config set registry https://registry.npmjs.org/
npm install --no-audit --no-fund
npm run dev
```

Frontend: `http://localhost:5173`
