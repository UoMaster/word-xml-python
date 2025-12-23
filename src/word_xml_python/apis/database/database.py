from __future__ import annotations

from typing import TYPE_CHECKING

import psycopg2

if TYPE_CHECKING:
    from psycopg2.extensions import connection, cursor


class Database:
    """数据库连接类"""

    db_url: str = "postgresql://dev_user:dev_password@localhost:5432/dev_db"
    conn: connection | None = None
    _cursor: cursor | None = None

    def __init__(self):
        self.conn = psycopg2.connect(self.db_url)
        self._cursor = self.conn.cursor()

    @property
    def cursor(self) -> cursor:
        """获取数据库游标"""
        if self._cursor is None:
            raise RuntimeError("Database cursor is not initialized")
        return self._cursor

    def close(self):
        if self._cursor:
            self._cursor.close()
        if self.conn:
            self.conn.close()


# ==================== 依赖注入 ====================

# 全局数据库单例
_db_instance: Database | None = None


def get_database() -> Database:
    """
    获取数据库单例实例（用于 FastAPI 依赖注入）

    使用方式:
        @router.get("/")
        async def handler(db: Database = Depends(get_database)):
            ...
    """
    global _db_instance
    if _db_instance is None:
        _db_instance = Database()
    return _db_instance


def close_database() -> None:
    """关闭数据库连接（应用关闭时调用）"""
    global _db_instance
    if _db_instance is not None:
        _db_instance.close()
        _db_instance = None
