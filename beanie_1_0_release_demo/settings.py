from pydantic import BaseSettings


class Settings(BaseSettings):
    mongodb_dsn: str = "mongodb://localhost:27017"
    mongodb_db_name: str = "beanie_db"
