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
        log_type: str,
    ) -> dict[str, Any] | None:
        """创建新记录"""
        sql = f"""
        INSERT INTO {self.TABLE_NAME} (label_key, type, options, hit_count, consistency_count, un_consistency_count, confidence)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING id, label_key, type, options, hit_count, consistency_count, 
                  un_consistency_count, confidence, create_time, update_time;
        """
        consistency_count = 1 if log_type == "consistency" else 0
        un_consistency_count = 1 if log_type == "consistency" else 0
        self.db.cursor.execute(
            sql,
            (label_key, type, options, 0, consistency_count, un_consistency_count, 0),
        )
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

    def find_by_label_key(self, label_key: str) -> list[dict[str, Any]]:
        """根据 label_key 查询多条记录"""
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

    def count_all(self) -> int:
        """获取总记录数"""
        sql = f"SELECT COUNT(*) FROM {self.TABLE_NAME};"
        self.db.cursor.execute(sql)
        result = self.db.cursor.fetchone()
        return result[0] if result else 0

    def find_by_label_key_and_type(
        self, label_key: str, type: str
    ) -> dict[str, Any] | None:
        """根据 label_key 和 type 查询单条记录"""
        sql = f"""
        SELECT id, label_key, type, options, hit_count, consistency_count, 
               un_consistency_count, confidence, create_time, update_time
        FROM {self.TABLE_NAME}
        WHERE label_key = %s AND type = %s
        LIMIT 1
        """
        self.db.cursor.execute(sql, (label_key, type))
        row = self.db.cursor.fetchone()
        return (
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
            if row
            else None
        )

    def update_hit_count_by_label_key_and_type(
        self, label_key: str, type: str, hit_count: int
    ) -> bool:
        """根据 label_key 和 type 更新 hit_count"""
        sql = f"""
        UPDATE {self.TABLE_NAME}
        SET hit_count = %s
        WHERE label_key = %s AND type = %s
        """
        self.db.cursor.execute(sql, (hit_count, label_key, type))
        self.db.conn.commit()
        return self.db.cursor.rowcount > 0

    def update_consistency_count_by_label_key_and_type(
        self, label_key: str, type: str, consistency_count: int
    ) -> bool:
        """根据 label_key 和 type 更新 consistency_count"""
        sql = f"""
        UPDATE {self.TABLE_NAME}
        SET consistency_count = %s
        WHERE label_key = %s AND type = %s
        """
        self.db.cursor.execute(sql, (consistency_count, label_key, type))
        self.db.conn.commit()
        return self.db.cursor.rowcount > 0

    def update_un_consistency_count_by_label_key_and_type(
        self, label_key: str, type: str, un_consistency_count: int
    ) -> bool:
        """根据 label_key 和 type 更新 un_consistency_count"""
        sql = f"""
        UPDATE {self.TABLE_NAME}
        SET un_consistency_count = %s
        WHERE label_key = %s AND type = %s
        """
        self.db.cursor.execute(sql, (un_consistency_count, label_key, type))
        self.db.conn.commit()
        return self.db.cursor.rowcount > 0
