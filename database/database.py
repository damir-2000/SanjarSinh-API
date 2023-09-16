from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from config import DBSettings

db_settings = DBSettings()
DATABASE_URL = f'postgresql://{db_settings.database_user}:{db_settings.database_password}@{db_settings.database_host}:{db_settings.database_port}/{db_settings.database_db}'

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


create_unique_id_sequence = text("CREATE SEQUENCE IF NOT EXISTS unique_id START WITH 10000000 INCREMENT BY 1 CACHE 1;")