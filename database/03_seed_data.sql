INSERT INTO item_condicion (nombre) VALUES
('carroceria'),
('pintura'),
('vestidura'),
('direccion'),
('motor'),
('sistema_electrico'),
('sistema_encendido'),
('sistema_frenos'),
('sistema_suspension'),
('sistema_transmision');

INSERT INTO item_inventario (nombre, categoria, estado_default) VALUES
('tapon_gas', 'pieza', 'correcto'),          ('estereo', 'pieza', 'correcto'),            ('calefaccion', 'pieza', 'correcto'),        ('aire_acond', 'pieza', 'correcto'),             ('consola_bateria_auxiliar', 'equipo_especial', 'na'),
('tapon_radiador', 'pieza', 'correcto'),     ('radio_amfm', 'pieza', 'correcto'),         ('cenicero', 'pieza', 'correcto'),           ('jgo_herramientas', 'pieza', 'correcto'),       ('radio_trans_antena', 'equipo_especial', 'na'),
('tapon_aceite', 'pieza', 'correcto'),       ('antena', 'pieza', 'correcto'),             ('encendedor', 'pieza', 'na'),               ('extinguidor', 'pieza', 'correcto'),            ('estrobos_faros_calaveras', 'equipo_especial', 'na'),
('tapones_rines', 'pieza', 'correcto'),      ('alarma', 'pieza', 'correcto'),             ('visera_derecha', 'pieza', 'correcto'),     ('bayoneta', 'pieza', 'correcto'),               ('camara_frontal_trasera', 'equipo_especial', 'na'),
('emblemas', 'pieza', 'correcto'),           ('llave_puertas', 'pieza', 'na'),            ('visera_izquierda', 'pieza', 'correcto'),   ('bateria', 'pieza', 'correcto'),                ('tumbaburros_sirena_altavoz', 'equipo_especial', 'na'),
('parrillas', 'pieza', 'correcto'),          ('llave_tapon_gas', 'pieza', 'na'),          ('cinturon_seg', 'pieza', 'correcto'),       ('jgo_placas', 'pieza', 'correcto'),             ('sistema_grabacion', 'equipo_especial', 'na'),
('limpiadores', 'pieza', 'correcto'),        ('llave_cajuela', 'pieza', 'na'),            ('tapetes', 'pieza', 'correcto'),            ('tarjeta_circulacion', 'pieza', 'correcto'),    
('espejo_lat_izq', 'pieza', 'correcto'),     ('llave_guantera', 'pieza', 'na'),           ('alfombra_cajuela', 'pieza', 'correcto'),   ('poliza_seguro', 'pieza', 'correcto'),          
('espejo_lat_der', 'pieza', 'correcto'),     ('llave_encendido', 'pieza', 'correcto'),    ('llanta_refaccion', 'pieza', 'correcto'),   ('poliza_servicio', 'pieza', 'correcto'),        
('espejo_retrovisor', 'pieza', 'correcto'),  ('sistema_alarma', 'pieza', 'na'),           ('gato', 'pieza', 'correcto'),               ('verificacion', 'pieza', 'correcto'),           
('llantas', 'pieza', 'correcto'),            ('seguro_aletas', 'pieza', 'na'),            ('llave_birlos', 'pieza', 'correcto'),       ('revista_vehi', 'pieza', 'correcto'),         
('claxon', 'pieza', 'correcto'),             ('seguro_puertas', 'pieza', 'na'),           ('defroster', 'pieza', 'correcto'),          ('reflejantes', 'pieza', 'correcto');




--PRUEBA DE EL FLUJO MÍNIMO PARA VALIDAR RELACIONES
INSERT INTO usuario_sistema (nombre, apellido_paterno, num_empleado, correo, contrasena_hash, rol, estado) VALUES
('Admin1', 'prueba', '000001', 'admin.prueba@prueba.com', '123456', 'administrador', 'activo');


INSERT INTO persona_autorizada (nombre, apellido_paterno, num_licencia, vigencia_licencia, tipo_licencia, estado) VALUES
('Persona1', 'prueba', '000001', '2030-08-02', 'A', 'activo');

INSERT INTO vehiculo (placa, marca, tipo, modelo_anio, cilindros, num_serie, color, km_acumulado, estado) VALUES
('NWS681C', 'NISSAN FRONTIER', 'CAMIONETA 4X2', 2026, 4, '3N6AD33AXTK821924','BLANCA', 354.87, 'disponible');

INSERT INTO salida (vehiculo_id, persona_id, capturado_por, cargo_en_viaje, area_en_viaje, tipo_movimiento, forma_movimiento, finalidad_uso, km_odometro_salida, nivel_gasolina_salida, estado_llantas_salida)
VALUES
(1, 1, 1, 'Salida', 'Area salida', 'asignacion', 'provisional', 'Viaje', 354.87, 'lleno', 'lleno');

INSERT INTO revision_condicion (salida_id, item_condicion_id, estado) VALUES
(1, 1, 'bueno');

INSERT INTO revision_inventario (salida_id, item_id, estado) VALUES 
(1, 1, 'correcto');

INSERT INTO presupuesto_gasolina (vehiculo_id, monto_autorizado_total, monto_por_mes, monto_utilizado, saldo_acumulado, anio) VALUES
(1, 10578.00, 824.50, 6850.00, 3737.00, 2026);

INSERT INTO gasto_gasolina (vehiculo_id, salida_id, presupuesto_id, fecha_gasto, litros, monto, nota) VALUES 
(1, 1, 1, CURRENT_DATE, 45.50, 1248.90, 'Carga de gasolina para salida de prueba');

INSERT INTO regreso (salida_id, capturado_por, km_odometro_regreso, nivel_gasolina_regreso, estado_llantas_regreso, estado_vehiculo_regreso, finalidad_devolucion, observaciones) 
VALUES 
(1, 1, 412.50, 'medio', 'medio', 'bueno', 'disponible', 'Regreso de prueba sin incidencias');

SELECT * FROM regreso;

INSERT INTO resguardo (salida_id, nombre_archivo, ruta_archivo) VALUES 
(1, 'resguardo_salida_1.docx', 'archivos/resguardos/resguardo_salida_1.docx');

SELECT * FROM resguardo;

INSERT INTO ajuste_odometro (vehiculo_id, km_anterior, km_nuevo, motivo, realizado_por) VALUES 
(1, 412.50, 415.00, 'Ajuste de prueba por corrección manual', 1);

SELECT * FROM ajuste_odometro;
