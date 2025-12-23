"""
FastAPI 主入口文件
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
import uvicorn

from .controller import widget_router
from .database.database import close_database


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理
    - 启动时：可以进行初始化操作
    - 关闭时：清理数据库连接等资源
    """
    yield
    close_database()


# 创建 FastAPI 应用
app = FastAPI(
    title="Word XML Python API",
    description="Word XML 处理服务 API",
    version="1.0.0",
    docs_url="/docs",  # Swagger UI 文档地址
    redoc_url="/redoc",  # ReDoc 文档地址
    lifespan=lifespan,  # 生命周期管理
)


app.include_router(widget_router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
