from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.config import get_settings
from app.database import engine
from app.routes import combustible_routes
from app.routes.ajuste_routes import router as ajuste_router
from app.routes.auth_routes import router as auth_router
from app.routes.historial_salida_routes import router as historial_salida_router
from app.routes.item_condicion_routes import router as item_condicion_router
from app.routes.item_inventario_routes import router as item_inventario_router
from app.routes.persona_routes import router as persona_router
from app.routes.regreso_routes import router as regreso_router
from app.routes.revision_condicion_routes import router as revision_condicion_router
from app.routes.revision_inventario_routes import router as revision_inventario_router
from app.routes.salida_routes import router as salida_router
from app.routes.usuario_routes import router as usuario_router
from app.routes.vehiculo_routes import router as vehiculo_router

settings = get_settings()
settings.validate_auth()

app = FastAPI(title="Control Vehicular PA", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

for router in (
    usuario_router,
    persona_router,
    vehiculo_router,
    salida_router,
    regreso_router,
    ajuste_router,
    item_condicion_router,
    item_inventario_router,
    revision_condicion_router,
    revision_inventario_router,
    historial_salida_router,
    auth_router,
    combustible_routes.router,
):
    app.include_router(router)


@app.get("/")
def home():
    return {"mensaje": "API funcionando", "version": app.version}


@app.get("/health")
def health():
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
    return {"status": "ok"}
