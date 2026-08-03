# Pasos para probar y desplegar la versión corregida

## Camino recomendado: base nueva

La base anterior fue alterada manualmente y se permite eliminar datos de prueba. La opción más segura y rápida es crear una base nueva y conservar un respaldo de la anterior.

### 1. Respaldar la base anterior

Desde pgAdmin crea un Backup completo antes de eliminar o abandonar la base anterior. No uses el respaldo como script en Query Tool si está en formato personalizado; ese formato se restaura con Restore/`pg_restore`.

### 2. Crear una base vacía

Crea, por ejemplo:

```text
control_vehicular_nuevo
```

En Query Tool confirma:

```sql
SELECT current_database();
```

### 3. Ejecutar los scripts

Ejecuta uno por uno y detente ante el primer error:

1. `database/02_create_tables.sql`
2. `database/03_seed_data.sql`
3. `database/06_recrear_superadmin.sql`
4. `database/07_verify_deploy.sql`

No ejecutes `04_alter_tables.sql` ni `05_alter_tables_v3.sql` en una base nueva.

Credenciales temporales:

```text
Correo: superadmin@admin.com
Contraseña: PasswordSuperadmin123
```

Cambia la contraseña después de verificar el acceso.

### 4. Configurar el backend local

En `backend`:

```powershell
Copy-Item .env.example .env
```

Edita `.env` con la base nueva. Genera una clave aleatoria, por ejemplo:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Colócala en `SECRET_KEY`. No subas `.env`.

### 5. Crear un entorno virtual limpio

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip check
python -c "from importlib.metadata import version; print('bcrypt', version('bcrypt')); print('docxtpl', version('docxtpl'))"
```

`bcrypt` debe ser `4.0.1`. No instales dependencias manualmente fuera de `requirements.txt`.

### 6. Levantar el backend

```powershell
uvicorn app.main:app --reload
```

Prueba:

```text
http://127.0.0.1:8000/health
http://127.0.0.1:8000/docs
```

`/health` debe devolver:

```json
{"status":"ok"}
```

### 7. Levantar el frontend

Abre `frontend/index.html` con Live Server. En local, la aplicación detecta automáticamente `http://127.0.0.1:8000`.

Si Live Server usa un puerto distinto de 5500, agrega el origen exacto a `CORS_ORIGINS` en `.env`, por ejemplo:

```dotenv
CORS_ORIGINS=http://127.0.0.1:5501,http://localhost:5501
```

Reinicia Uvicorn después de modificar `.env`.

### 8. Ejecutar pruebas mínimas

Sigue `DEPLOY_CHECKLIST.md`. Como mínimo prueba en este orden:

1. Login de superadmin.
2. Alta única y baja/reactivación de persona.
3. Alta de vehículo y visualización de tarjeta.
4. Salida sin área ni hora.
5. Presupuesto y gasto de gasolina.
6. Regreso sin saldo final obligatorio.
7. Resguardo descargable.
8. Usuario suspendido sin acceso.

Revisa Network y la terminal. No avances si aparece 404, 422, 500 o CORS.

## Configuración de producción

### Backend

Configura en la plataforma:

- `DATABASE_URL`, o bien las variables `DB_*`.
- `SECRET_KEY` nueva.
- `CORS_ORIGINS` con el dominio exacto del frontend, sin diagonal final.
- variables SMTP solo si se habilitará recuperación de contraseña.

Comando de inicio típico:

```text
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### Frontend

Si backend y frontend están en dominios diferentes, edita antes de publicar:

```javascript
window.CONTROL_VEHICULAR_API_URL = "https://URL-PUBLICA-DEL-BACKEND";
```

en `frontend/js/config.js`.

Si ambos se sirven bajo el mismo origen y el proxy envía las rutas al backend, puede permanecer vacío.

### Resguardos

Muchos proveedores borran archivos locales al reiniciar. Para conservar resguardos `.docx`, configura un volumen persistente o almacenamiento externo.

## Alternativa: conservar la base existente

Solo úsala si los datos son necesarios:

1. Backup completo.
2. `database/00_preflight_existing.sql`.
3. Resolver todos los conflictos reportados.
4. `database/04_alter_tables.sql`.
5. `database/05_alter_tables_v3.sql`.
6. `database/06_recrear_superadmin.sql`.
7. `database/03_seed_data.sql`.
8. `database/07_verify_deploy.sql`.

No mezcles esta ruta con la instalación nueva.
