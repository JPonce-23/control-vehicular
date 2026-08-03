-- Correcciones funcionales del nuevo despliegue. Seguro para volver a ejecutar.
ALTER TABLE salida ALTER COLUMN area_en_viaje DROP NOT NULL;
ALTER TABLE salida ALTER COLUMN forma_movimiento SET DEFAULT 'provisional';
ALTER TABLE regreso ALTER COLUMN fecha_regreso SET DEFAULT CURRENT_TIMESTAMP;
