import os, secrets, string
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.usuario_model import UsuarioSistema
from app.schemas.usuario_schema import UsuarioResponse, UsuarioCreate, UsuarioRolUpdate, UsuarioEstadoUpdate, UsuarioUpdate, CambiarPasswordRequest
from app.services.auth_service import obtener_usuario_actual, requerir_rol, generar_hash_password, verificar_password 



SUPERADMIN_ID = int(os.getenv("SUPERADMIN_ID", 1))

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
        rol="capturista",
        estado="activo"
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
        
    if usuario.id == SUPERADMIN_ID:
        raise HTTPException(
            status_code=400,
            detail="No se puede modificar el rol del superadministrador"
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
    
    if usuario.id == SUPERADMIN_ID:
        raise HTTPException(
            status_code=400,
            detail="No se puede modificar el rol del superadministrador"
        )

    usuario.estado = datos.estado
    db.commit()
    db.refresh(usuario)

    return {
        "mensaje": "Estado actualizado correctamente",
        "usuario_id": usuario.id,
        "estado": usuario.estado
    }
    
@router.put("/{usuario_id}", response_model=UsuarioResponse)
def actualizar_usuario(
    usuario_id: int,
    datos: UsuarioUpdate,
    db: Session = Depends(get_db),
    usuario_actual = Depends(requerir_rol(["administrador"]))
):
    usuario = db.query(UsuarioSistema).filter(
        UsuarioSistema.id == usuario_id
    ).first()

    if usuario is None:
        raise HTTPException(
            status_code=404,
            detail="Usuario no encontrado"
        )

    datos_actualizar = datos.model_dump(exclude_unset=True)

    if "correo" in datos_actualizar or "num_empleado" in datos_actualizar:
        usuario_existente = db.query(UsuarioSistema).filter(
            UsuarioSistema.id != usuario_id,
            (
                (UsuarioSistema.correo == datos_actualizar.get("correo")) |
                (UsuarioSistema.num_empleado == datos_actualizar.get("num_empleado"))
            )
        ).first()

        if usuario_existente:
            raise HTTPException(
                status_code=400,
                detail="El correo o número de empleado ya está registrado"
            )

    for campo, valor in datos_actualizar.items():
        setattr(usuario, campo, valor)

    db.commit()
    db.refresh(usuario)

    return usuario

@router.patch("/{usuario_id}/reset-password")
def reset_password_admin(
    usuario_id: int,
    db: Session = Depends(get_db),
    usuario_actual = Depends(requerir_rol(["administrador"]))
):
    usuario = db.query(UsuarioSistema).filter(
        UsuarioSistema.id == usuario_id
    ).first()

    if usuario is None:
        raise HTTPException(
            status_code=404,
            detail="Usuario no encontrado"
        )
        
    if usuario.id == SUPERADMIN_ID:
        raise HTTPException(
            status_code=400,
            detail="No se puede generar contraseña temporal para el superadministrador"
        )

    caracteres = string.ascii_letters + string.digits
    password_temporal = "Temp-" + "".join(
        secrets.choice(caracteres) for _ in range(8)
    )

    usuario.contrasena_hash = generar_hash_password(password_temporal)

    db.commit()

    return {
        "mensaje": "Contraseña temporal generada correctamente",
        "usuario_id": usuario.id,
        "password_temporal": password_temporal
    }
    
@router.patch("/me/password")
def cambiar_mi_password(
    datos: CambiarPasswordRequest,
    db: Session = Depends(get_db),
    usuario_actual = Depends(obtener_usuario_actual)
):
    if not verificar_password(
        datos.password_actual,
        usuario_actual.contrasena_hash
    ):
        raise HTTPException(
            status_code=400,
            detail="La contraseña actual no es correcta"
        )

    usuario_actual.contrasena_hash = generar_hash_password(datos.nueva_password)

    db.commit()

    return {
        "mensaje": "Contraseña actualizada correctamente"
    }