import secrets
import string

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.usuario_model import UsuarioSistema
from app.schemas.usuario_schema import (
    CambiarPasswordRequest,
    UsuarioCreate,
    UsuarioEstadoUpdate,
    UsuarioResponse,
    UsuarioRolUpdate,
    UsuarioUpdate,
)
from app.services.auth_service import (
    generar_hash_password,
    obtener_usuario_actual,
    requerir_rol,
    verificar_password,
)

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])


def _obtener_usuario_o_404(db: Session, usuario_id: int) -> UsuarioSistema:
    usuario = db.query(UsuarioSistema).filter(UsuarioSistema.id == usuario_id).first()
    if usuario is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario


def _proteger_superadmin(usuario: UsuarioSistema) -> None:
    if usuario.es_superadmin:
        raise HTTPException(
            status_code=400,
            detail="No se puede modificar la cuenta del superadministrador desde esta operación",
        )


def _validar_password(password: str) -> None:
    if len(password) < 10:
        raise HTTPException(
            status_code=400,
            detail="La contraseña debe tener al menos 10 caracteres",
        )


@router.get("/", response_model=list[UsuarioResponse])
def listar_usuarios(
    db: Session = Depends(get_db),
    usuario_actual=Depends(requerir_rol(["administrador"])),
):
    return db.query(UsuarioSistema).order_by(UsuarioSistema.id).all()


@router.get("/me", response_model=UsuarioResponse)
def obtener_mi_usuario(usuario_actual=Depends(obtener_usuario_actual)):
    return usuario_actual


@router.patch("/me/password")
def cambiar_mi_password(
    datos: CambiarPasswordRequest,
    db: Session = Depends(get_db),
    usuario_actual=Depends(obtener_usuario_actual),
):
    if not verificar_password(datos.password_actual, usuario_actual.contrasena_hash):
        raise HTTPException(status_code=400, detail="La contraseña actual no es correcta")
    _validar_password(datos.nueva_password)
    usuario_actual.contrasena_hash = generar_hash_password(datos.nueva_password)
    db.commit()
    return {"mensaje": "Contraseña actualizada correctamente"}


@router.get("/{usuario_id}", response_model=UsuarioResponse)
def obtener_usuario_por_id(
    usuario_id: int,
    db: Session = Depends(get_db),
    usuario_actual=Depends(requerir_rol(["administrador"])),
):
    return _obtener_usuario_o_404(db, usuario_id)


@router.post("/", response_model=UsuarioResponse, status_code=201)
def crear_usuario(
    usuario: UsuarioCreate,
    db: Session = Depends(get_db),
    usuario_actual=Depends(requerir_rol(["administrador"])),
):
    _validar_password(usuario.password)
    nombre = usuario.nombre.strip()
    apellido_paterno = usuario.apellido_paterno.strip()
    num_empleado = usuario.num_empleado.strip()
    correo = usuario.correo.strip().lower()
    if not all((nombre, apellido_paterno, num_empleado, correo)):
        raise HTTPException(status_code=400, detail="Nombre, apellido, número de empleado y correo son obligatorios")

    usuario_existente = db.query(UsuarioSistema).filter(
        or_(
            UsuarioSistema.correo == correo,
            UsuarioSistema.num_empleado == num_empleado,
        )
    ).first()
    if usuario_existente:
        raise HTTPException(
            status_code=409,
            detail="El correo o número de empleado ya está registrado",
        )

    nuevo_usuario = UsuarioSistema(
        nombre=nombre,
        apellido_paterno=apellido_paterno,
        apellido_materno=(usuario.apellido_materno or "").strip() or None,
        num_empleado=num_empleado,
        correo=correo,
        contrasena_hash=generar_hash_password(usuario.password),
        rol="capturista",
        estado="activo",
        es_superadmin=False,
    )
    db.add(nuevo_usuario)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="El correo o número de empleado ya está registrado")
    db.refresh(nuevo_usuario)
    return nuevo_usuario


