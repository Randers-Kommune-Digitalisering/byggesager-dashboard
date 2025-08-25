from utils.database import DatabaseClient
from utils.config import (
    BYGGESAGER_POSTGRES_DB_DATABASE,
    BYGGESAGER_POSTGRES_DB_USER,
    BYGGESAGER_POSTGRES_DB_PASS,
    BYGGESAGER_POSTGRES_DB_HOST,
    BYGGESAGER_POSTGRES_DB_PORT
)


def get_byggesager_db():
    return DatabaseClient(
        db_type='postgresql',
        database=BYGGESAGER_POSTGRES_DB_DATABASE,
        username=BYGGESAGER_POSTGRES_DB_USER,
        password=BYGGESAGER_POSTGRES_DB_PASS,
        host=BYGGESAGER_POSTGRES_DB_HOST,
        port=BYGGESAGER_POSTGRES_DB_PORT
    )
