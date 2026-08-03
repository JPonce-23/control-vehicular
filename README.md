# Sistema de Control Vehicular PA

Aplicación FastAPI + PostgreSQL con frontend HTML/CSS/JavaScript para administrar vehículos, personas autorizadas, salidas, regresos, resguardos y combustible.

## Preparación local

1. Crea una base vacía y sigue `database/README.md`.
2. Copia `backend/.env.example` como `backend/.env` y completa los valores.
3. Crea un entorno virtual limpio:

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip check
uvicorn app.main:app --reload
```

4. Abre `frontend/pages/index.html` o `frontend/index.html` con Live Server.
5. En local, `frontend/js/api.js` detecta automáticamente `http://127.0.0.1:8000`.

## Producción

- Configura las variables de `backend/.env.example` en la plataforma; no subas `.env`.
- Define los orígenes públicos del frontend en `CORS_ORIGINS`.
- Si frontend y backend usan dominios diferentes, edita `frontend/js/config.js` con la URL pública del backend.
- Ejecuta `uvicorn app.main:app --host 0.0.0.0 --port $PORT` o el equivalente de tu plataforma.
- El almacenamiento local de resguardos puede ser efímero en algunos proveedores. Usa un volumen persistente si necesitas conservar los `.docx` después de reinicios.

## Verificación

Consulta:

- `/health`
- `/docs`

Luego ejecuta el checklist de `DEPLOY_CHECKLIST.md`.
