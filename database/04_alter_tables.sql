-- Migración idempotente para bases creadas con versiones anteriores.
-- No elimina registros.

ALTER TABLE usuario_sistema
ADD COLUMN IF NOT EXISTS es_superadmin BOOLEAN NOT NULL DEFAULT FALSE;

ALTER TABLE persona_autorizada
ADD COLUMN IF NOT EXISTS cargo VARCHAR(150);

ALTER TABLE salida
ADD COLUMN IF NOT EXISTS cargo_en_viaje VARCHAR(150);

UPDATE persona_autorizada p
SET cargo = COALESCE(
    NULLIF(btrim(p.cargo), ''),
    (
        SELECT NULLIF(btrim(s.cargo_en_viaje), '')
        FROM salida s
        WHERE s.persona_id = p.id
        ORDER BY s.fecha_salida DESC
        LIMIT 1
    ),
    'Pendiente por definir'
)
WHERE cargo IS NULL OR btrim(cargo) = '';

ALTER TABLE persona_autorizada ALTER COLUMN cargo SET NOT NULL;
ALTER TABLE persona_autorizada ALTER COLUMN num_licencia DROP NOT NULL;
ALTER TABLE persona_autorizada ALTER COLUMN vigencia_licencia DROP NOT NULL;
ALTER TABLE persona_autorizada ALTER COLUMN tipo_licencia DROP NOT NULL;

ALTER TABLE vehiculo ALTER COLUMN num_economico DROP NOT NULL;
ALTER TABLE vehiculo ADD COLUMN IF NOT EXISTS num_tarjeta_gasolina VARCHAR(50);
ALTER TABLE vehiculo ADD COLUMN IF NOT EXISTS saldo_tarjeta_gasolina DECIMAL(12,2) NOT NULL DEFAULT 0;

ALTER TABLE salida ALTER COLUMN area_en_viaje DROP NOT NULL;
ALTER TABLE salida ADD COLUMN IF NOT EXISTS fecha_regreso_estimada DATE;
ALTER TABLE salida ADD COLUMN IF NOT EXISTS monto_agregado_tarjeta DECIMAL(12,2) NOT NULL DEFAULT 0;
ALTER TABLE salida ADD COLUMN IF NOT EXISTS saldo_tarjeta_salida DECIMAL(12,2) NOT NULL DEFAULT 0;
ALTER TABLE salida ALTER COLUMN forma_movimiento SET DEFAULT 'provisional';

ALTER TABLE regreso ALTER COLUMN fecha_regreso SET DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE regreso ADD COLUMN IF NOT EXISTS saldo_tarjeta_antes_regreso DECIMAL(12,2);
ALTER TABLE regreso ADD COLUMN IF NOT EXISTS saldo_tarjeta_regreso DECIMAL(12,2);
ALTER TABLE regreso ADD COLUMN IF NOT EXISTS monto_gastado_tarjeta DECIMAL(12,2);

ALTER TABLE presupuesto_gasolina ADD COLUMN IF NOT EXISTS mes_inicio INT NOT NULL DEFAULT 1;
ALTER TABLE presupuesto_gasolina ADD COLUMN IF NOT EXISTS mes_fin INT NOT NULL DEFAULT 12;

ALTER TABLE gasto_gasolina ADD COLUMN IF NOT EXISTS nivel_tanque nivel_gasolina_salida;
ALTER TABLE gasto_gasolina ADD COLUMN IF NOT EXISTS km_odometro DECIMAL(12,2);
ALTER TABLE gasto_gasolina ADD COLUMN IF NOT EXISTS capturado_por INT REFERENCES usuario_sistema(id);
ALTER TABLE gasto_gasolina ADD COLUMN IF NOT EXISTS fecha_registro TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE gasto_gasolina ALTER COLUMN litros DROP NOT NULL;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'presupuesto_gasolina_vehiculo_anio_unique') THEN
        ALTER TABLE presupuesto_gasolina
        ADD CONSTRAINT presupuesto_gasolina_vehiculo_anio_unique UNIQUE (vehiculo_id, anio);
    END IF;
END $$;

CREATE INDEX IF NOT EXISTS idx_salida_vehiculo ON salida (vehiculo_id);
CREATE INDEX IF NOT EXISTS idx_regreso_salida ON regreso (salida_id);
CREATE INDEX IF NOT EXISTS idx_gasto_gasolina_vehiculo ON gasto_gasolina (vehiculo_id);
CREATE INDEX IF NOT EXISTS idx_gasto_gasolina_fecha ON gasto_gasolina (fecha_gasto);
CREATE INDEX IF NOT EXISTS idx_gasto_gasolina_presupuesto ON gasto_gasolina (presupuesto_id);

-- Normaliza claves históricas del inventario al catálogo usado por el frontend actual.
UPDATE item_inventario AS item
SET nombre = cambios.nuevo
FROM (VALUES
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
) AS cambios(anterior, nuevo)
WHERE item.nombre = cambios.anterior
  AND NOT EXISTS (
      SELECT 1 FROM item_inventario existente
      WHERE existente.nombre = cambios.nuevo
  );

-- Restricciones de unicidad requeridas por el backend y por el seed idempotente.
-- Si existen duplicados, estos CREATE UNIQUE INDEX se detendrán sin borrar datos;
-- revisa primero 00_preflight_existing.sql.
CREATE UNIQUE INDEX IF NOT EXISTS ux_vehiculo_tarjeta_gasolina
ON vehiculo (num_tarjeta_gasolina)
WHERE num_tarjeta_gasolina IS NOT NULL AND btrim(num_tarjeta_gasolina) <> '';

CREATE UNIQUE INDEX IF NOT EXISTS ux_regreso_salida_unico
ON regreso (salida_id);

CREATE UNIQUE INDEX IF NOT EXISTS ux_resguardo_salida_unico
ON resguardo (salida_id);

CREATE UNIQUE INDEX IF NOT EXISTS ux_item_condicion_nombre
ON item_condicion (nombre);

CREATE UNIQUE INDEX IF NOT EXISTS ux_item_inventario_nombre
ON item_inventario (nombre);

CREATE UNIQUE INDEX IF NOT EXISTS ux_revision_condicion_salida_item
ON revision_condicion (salida_id, item_condicion_id);

CREATE UNIQUE INDEX IF NOT EXISTS ux_revision_inventario_salida_item
ON revision_inventario (salida_id, item_id);

-- Recupera el capturador de gastos históricos cuando la salida lo permite.
UPDATE gasto_gasolina g
SET capturado_por = s.capturado_por
FROM salida s
WHERE g.salida_id = s.id
  AND g.capturado_por IS NULL;
