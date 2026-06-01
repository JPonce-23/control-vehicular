from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.token_model import TokenAcceso
from app.schemas.token_schema import TokenAccesoResponse

router = APIRouter(
    prefix="/tokens",
    tags=["Tokens"]
)

@router.get("/", response_model=list[TokenAccesoResponse])
def listar_tokens(db: Session = Depends(get_db)):
    return db.query(TokenAcceso).all()