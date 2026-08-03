-- Crea o repara el superadministrador por CORREO, sin depender del ID 1.
-- Correo: superadmin@admin.com
-- Contraseña temporal inicial: PasswordSuperadmin123
-- Cambiarla inmediatamente después del primer acceso.

ALTER TABLE usuario_sistema
ADD COLUMN IF NOT EXISTS es_superadmin BOOLEAN NOT NULL DEFAULT FALSE;

DO $$
DECLARE
    superadmin_id INT;
    coincidencias INT;
BEGIN
    SELECT COUNT(DISTINCT id) INTO coincidencias
    FROM usuario_sistema
    WHERE es_superadmin = TRUE
       OR correo = 'superadmin@admin.com'
       OR num_empleado = 'SUPERADMIN';

    IF coincidencias > 1 THEN
        RAISE EXCEPTION 'Existen dos cuentas distintas usando el correo o número de empleado del superadmin. Revísalas antes de continuar.';
    END IF;

    SELECT id INTO superadmin_id
    FROM usuario_sistema
    WHERE es_superadmin = TRUE
       OR correo = 'superadmin@admin.com'
       OR num_empleado = 'SUPERADMIN'
    ORDER BY es_superadmin DESC, id
    LIMIT 1;

    IF superadmin_id IS NULL THEN
        INSERT INTO usuario_sistema (
            nombre, apellido_paterno, apellido_materno,
            num_empleado, correo, contrasena_hash,
            rol, estado, es_superadmin, fecha_alta
        ) VALUES (
            'Super', 'Admin', NULL,
            'SUPERADMIN', 'superadmin@admin.com',
            '$2b$12$tgXzHwAEiNpNYwFNE9HQueorP02TldeBoVfEiGGmwevxS/8xL7Ub6',
            'administrador', 'activo', TRUE, CURRENT_TIMESTAMP
        )
        RETURNING id INTO superadmin_id;
    ELSE
        UPDATE usuario_sistema
        SET nombre = 'Super',
            apellido_paterno = 'Admin',
            num_empleado = 'SUPERADMIN',
            correo = 'superadmin@admin.com',
            contrasena_hash = '$2b$12$tgXzHwAEiNpNYwFNE9HQueorP02TldeBoVfEiGGmwevxS/8xL7Ub6',
            rol = 'administrador',
            estado = 'activo',
            es_superadmin = TRUE
        WHERE id = superadmin_id;
    END IF;

    UPDATE usuario_sistema
    SET es_superadmin = FALSE
    WHERE id <> superadmin_id AND es_superadmin = TRUE;
END $$;

CREATE UNIQUE INDEX IF NOT EXISTS ux_usuario_superadmin_unico
ON usuario_sistema (es_superadmin)
WHERE es_superadmin = TRUE;

SELECT id, correo, rol, estado, es_superadmin
FROM usuario_sistema
WHERE correo = 'superadmin@admin.com';
