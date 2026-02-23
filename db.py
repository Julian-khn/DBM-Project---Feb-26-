from __future__ import annotations
from contextlib import contextmanager
from dataclasses import dataclass
from mysql.connector import pooling

@dataclass(frozen=True)
class DbSettings:
    host: str
    port: int
    user: str
    password: str
    database: str

class Database:
    def __init__(self, settings: DbSettings, pool_name: str = "carsharing_pool", pool_size: int = 5):
        self._pool = pooling.MySQLConnectionPool(
            pool_name=pool_name,
            pool_size=pool_size,
            host=settings.host,
            port=settings.port,
            user=settings.user,
            password=settings.password,
            database=settings.database,
        )

    @contextmanager
    def connection(self):
        conn = self._pool.get_connection()
        try:
            conn.autocommit = False
            yield conn
        finally:
            conn.close()
