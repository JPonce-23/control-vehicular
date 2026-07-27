--SE MODIFICA LA TABLA VEHICULO PUES NO ES RELEVANTE EN NUMERO ECONOMICO Y TAMPOCO REQUERIDO

ALTER TABLE vehiculo
ALTER COLUMN num_economico DROP NOT NULL;

ALTER TABLE vehiculo
DROP CONSTRAINT vehiculo_num_economico_key;

SELECT conname
FROM pg_constraint
WHERE conrelid = 'vehiculo'::regclass;


-- ============================================
-- ALTERACIONES PARA MÓDULO DE GASTOS DE GASOLINA
-- ============================================

ALTER TABLE gasto_gasolina
ADD COLUMN IF NOT EXISTS nivel_tanque nivel_gasolina_salida,
ADD COLUMN IF NOT EXISTS km_odometro DECIMAL(10,2),
ADD COLUMN IF NOT EXISTS capturado_por INT REFERENCES usuario_sistema(id),
ADD COLUMN IF NOT EXISTS fecha_registro TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP;

-- Evita duplicar presupuesto por vehículo y año
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'presupuesto_gasolina_vehiculo_anio_unique'
    ) THEN
        ALTER TABLE presupuesto_gasolina
        ADD CONSTRAINT presupuesto_gasolina_vehiculo_anio_unique
        UNIQUE (vehiculo_id, anio);
    END IF;
END $$;

-- Índices para consultas y reportes
CREATE INDEX IF NOT EXISTS idx_gasto_gasolina_vehiculo
ON gasto_gasolina (vehiculo_id);

CREATE INDEX IF NOT EXISTS idx_gasto_gasolina_fecha
ON gasto_gasolina (fecha_gasto);

CREATE INDEX IF NOT EXISTS idx_gasto_gasolina_presupuesto
ON gasto_gasolina (presupuesto_id);

CREATE INDEX IF NOT EXISTS idx_salida_vehiculo
ON salida (vehiculo_id);

CREATE INDEX IF NOT EXISTS idx_regreso_salida
ON regreso (salida_id);

-- ====================================
-- Se quita el NOT NULL de la tabla gasto_gasolina
-- ====================================

ALTER TABLE gasto_gasolina
ALTER COLUMN litros DROP NOT NULL;


-- ===================================
-- Se altera la tabla de presupuesto para que el administrador pueda definir
-- el mes de inicio y de fin en el presupuesto
-- ===================================
ALTER TABLE presupuesto_gasolina
ADD COLUMN mes_inicio INT NOT NULL DEFAULT 1,
ADD COLUMN mes_fin INT NOT NULL DEFAULT 12;


-- ===================================
-- Se altera la tabla gasto_gasolina 
-- para que el id de la salida sea obligatorio
-- ===================================

DELETE FROM gasto_gasolina;

ALTER TABLE gasto_gasolina
ALTER COLUMN salida_id SET NOT NULL;


--====================================
-- Se altera vehiculo para que numero economico no sea obligatorio
-- pues no se usa al registrar el vehículo
--====================================

ALTER TABLE vehiculo
ALTER COLUMN num_economico DROP NOT NULL;


-- ==================================
-- Se modifica tabla persona_autorizada ya que el usuario
-- no registra de forma obligatoria datos de la licencia
-- ==================================

ALTER TABLE persona_autorizada ALTER COLUMN num_licencia DROP NOT NULL;
ALTER TABLE persona_autorizada ALTER COLUMN vigencia_licencia DROP NOT NULL;
ALTER TABLE persona_autorizada ALTER COLUMN tipo_licencia DROP NOT NULL;


-- ================================
-- Se agrega el cargo a usuario y no al viaje
-- ================================

ALTER TABLE persona_autorizada
ADD COLUMN IF NOT EXISTS cargo VARCHAR(150);


UPDATE persona_autorizada p
SET cargo = COALESCE(
    (
        SELECT s.cargo_en_viaje
        FROM salida s
        WHERE s.persona_id = p.id
        ORDER BY s.fecha_salida DESC
        LIMIT 1
    ),
    'Pendiente por definir'
)
WHERE p.cargo IS NULL;


ALTER TABLE persona_autorizada
ALTER COLUMN cargo SET NOT NULL;



ALTER TABLE salida
ADD COLUMN IF NOT EXISTS fecha_regreso_estimada DATE;

ALTER TABLE vehiculo
ADD COLUMN IF NOT EXISTS saldo_tarjeta_gasolina DECIMAL(10,2) NOT NULL DEFAULT 0;

ALTER TABLE salida
ADD COLUMN IF NOT EXISTS monto_agregado_tarjeta DECIMAL(10,2) NOT NULL DEFAULT 0,
ADD COLUMN IF NOT EXISTS saldo_tarjeta_salida DECIMAL(10,2) NOT NULL DEFAULT 0;

ALTER TABLE regreso
ADD COLUMN IF NOT EXISTS saldo_tarjeta_antes_regreso DECIMAL(10,2),
ADD COLUMN IF NOT EXISTS saldo_tarjeta_regreso DECIMAL(10,2),
ADD COLUMN IF NOT EXISTS monto_gastado_tarjeta DECIMAL(10,2);