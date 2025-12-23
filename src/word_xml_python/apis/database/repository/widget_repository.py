"""
Repository 仓库层
负责与数据库直接交互，执行 SQL 操作
"""

from datetime import datetime
from typing import Any
from ..database import Database


class WidgetRepository:
    """Widget 数据仓库 - 处理数据库 CRUD 操作"""

    def __init__(self, db: Database):
        self.db = db

    def create_table_if_not_exists(self) -> None:
        """创建表（如果不存在）"""
        sql = """
        CREATE TABLE IF NOT EXISTS widget_record (
            id SERIAL PRIMARY KEY,
            label_key VARCHAR(255) NOT NULL,
            type VARCHAR(100) NOT NULL,
            options TEXT[] DEFAULT '{}',
            hit_count INTEGER DEFAULT 0,
            consistency_count INTEGER DEFAULT 0,
            un_consistency_count INTEGER DEFAULT 0,
            confidence FLOAT DEFAULT 0.0,
            create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        self.db.cursor.execute(sql)
        self.db.conn.commit()

    def create(
        self,
        label_key: str,
        type: str,
        options: list[str],
    ) -> dict[str, Any] | None:
        """创建新记录"""
        sql = """
        INSERT INTO widget_record (label_key, type, options)
        VALUES (%s, %s, %s)
        RETURNING id, label_key, type, options, hit_count, consistency_count, 
                  un_consistency_count, confidence, create_time, update_time;
        """
        self.db.cursor.execute(sql, (label_key, type, options))
        self.db.conn.commit()
        row = self.db.cursor.fetchone()
        return self._row_to_dict(row) if row else None

    def find_by_id(self, id: int) -> dict[str, Any] | None:
        """根据 ID 查询"""
        sql = """
        SELECT id, label_key, type, options, hit_count, consistency_count, 
               un_consistency_count, confidence, create_time, update_time
        FROM widget_record 
        WHERE id = %s;
        """
        self.db.cursor.execute(sql, (id,))
        row = self.db.cursor.fetchone()
        return self._row_to_dict(row) if row else None

    def find_all(self, limit: int = 100, offset: int = 0) -> list[dict[str, Any]]:
        """查询所有记录（分页）"""
        sql = """
        SELECT id, label_key, type, options, hit_count, consistency_count, 
               un_consistency_count, confidence, create_time, update_time
        FROM widget_record 
        ORDER BY create_time DESC
        LIMIT %s OFFSET %s;
        """
        self.db.cursor.execute(sql, (limit, offset))
        rows = self.db.cursor.fetchall()
        return [self._row_to_dict(row) for row in rows]

    def count_all(self) -> int:
        """获取总记录数"""
        sql = "SELECT COUNT(*) FROM widget_record;"
        self.db.cursor.execute(sql)
        result = self.db.cursor.fetchone()
        return result[0] if result else 0

    def update(self, id: int, **kwargs) -> dict[str, Any] | None:
        """更新记录"""
        # 过滤掉 None 值
        updates = {k: v for k, v in kwargs.items() if v is not None}
        if not updates:
            return self.find_by_id(id)

        # 添加更新时间
        updates["update_time"] = datetime.now()

        # 构建 SQL
        set_clause = ", ".join([f"{k} = %s" for k in updates.keys()])
        sql = f"""
        UPDATE widget_record 
        SET {set_clause}
        WHERE id = %s
        RETURNING id, label_key, type, options, hit_count, consistency_count, 
                  un_consistency_count, confidence, create_time, update_time;
        """
        values = list(updates.values()) + [id]
        self.db.cursor.execute(sql, values)
        self.db.conn.commit()
        row = self.db.cursor.fetchone()
        return self._row_to_dict(row) if row else None

    def delete(self, id: int) -> bool:
        """删除记录"""
        sql = "DELETE FROM widget_record WHERE id = %s;"
        self.db.cursor.execute(sql, (id,))
        self.db.conn.commit()
        return self.db.cursor.rowcount > 0

    def find_by_label_key(self, label_key: str) -> dict[str, Any] | None:
        """根据 label_key 查询"""
        sql = """
        SELECT id, label_key, type, options, hit_count, consistency_count, 
               un_consistency_count, confidence, create_time, update_time
        FROM widget_record 
        WHERE label_key = %s;
        """
        self.db.cursor.execute(sql, (label_key,))
        row = self.db.cursor.fetchone()
        return self._row_to_dict(row) if row else None

    def _row_to_dict(self, row: tuple) -> dict[str, Any]:
        """将数据库行转换为字典"""
        return {
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
