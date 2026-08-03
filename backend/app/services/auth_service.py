from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.models.usuario_model import UsuarioSistema

settings = get_settings()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = HTTPBearer()


def verificar_password(password_plano: str, password_hash: str) -> bool:
    try:
        return pwd_context.verify(password_plano, password_hash)
    except (ValueError, TypeError):
        return False


def generar_hash_password(password: str) -> str:
    return pwd_context.hash(password)


def crear_token_acceso(data: dict) -> str:
    settings.validate_auth()
    datos = data.copy()
    expiracion = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes
    )
    datos.update({"exp": expiracion})
    return jwt.encode(datos, settings.secret_key, algorithm=settings.algorithm)


def obtener_usuario_actual(
    credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    settings.validate_auth()
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.secret_key,
            algorithms=[settings.algorithm],
        )
        usuario_id = payload.get("sub")
        if usuario_id is None:
            raise HTTPException(status_code=401, detail="Token inválido")
        usuario_id = int(usuario_id)
    except (JWTError, TypeError, ValueError):
        raise HTTPException(status_code=401, detail="Token inválido o expirado")

    usuario = db.query(UsuarioSistema).filter(UsuarioSistema.id == usuario_id).first()
    if usuario is None:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")
    if usuario.estado != "activo":
        raise HTTPException(status_code=403, detail="Usuario suspendido")
    return usuario


def requerir_rol(roles_permitidos: list[str]):
    def validar_rol(usuario_actual=Depends(obtener_usuario_actual)):
        if usuario_actual.rol not in roles_permitidos:
            raise HTTPException(
                status_code=403,
                detail="No tienes permisos para realizar esta acción",
            )
        return usuario_actual

    return validar_rol
