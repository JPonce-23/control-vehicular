-- Verificación posterior a instalación/migración. Todas las consultas deben revisarse.

SELECT current_database() AS base_activa;

SELECT id, correo, rol, estado, es_superadmin
FROM usuario_sistema
WHERE es_superadmin = TRUE OR correo = 'superadmin@admin.com';

SELECT column_name, is_nullable, data_type
FROM information_schema.columns
WHERE table_schema = 'public'
  AND (
      (table_name = 'persona_autorizada' AND column_name = 'cargo') OR
      (table_name = 'vehiculo' AND column_name IN ('num_economico', 'num_tarjeta_gasolina', 'saldo_tarjeta_gasolina')) OR
      (table_name = 'salida' AND column_name IN ('area_en_viaje', 'fecha_regreso_estimada', 'monto_agregado_tarjeta', 'saldo_tarjeta_salida')) OR
      (table_name = 'regreso' AND column_name IN ('saldo_tarjeta_regreso', 'monto_gastado_tarjeta')) OR
      (table_name = 'usuario_sistema' AND column_name = 'es_superadmin')
  )
ORDER BY table_name, column_name;

-- Debe devolver cero filas.
SELECT num_tarjeta_gasolina, COUNT(*)
FROM vehiculo
WHERE num_tarjeta_gasolina IS NOT NULL AND btrim(num_tarjeta_gasolina) <> ''
GROUP BY num_tarjeta_gasolina
HAVING COUNT(*) > 1;

-- Debe devolver cero filas.
SELECT salida_id, COUNT(*)
FROM regreso
GROUP BY salida_id
HAVING COUNT(*) > 1;

-- Debe devolver cero filas.
SELECT id, nombre, apellido_paterno
FROM persona_autorizada
WHERE cargo IS NULL OR btrim(cargo) = '';

-- Información, no necesariamente cero: gastos antiguos sin salida o capturador
-- deben revisarse antes de imponer NOT NULL en una base migrada.
SELECT
    COUNT(*) FILTER (WHERE salida_id IS NULL) AS gastos_sin_salida,
    COUNT(*) FILTER (WHERE capturado_por IS NULL) AS gastos_sin_capturador
FROM gasto_gasolina;
