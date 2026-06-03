from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.usuario_model import UsuarioSistema
from app.schemas.usuario_schema import LoginRequest
from app.services.auth_service import verificar_password, crear_token_acceso

router = APIRouter(
    prefix="/auth",
    tags=["Autenticación"]
)

@router.post("/login")
def login(datos: LoginRequest, db: Session = Depends(get_db)):
    usuario = db.query(UsuarioSistema).filter(
        UsuarioSistema.correo == datos.correo
    ).first()

    if usuario is None:
        raise HTTPException(
            status_code=401,
            detail="Correo o contraseña incorrectos"
        )

    if not verificar_password(datos.password, usuario.contrasena_hash):
        raise HTTPException(
            status_code=401,
            detail="Correo o contraseña incorrectos"
        )

    token = crear_token_acceso({
    "sub": str(usuario.id),
    "correo": usuario.correo,
    "rol": usuario.rol
})

    return {
        "access_token": token,
        "token_type": "bearer",
        "usuario": {
            "id": usuario.id,
            "nombre": usuario.nombre,
            "rol": usuario.rol
        }
    }