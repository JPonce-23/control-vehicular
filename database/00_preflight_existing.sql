-- Ejecutar SOLO para evaluar una base existente antes de 04_alter_tables.sql.
-- No modifica información. Cada consulta de duplicados debería devolver cero filas.

SELECT current_database() AS base_evaluada;

SELECT correo, COUNT(*)
FROM usuario_sistema
WHERE correo = 'superadmin@admin.com'
GROUP BY correo
HAVING COUNT(*) > 1;

SELECT num_empleado, COUNT(*)
FROM usuario_sistema
WHERE num_empleado = 'SUPERADMIN'
GROUP BY num_empleado
HAVING COUNT(*) > 1;

SELECT num_tarjeta_gasolina, COUNT(*)
FROM vehiculo
WHERE num_tarjeta_gasolina IS NOT NULL AND btrim(num_tarjeta_gasolina) <> ''
GROUP BY num_tarjeta_gasolina
HAVING COUNT(*) > 1;

SELECT salida_id, COUNT(*)
FROM regreso
GROUP BY salida_id
HAVING COUNT(*) > 1;

SELECT salida_id, COUNT(*)
FROM resguardo
GROUP BY salida_id
HAVING COUNT(*) > 1;

SELECT nombre, COUNT(*)
FROM item_condicion
GROUP BY nombre
HAVING COUNT(*) > 1;

-- Debe devolver cero filas. Si devuelve pares, existen a la vez la clave antigua
-- y la nueva; fusiona sus revisiones antes de continuar.
WITH cambios(anterior, nuevo) AS (VALUES
    ('tapon_gas', 'tapon_gasolina'),
    ('aire_acond', 'aire_acondicionado'),
    ('radio_amfm', 'radio_am_fm'),
    ('jgo_herramientas', 'juego_herramientas'),
    ('bayoneta', 'bayoneta_aceite'),
    ('llave_tapon_gas', 'llave_tapon_gasolina'),
    ('cinturon_seg', 'cinturon_seguridad'),
    ('jgo_placas', 'juego_placas'),
    ('espejo_lat_izq', 'espejo_lateral_izquierdo'),
    ('espejo_lat_der', 'espejo_lateral_derecho'),
    ('revista_vehi', 'revista_vehicular')
)
SELECT cambios.anterior, cambios.nuevo
FROM cambios
WHERE EXISTS (SELECT 1 FROM item_inventario i WHERE i.nombre = cambios.anterior)
  AND EXISTS (SELECT 1 FROM item_inventario i WHERE i.nombre = cambios.nuevo);

SELECT nombre, COUNT(*)
FROM item_inventario
GROUP BY nombre
HAVING COUNT(*) > 1;

SELECT salida_id, item_condicion_id, COUNT(*)
FROM revision_condicion
GROUP BY salida_id, item_condicion_id
HAVING COUNT(*) > 1;

SELECT salida_id, item_id, COUNT(*)
FROM revision_inventario
GROUP BY salida_id, item_id
HAVING COUNT(*) > 1;

SELECT vehiculo_id, anio, COUNT(*)
FROM presupuesto_gasolina
GROUP BY vehiculo_id, anio
HAVING COUNT(*) > 1;

SELECT
    COUNT(*) FILTER (WHERE salida_id IS NULL) AS gastos_sin_salida,
    COUNT(*) FILTER (WHERE capturado_por IS NULL) AS gastos_sin_capturador
FROM gasto_gasolina;
