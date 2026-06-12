from sqlalchemy import Column, Integer, String, DateTime, func
from app.database import Base
from pydantic import BaseModel
from typing import Optional
from datetime import date

class UsuarioSistema(Base):
    __tablename__ = "usuario_sistema"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String)
    apellido_paterno = Column(String)
    apellido_materno = Column(String)
    num_empleado = Column(String)
    correo = Column(String)
    contrasena_hash = Column(String)
    rol = Column(String)
    estado = Column(String)
    fecha_alta = Column(DateTime, nullable=False, server_default=func.now())
    ultimo_acceso = Column(DateTime)
    
    
    
