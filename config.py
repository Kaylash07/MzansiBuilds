import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "mzansi-builds-secret-key-change-in-production")

    # Render provides DATABASE_URL with postgres:// prefix; SQLAlchemy needs postgresql://
    database_url = os.environ.get(
        "DATABASE_URL",
        "postgresql+psycopg://postgres:Jasmica%4020@localhost:5432/mzansibuilds"
    )
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql+psycopg://", 1)
    elif database_url.startswith("postgresql://"):
        database_url = database_url.replace("postgresql://", "postgresql+psycopg://", 1)

    SQLALCHEMY_DATABASE_URI = database_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
