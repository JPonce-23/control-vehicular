# Validación realizada

Fecha de revisión: 31 de julio de 2026.

## Resultados satisfactorios

- Python: todos los módulos de `backend/app` compilan sin errores sintácticos.
- JavaScript: los 17 archivos de `frontend/js` pasan `node --check`.
- Dependencias: `requirements.txt` está en UTF-8 e incluye `bcrypt==4.0.1` y `docxtpl`.
- Empaquetado: no contiene `.env`, `.git`, `venv`, `__pycache__`, `.pyc` ni respaldos locales.
- OpenAPI: 43 rutas publicadas, sin duplicados exactos; `/tokens/` no está expuesto.
- Frontend/backend: las llamadas `apiFetch` revisadas corresponden con rutas publicadas.
- DOM: no quedaron referencias literales a elementos eliminados en los formularios revisados.
- Modelos/esquema: las 15 tablas de SQLAlchemy coinciden en columnas y nulabilidad con el esquema final.

## Prueba HTTP de integración

Se ejecutó un flujo integral con una base SQLite temporal para validar la lógica de la aplicación:

- login y protección del superadministrador sin depender del ID 1;
- suspensión de usuario y rechazo de JWT anterior;
- recuperación de contraseña con token almacenado mediante hash;
- alta única de persona y rechazo de duplicado;
- alta de vehículo y validación de tarjeta;
- salida sin área/hora y forzada a provisional;
- generación y descarga de resguardo básico;
- presupuesto, gasto y rechazo de sobregasto;
- regreso con saldo opcional y estado de mantenimiento;
- corrección administrativa y sincronización del vehículo;
- ajuste de odómetro autenticado y atribuido al usuario del token.

Conteos finales del flujo: una persona, un vehículo, una salida, un regreso, un presupuesto, un gasto y un ajuste.

## Pendientes obligatorios antes de producción

- Ejecutar los scripts SQL en PostgreSQL real. Este entorno no disponía de un servidor PostgreSQL/`psql`.
- Crear un entorno virtual limpio en Windows o en el servidor y ejecutar `pip install -r requirements.txt`.
- Confirmar el login con el `bcrypt` nativo instalado desde `requirements.txt`.
- Ejecutar `DEPLOY_CHECKLIST.md` en local o staging.
- Configurar dominio real, CORS, base de datos, secretos y persistencia de documentos.
