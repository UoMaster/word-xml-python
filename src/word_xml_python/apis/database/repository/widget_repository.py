"""
Repository 仓库层
负责与数据库直接交互，执行 SQL 操作
"""

from typing import Any

from ..database import Database


class WidgetRepository:
    """Widget 数据仓库 - 处理数据库 CRUD 操作"""

    TABLE_NAME = "weight_record"

    def __init__(self, db: Database):
        self.db = db

    def create(
        self,
        label_key: str,
        type: str,
        options: list[str],
    ) -> dict[str, Any] | None:
        """创建新记录"""
        sql = f"""
        INSERT INTO {self.TABLE_NAME} (label_key, type, options)
        VALUES (%s, %s, %s)
        RETURNING id, label_key, type, options, hit_count, consistency_count, 
                  un_consistency_count, confidence, create_time, update_time;
        """
        self.db.cursor.execute(sql, (label_key, type, options))
        self.db.conn.commit()
        row = self.db.cursor.fetchone()
        return self._row_to_dict(row) if row else None

    def find_all(self, label_key: str) -> list[dict[str, Any]]:
        """根据 label_key 查询所有记录"""
        sql = f"""
        SELECT id, label_key, type, options, hit_count, consistency_count, 
               un_consistency_count, confidence, create_time, update_time
        FROM {self.TABLE_NAME}
        WHERE label_key = %s
        """
        self.db.cursor.execute(sql, (label_key,))
        rows = self.db.cursor.fetchall()
        return [
            {
                "id": row[0],
                "label_key": row[1],
                "type": row[2],
                "options": list(row[3]) if row[3] else [],
                "hit_count": row[4],
                "consistency_count": row[5],
                "un_consistency_count": row[6],
                "confidence": row[7],
                "create_time": row[8],
                "update_time": row[9],
            }
            for row in rows
        ]

    def find_by_label_key(self, label_key: str) -> dict[str, Any] | None:
        """根据 label_key 查询单条记录"""
        sql = f"""
        SELECT id, label_key, type, options, hit_count, consistency_count, 
               un_consistency_count, confidence, create_time, update_time
        FROM {self.TABLE_NAME}
        WHERE label_key = %s
        LIMIT 1
        """
        self.db.cursor.execute(sql, (label_key,))
        row = self.db.cursor.fetchone()
        return self._row_to_dict(row) if row else None

    def count_all(self) -> int:
        """获取总记录数"""
        sql = f"SELECT COUNT(*) FROM {self.TABLE_NAME};"
        self.db.cursor.execute(sql)
        result = self.db.cursor.fetchone()
        return result[0] if result else 0
