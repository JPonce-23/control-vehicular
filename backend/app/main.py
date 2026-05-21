from fastapi import FastAPI

app = FastAPI(
    title="Control Vehicular PA",
    version="0.1"
)

@app.get("/")
def home():
    return {"mensaje": "API funcionando"}