"""API服务器启动脚本"""

import uvicorn


if __name__ == "__main__":
    print("🚀 启动 Word XML Parser API 服务器...")
    print("📝 API文档地址: http://localhost:8000/docs")
    print("🔍 健康检查: http://localhost:8000/health")
    print("=" * 50)
    
    uvicorn.run(
        "src.word_xml_python.exporters.api_exporter:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # 开发模式下自动重载
        log_level="info"
    )

