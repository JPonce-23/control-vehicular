from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.usuario_model import UsuarioSistema
from app.schemas.usuario_schema import UsuarioResponse, UsuarioCreate, UsuarioRolUpdate, UsuarioEstadoUpdate
from app.services.auth_service import obtener_usuario_actual, requerir_rol, generar_hash_password

router = APIRouter(
    prefix="/usuarios",
    tags=["Usuarios"]
)

@router.get("/", response_model=list[UsuarioResponse])
def listar_usuarios(
    db: Session = Depends(get_db),
    usuario_actual = Depends(obtener_usuario_actual)
):
    return db.query(UsuarioSistema).all()

@router.get("/{usuario_id}", response_model=UsuarioResponse)
def obtener_usuario_por_id(
    usuario_id: int,
    db: Session = Depends(get_db),
    usuario_actual = Depends(obtener_usuario_actual)
):
    usuario = db.query(UsuarioSistema).filter(
        UsuarioSistema.id == usuario_id
    ).first()

    if usuario is None:
        raise HTTPException(
            status_code=404,
            detail="Usuario no encontrado"
        )

    return usuario

@router.post("/", response_model=UsuarioResponse)
def crear_usuario(
    usuario: UsuarioCreate,
    db: Session = Depends(get_db),
    usuario_actual = Depends(requerir_rol(["administrador"]))
):
    usuario_existente = db.query(UsuarioSistema).filter(
        (UsuarioSistema.correo == usuario.correo) |
        (UsuarioSistema.num_empleado == usuario.num_empleado)
    ).first()

    if usuario_existente:
        raise HTTPException(
            status_code=400,
            detail="El correo o número de empleado ya está registrado"
        )

    nuevo_usuario = UsuarioSistema(
        nombre=usuario.nombre,
        apellido_paterno=usuario.apellido_paterno,
        apellido_materno=usuario.apellido_materno,
        num_empleado=usuario.num_empleado,
        correo=usuario.correo,
        contrasena_hash=generar_hash_password(usuario.password),
        rol=usuario.rol,
        estado=usuario.estado
    )

    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)

    return nuevo_usuario


@router.put("/{usuario_id}/rol")
def actualizar_rol_usuario(
    usuario_id: int,
    datos: UsuarioRolUpdate,
    db: Session = Depends(get_db),
    usuario_actual = Depends(requerir_rol(["administrador"]))
):
    roles_permitidos = ["administrador", "capturista"]

    if datos.rol not in roles_permitidos:
        raise HTTPException(
            status_code=400,
            detail="Rol de usuario no válido"
        )

    usuario = db.query(UsuarioSistema).filter(
        UsuarioSistema.id == usuario_id
    ).first()

    if usuario is None:
        raise HTTPException(
            status_code=404,
            detail="Usuario no encontrado"
        )

    usuario.rol = datos.rol

    db.commit()
    db.refresh(usuario)

    return {
        "mensaje": "Rol actualizado correctamente",
        "usuario_id": usuario.id,
        "rol": usuario.rol
    }
    
@router.patch("/{usuario_id}/estado")
def actualizar_estado_usuario(
    usuario_id: int,
    datos: UsuarioEstadoUpdate,
    db: Session = Depends(get_db),
    usuario_actual = Depends(requerir_rol(["administrador"]))
):
    estados_permitidos = ["activo", "suspendido"]

    if datos.estado not in estados_permitidos:
        raise HTTPException(status_code=400, detail="Estado de usuario no válido")

    usuario = db.query(UsuarioSistema).filter(UsuarioSistema.id == usuario_id).first()

    if usuario is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    usuario.estado = datos.estado
    db.commit()
    db.refresh(usuario)

    return {
        "mensaje": "Estado actualizado correctamente",
        "usuario_id": usuario.id,
        "estado": usuario.estado
    }