@router.put("/{usuario_id}/rol")
def actualizar_rol_usuario(
    usuario_id: int,
    datos: UsuarioRolUpdate,
    db: Session = Depends(get_db),
    usuario_actual=Depends(requerir_rol(["administrador"])),
):
    if datos.rol not in {"administrador", "capturista"}:
        raise HTTPException(status_code=400, detail="Rol de usuario no válido")

    usuario = _obtener_usuario_o_404(db, usuario_id)
    _proteger_superadmin(usuario)

    if usuario.id == usuario_actual.id and datos.rol != "administrador":
        raise HTTPException(status_code=400, detail="No puedes quitarte tu propio rol de administrador")

    usuario.rol = datos.rol
    db.commit()
    return {"mensaje": "Rol actualizado correctamente", "usuario_id": usuario.id, "rol": usuario.rol}


@router.patch("/{usuario_id}/estado")
def actualizar_estado_usuario(
    usuario_id: int,
    datos: UsuarioEstadoUpdate,
    db: Session = Depends(get_db),
    usuario_actual=Depends(requerir_rol(["administrador"])),
):
    if datos.estado not in {"activo", "suspendido"}:
        raise HTTPException(status_code=400, detail="Estado de usuario no válido")

    usuario = _obtener_usuario_o_404(db, usuario_id)
    _proteger_superadmin(usuario)

    if usuario.id == usuario_actual.id and datos.estado != "activo":
        raise HTTPException(status_code=400, detail="No puedes suspender tu propia cuenta")

    usuario.estado = datos.estado
    db.commit()
    return {"mensaje": "Estado actualizado correctamente", "usuario_id": usuario.id, "estado": usuario.estado}


@router.put("/{usuario_id}", response_model=UsuarioResponse)
def actualizar_usuario(
    usuario_id: int,
    datos: UsuarioUpdate,
    db: Session = Depends(get_db),
    usuario_actual=Depends(requerir_rol(["administrador"])),
):
    usuario = _obtener_usuario_o_404(db, usuario_id)
    if usuario.es_superadmin and usuario_actual.id != usuario.id:
        raise HTTPException(status_code=400, detail="La cuenta del superadministrador está protegida")
    datos_actualizar = datos.model_dump(exclude_unset=True)
    if usuario.es_superadmin and any(campo in datos_actualizar for campo in ("correo", "num_empleado")):
        raise HTTPException(
            status_code=400,
            detail="El correo y número de empleado del superadministrador están protegidos",
        )

    for campo in ("nombre", "apellido_paterno", "correo", "num_empleado"):
        if campo in datos_actualizar and (datos_actualizar[campo] is None or not str(datos_actualizar[campo]).strip()):
            raise HTTPException(status_code=400, detail=f"El campo {campo} no puede quedar vacío")

    if "correo" in datos_actualizar and datos_actualizar["correo"] is not None:
        datos_actualizar["correo"] = datos_actualizar["correo"].strip().lower()
    if "num_empleado" in datos_actualizar and datos_actualizar["num_empleado"] is not None:
        datos_actualizar["num_empleado"] = datos_actualizar["num_empleado"].strip()

    filtros = []
    if datos_actualizar.get("correo"):
        filtros.append(UsuarioSistema.correo == datos_actualizar["correo"])
    if datos_actualizar.get("num_empleado"):
        filtros.append(UsuarioSistema.num_empleado == datos_actualizar["num_empleado"])
    if filtros:
        existente = db.query(UsuarioSistema).filter(
            UsuarioSistema.id != usuario_id,
            or_(*filtros),
        ).first()
        if existente:
            raise HTTPException(status_code=409, detail="El correo o número de empleado ya está registrado")

    for campo, valor in datos_actualizar.items():
        if isinstance(valor, str):
            valor = valor.strip()
        setattr(usuario, campo, valor)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="El correo o número de empleado ya está registrado")
    db.refresh(usuario)
    return usuario


@router.patch("/{usuario_id}/reset-password")
def reset_password_admin(
    usuario_id: int,
    db: Session = Depends(get_db),
    usuario_actual=Depends(requerir_rol(["administrador"])),
):
    usuario = _obtener_usuario_o_404(db, usuario_id)
    _proteger_superadmin(usuario)

    caracteres = string.ascii_letters + string.digits
    password_temporal = "Temp-" + "".join(secrets.choice(caracteres) for _ in range(10))
    usuario.contrasena_hash = generar_hash_password(password_temporal)
    db.commit()
    return {
        "mensaje": "Contraseña temporal generada correctamente",
        "usuario_id": usuario.id,
        "password_temporal": password_temporal,
    }
