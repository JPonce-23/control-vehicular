--SE MODIFICA LA TABLA VEHICULO PUES NO ES RELEVANTE EN NUMERO ECONOMICO Y TAMPOCO REQUERIDO

ALTER TABLE vehiculo
ALTER COLUMN num_economico DROP NOT NULL;

ALTER TABLE vehiculo
DROP CONSTRAINT vehiculo_num_economico_key;

SELECT conname
FROM pg_constraint
WHERE conrelid = 'vehiculo'::regclass;