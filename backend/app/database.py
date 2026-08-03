from urllib.parse import quote_plus

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import get_settings

settings = get_settings()

if settings.database_url:
    DATABASE_URL = settings.database_url
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = "postgresql://" + DATABASE_URL[len("postgres://"):]
else:
    password = quote_plus(settings.db_password)
    user = quote_plus(settings.db_user)
    DATABASE_URL = (
        f"postgresql://{user}:{password}"
        f"@{settings.db_host}:{settings.db_port}/{settings.db_name}"
    )

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
Base = declarative_base()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
