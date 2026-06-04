from datetime import datetime, timedelta
import secrets
from app.models.token_model import TokenAcceso
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.usuario_model import UsuarioSistema
from app.schemas.usuario_schema import LoginRequest, RecuperarPasswordRequest, ResetPasswordRequest
from app.services.auth_service import verificar_password, crear_token_acceso, generar_hash_password
from app.services.email_service import enviar_correo_recuperacion


router = APIRouter(
    prefix="/auth",
    tags=["Autenticación"]
)

@router.post("/login")
def login(datos: LoginRequest, db: Session = Depends(get_db)):
    usuario = db.query(
        UsuarioSistema).filter(
        UsuarioSistema.correo == datos.correo
    ).first()

    if usuario is None:
        raise HTTPException(
            status_code=401,
            detail="Correo o contraseña incorrectos"
        )
        
    if usuario.estado != "activo":
        raise HTTPException(
            status_code=403,
            detail="Usuario suspendido"
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
    
@router.post("/recuperar-password")
def recuperar_password(
    datos: RecuperarPasswordRequest,
    db: Session = Depends(get_db)
):
    usuario = db.query(UsuarioSistema).filter(
        UsuarioSistema.correo == datos.correo
    ).first()

    if usuario is None:
        raise HTTPException(
            status_code=404,
            detail="No existe un usuario con ese correo"
        )

    token = secrets.token_urlsafe(32)

    nuevo_token = TokenAcceso(
        usuario_id=usuario.id,
        token=token,
        tipo="recuperacion",
        fecha_expiracion=datetime.utcnow() + timedelta(minutes=5),
        usado=False
    )

    db.add(nuevo_token)
    db.commit()

    enviar_correo_recuperacion(usuario.correo, token)

    return {
        "mensaje": "Se envió un correo con instrucciones para recuperar la contraseña"
    }
    
@router.post("/reset-password")
def reset_password(
    datos: ResetPasswordRequest,
    db: Session = Depends(get_db)
):
    usuario = db.query(UsuarioSistema).filter(
        UsuarioSistema.correo == datos.correo
    ).first()

    if usuario is None:
        raise HTTPException(
            status_code=404,
            detail="Usuario no encontrado"
        )

    token_db = db.query(TokenAcceso).filter(
        TokenAcceso.usuario_id == usuario.id,
        TokenAcceso.token == datos.token,
        TokenAcceso.tipo == "recuperacion",
        TokenAcceso.usado == False
    ).first()

    if token_db is None:
        raise HTTPException(
            status_code=400,
            detail="Token inválido o ya utilizado"
        )

    if token_db.fecha_expiracion < datetime.utcnow():
        raise HTTPException(
            status_code=400,
            detail="El token ha expirado"
        )

    usuario.contrasena_hash = generar_hash_password(datos.nueva_password)
    token_db.usado = True

    db.commit()

    return {
        "mensaje": "Contraseña actualizada correctamente"
    }