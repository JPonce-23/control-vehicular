# Correcciones aplicadas

Esta copia integra y corrige los cambios del paquete de mejoras. No depende del usuario con ID 1 y separa claramente una instalación nueva de una migración de base existente.

## Bloqueos corregidos

- Registro de salida: ya no intenta leer `fecha_fin_provisional` cuando el campo no existe.
- Salidas: área opcional, fecha sin captura manual de hora y tipo de movimiento forzado a `provisional` también en backend.
- Regresos: fecha sin hora visible, saldo final de tarjeta opcional y estado del vehículo derivado de las condiciones reportadas.
- Resguardos: se genera un documento básico aunque no exista una plantilla institucional `.docx`.
- Personas: evita altas duplicadas por reenvío, bloquea el botón durante la petición y agrega baja/reactivación lógica.
- Vehículos: muestra y valida el número de tarjeta de gasolina.
- Presupuesto: incluye vehículos suspendidos/fuera de servicio en el resumen histórico, pero impide nuevas asignaciones a vehículos no elegibles.
- Formularios principales: recargan después del alta y muestran `Registro completado`.
- Tablas: encabezados centrados.

## Seguridad y consistencia

- Eliminado el endpoint público que listaba tokens de recuperación.
- Los tokens de recuperación se guardan mediante hash y se invalidan al usarse.
- Los ajustes de odómetro requieren administrador y toman el autor desde el JWT.
- Un usuario suspendido deja de poder usar un token emitido previamente.
- El superadministrador se identifica mediante `es_superadmin`, no mediante `id = 1`.
- Se eliminaron routers duplicados y módulos de rutas obsoletos.
- CORS se configura mediante `CORS_ORIGINS`.
- La URL del backend del frontend se configura en `frontend/js/config.js`.
- Los modelos SQLAlchemy se alinearon con el esquema final de PostgreSQL.

## Base de datos

- `02_create_tables.sql`: esquema final para una instalación limpia.
- `03_seed_data.sql`: catálogos idempotentes completos.
- `06_recrear_superadmin.sql`: crea o repara el superadministrador sin depender del ID 1.
- `07_verify_deploy.sql`: validaciones posteriores.
- `00_preflight_existing.sql`, `04_alter_tables.sql` y `05_alter_tables_v3.sql`: ruta separada para migrar una base existente.
- Las migraciones no borran gastos automáticamente.

## Validaciones realizadas

- Compilación sintáctica de Python.
- Validación sintáctica de JavaScript.
- Comparación entre modelos SQLAlchemy y esquema SQL.
- Verificación de rutas de frontend contra OpenAPI.
- Prueba HTTP integral con una base temporal: login, usuarios, personas, vehículos, salidas, resguardos, combustible, regreso, correcciones y ajustes.

## Límites de la validación

No se ejecutaron los scripts contra un servidor PostgreSQL real en este entorno. Deben probarse en una base nueva local o de staging antes de tocar producción. Tampoco se incluyó una plantilla institucional de resguardo; el sistema utiliza el formato básico integrado hasta que se agregue una.
