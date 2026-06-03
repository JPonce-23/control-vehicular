from fastapi import FastAPI
from app.database import engine
from sqlalchemy import text
from app.routes.usuario_routes import router as usuario_router
from app.routes.persona_routes import router as persona_router
from app.routes.vehiculo_routes import router as vehiculo_router
from app.routes.salida_routes import router as salida_router
from app.routes.regreso_routes import router as regreso_router
from app.routes.resguardo_routes import router as resguardo_router
from app.routes.ajuste_routes import router as ajuste_router
from app.routes.item_condicion_routes import router as item_condicion_router
from app.routes.item_inventario_routes import router as item_inventario_router
from app.routes.revision_condicion_routes import router as revision_condicion_router
from app.routes.revision_inventario_routes import router as revision_inventario_router
from app.routes.presupuesto_gasolina_routes import router as presupuesto_gasolina_router
from app.routes.gasto_gasolina_routes import router as gasto_gasolina_router
from app.routes.historial_salida_routes import router as historial_salida_router
from app.routes.token_routes import router as token_router
from app.routes.auth_routes import router as auth_router

app = FastAPI(
    title="Control Vehicular PA",
    version="0.1"
)

app.include_router(usuario_router)
app.include_router(persona_router)
app.include_router(vehiculo_router)
app.include_router(salida_router)
app.include_router(regreso_router)
app.include_router(resguardo_router)
app.include_router(ajuste_router)
app.include_router(item_condicion_router)
app.include_router(item_inventario_router)
app.include_router(revision_condicion_router)
app.include_router(revision_inventario_router)
app.include_router(presupuesto_gasolina_router)
app.include_router(gasto_gasolina_router)
app.include_router(historial_salida_router)
app.include_router(token_router)
app.include_router(auth_router)


@app.get("/")
def home():
    return {"mensaje": "API funcionando"}

@app.get("/test-db")
def test_db():
    with engine.connect() as connection:
        result = connection.execute(text("SELECT current_database();"))
        database_name = result.scalar()
    return {
        "mensaje": "Conexión exitosa a PostgreSQL",
        "database": database_name
    }