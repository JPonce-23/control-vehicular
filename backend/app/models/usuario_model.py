from sqlalchemy import Boolean, Column, DateTime, Integer, String, func

from app.database import Base


class UsuarioSistema(Base):
    __tablename__ = "usuario_sistema"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    apellido_paterno = Column(String(100), nullable=False)
    apellido_materno = Column(String(100), nullable=True)
    num_empleado = Column(String(50), nullable=False, unique=True)
    correo = Column(String(150), nullable=False, unique=True)
    contrasena_hash = Column(String(255), nullable=False)
    rol = Column(String, nullable=False)
    estado = Column(String, nullable=False, default="activo")
    es_superadmin = Column(Boolean, nullable=False, default=False, server_default="false")
    fecha_alta = Column(DateTime, nullable=False, server_default=func.now())
    ultimo_acceso = Column(DateTime, nullable=True)
