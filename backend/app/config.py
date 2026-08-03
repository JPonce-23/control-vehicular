import os
from functools import lru_cache

from dotenv import load_dotenv

load_dotenv()


class Settings:
    def __init__(self) -> None:
        self.database_url = os.getenv("DATABASE_URL", "").strip()
        self.db_host = os.getenv("DB_HOST", "localhost").strip()
        self.db_port = os.getenv("DB_PORT", "5432").strip()
        self.db_name = os.getenv("DB_NAME", "control_vehicular").strip()
        self.db_user = os.getenv("DB_USER", "postgres").strip()
        self.db_password = os.getenv("DB_PASSWORD", "")

        self.secret_key = os.getenv("SECRET_KEY", "").strip()
        self.algorithm = os.getenv("ALGORITHM", "HS256").strip()
        self.access_token_expire_minutes = int(
            os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
        )

        cors_default = ",".join(
            [
                "http://localhost:3000",
                "http://127.0.0.1:3000",
                "http://localhost:5500",
                "http://127.0.0.1:5500",
            ]
        )
        self.cors_origins = [
            origin.strip()
            for origin in os.getenv("CORS_ORIGINS", cors_default).split(",")
            if origin.strip()
        ]

        self.smtp_host = os.getenv("SMTP_HOST", "").strip()
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER", "").strip()
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        self.smtp_from = os.getenv("SMTP_FROM", "").strip()

    def validate_auth(self) -> None:
        if not self.secret_key or self.secret_key == "CAMBIAR_EN_PRODUCCION":
            raise RuntimeError(
                "SECRET_KEY no está configurada. Define una clave larga y aleatoria en .env."
            )


@lru_cache
def get_settings() -> Settings:
    return Settings()
