# Checklist para el nuevo despliegue

## Antes de desplegar

- [ ] Respaldar la base de datos anterior.
- [ ] Elegir una sola ruta: instalación nueva o migración existente.
- [ ] Para una base existente, ejecutar `database/00_preflight_existing.sql` y resolver duplicados antes de migrar.
- [ ] Ejecutar `database/07_verify_deploy.sql` sin resultados inesperados.
- [ ] Crear `.env`/variables de plataforma con una `SECRET_KEY` nueva.
- [ ] Configurar `CORS_ORIGINS` con el origen exacto del frontend.
- [ ] Confirmar que `pip install -r requirements.txt` termina sin instalaciones manuales.
- [ ] No incluir `.git`, `venv`, `.env`, `__pycache__` ni archivos generados.

## Pruebas del backend

- [ ] `GET /health` devuelve `status: ok`.
- [ ] `/docs` muestra una sola copia de cada ruta.
- [ ] Login del superadmin devuelve 200.
- [ ] Un usuario suspendido no puede iniciar sesión ni seguir usando un token anterior.
- [ ] `/tokens/` no está publicado.
- [ ] Crear ajuste de odómetro exige administrador y toma el usuario desde el token.

## Pruebas funcionales

- [ ] Registrar una persona crea exactamente una fila, recarga y muestra “Registro completado”.
- [ ] El botón Dar de baja/Reactivar aparece y cambia el estado sin borrar historial.
- [ ] Registrar vehículo muestra número de tarjeta en la tabla.
- [ ] Registrar salida funciona sin área ni hora y guarda forma `provisional`.
- [ ] Registrar regreso muestra solo fecha; saldo final de tarjeta es opcional.
- [ ] Un vehículo dañado no vuelve automáticamente a disponible.
- [ ] Presupuesto muestra vehículos fuera de servicio para consulta histórica.
- [ ] Un vehículo fuera de servicio no recibe un presupuesto nuevo.
- [ ] Gasto de gasolina recarga con mensaje y no excede el presupuesto.
- [ ] Los títulos de tabla aparecen centrados.
- [ ] Generar resguardo funciona aun sin plantilla institucional, usando el formato básico.

## Después del despliegue

- [ ] Cambiar inmediatamente `PasswordSuperadmin123`.
- [ ] Verificar consola del navegador y Network sin 404, 422, 500 ni errores CORS.
- [ ] Probar desde una sesión de administrador y otra de capturista.
- [ ] Confirmar persistencia de resguardos tras reiniciar el servicio.
