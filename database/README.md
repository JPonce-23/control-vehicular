# Base de datos

Hay dos rutas distintas. No mezcles los pasos.

## Instalación nueva

Crea una base vacía y ejecuta, en este orden:

1. `02_create_tables.sql`
2. `03_seed_data.sql`
3. `06_recrear_superadmin.sql`
4. `07_verify_deploy.sql`

No ejecutes `04_alter_tables.sql` ni `05_alter_tables_v3.sql` en una base nueva: son migraciones para versiones anteriores.

## Base existente del despliegue anterior

Haz primero un respaldo completo. Después:

1. Ejecuta `00_preflight_existing.sql` y resuelve cualquier duplicado que devuelva.
2. Ejecuta `04_alter_tables.sql`.
3. Ejecuta `05_alter_tables_v3.sql`.
4. Ejecuta `06_recrear_superadmin.sql`.
5. Ejecuta `03_seed_data.sql`.
6. Ejecuta `07_verify_deploy.sql`.

La migración no borra gastos ni otros registros. Si el preflight muestra gastos antiguos sin salida, deben corregirse manualmente porque no existe una asociación que pueda inferirse con seguridad.

## Superadministrador temporal

- Correo: `superadmin@admin.com`
- Contraseña inicial: `PasswordSuperadmin123`

La cuenta se identifica por `es_superadmin`, no por el ID 1. Cambia la contraseña después del primer acceso.

## Archivos heredados

- `control_vehicular_v1.sql` es un respaldo en formato personalizado/binario; se restaura con `pg_restore`, no con Query Tool.
- `schema.sql` y `seed.sql` son copias sincronizadas de los scripts 02 y 03 para compatibilidad con documentación anterior.
