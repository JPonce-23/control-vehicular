from datetime import datetime, timedelta, timezone
import hashlib
import secrets

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.token_model import TokenAcceso
from app.models.usuario_model import UsuarioSistema
from app.schemas.usuario_schema import LoginRequest, RecuperarPasswordRequest, ResetPasswordRequest
from app.services.auth_service import crear_token_acceso, generar_hash_password, verificar_password
from app.services.email_service import enviar_correo_recuperacion, smtp_configurado

router = APIRouter(prefix="/auth", tags=["Autenticación"])


def _ahora_utc_sin_zona() -> datetime:
    # PostgreSQL usa TIMESTAMP sin zona en este esquema.
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _validar_nueva_password(password: str) -> None:
    if len(password) < 10:
        raise HTTPException(status_code=400, detail="La contraseña debe tener al menos 10 caracteres")


@router.post("/login")
def login(datos: LoginRequest, db: Session = Depends(get_db)):
    correo = datos.correo.strip().lower()
    usuario = db.query(UsuarioSistema).filter(UsuarioSistema.correo == correo).first()
    if usuario is None or not verificar_password(datos.password, usuario.contrasena_hash):
        raise HTTPException(status_code=401, detail="Correo o contraseña incorrectos")
    if usuario.estado != "activo":
        raise HTTPException(status_code=403, detail="Usuario suspendido")

    usuario.ultimo_acceso = _ahora_utc_sin_zona()
    db.commit()

    token = crear_token_acceso({"sub": str(usuario.id)})
    return {
        "access_token": token,
        "token_type": "bearer",
        "usuario": {
            "id": usuario.id,
            "nombre": usuario.nombre,
            "rol": usuario.rol,
            "es_superadmin": bool(usuario.es_superadmin),
        },
    }


@router.post("/recuperar-password")
def recuperar_password(datos: RecuperarPasswordRequest, db: Session = Depends(get_db)):
    mensaje_generico = "Si el correo está registrado, recibirás instrucciones para recuperar la contraseña"
    if not smtp_configurado():
        raise HTTPException(status_code=503, detail="La recuperación por correo no está configurada")

    usuario = db.query(UsuarioSistema).filter(
        UsuarioSistema.correo == datos.correo.strip().lower()
    ).first()
    if usuario is None:
        return {"mensaje": mensaje_generico}

    token = secrets.token_urlsafe(32)
    db.query(TokenAcceso).filter(
        TokenAcceso.usuario_id == usuario.id,
        TokenAcceso.tipo == "recuperacion",
        TokenAcceso.usado.is_(False),
    ).update({TokenAcceso.usado: True}, synchronize_session=False)
    nuevo_token = TokenAcceso(
        usuario_id=usuario.id,
        token=_hash_token(token),
        tipo="recuperacion",
        fecha_expiracion=_ahora_utc_sin_zona() + timedelta(minutes=5),
        usado=False,
    )
    db.add(nuevo_token)
    try:
        enviar_correo_recuperacion(usuario.correo, token)
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=503, detail="No fue posible enviar el correo de recuperación")
    return {"mensaje": mensaje_generico}


@router.post("/reset-password")
def reset_password(datos: ResetPasswordRequest, db: Session = Depends(get_db)):
    _validar_nueva_password(datos.nueva_password)
    usuario = db.query(UsuarioSistema).filter(
        UsuarioSistema.correo == datos.correo.strip().lower()
    ).first()
    if usuario is None:
        raise HTTPException(status_code=400, detail="Token inválido o ya utilizado")

    token_db = db.query(TokenAcceso).filter(
        TokenAcceso.usuario_id == usuario.id,
        TokenAcceso.token == _hash_token(datos.token),
        TokenAcceso.tipo == "recuperacion",
        TokenAcceso.usado.is_(False),
    ).first()
    if token_db is None or token_db.fecha_expiracion < _ahora_utc_sin_zona():
        raise HTTPException(status_code=400, detail="Token inválido, utilizado o expirado")

    usuario.contrasena_hash = generar_hash_password(datos.nueva_password)
    db.query(TokenAcceso).filter(
        TokenAcceso.usuario_id == usuario.id,
        TokenAcceso.tipo == "recuperacion",
        TokenAcceso.usado.is_(False),
    ).update({TokenAcceso.usado: True}, synchronize_session=False)
    db.commit()
    return {"mensaje": "Contraseña actualizada correctamente"}
