from fastapi import FastAPI
from app.database import engine
from sqlalchemy import text
from app.routes.usuario_routes import router as usuario_router

app = FastAPI(
    title="Control Vehicular PA",
    version="0.1"
)

app.include_router(usuario_router)

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