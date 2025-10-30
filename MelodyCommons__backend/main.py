from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import os

from database import create_tables
from api import auth, songs, playlists
from utils.file import ensure_directories

# 创建FastAPI应用
app = FastAPI(
    title="MelodyCommons API",
    description="共享音乐库系统API",
    version="1.0.0"
)

# CORS配置 - 修复CORS问题
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],  # 明确指定前端地址
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# 确保目录存在
ensure_directories()

# 创建数据库表
create_tables()

# 挂载静态文件
if not os.path.exists("static"):
    os.makedirs("static", exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")

# 注册路由
app.include_router(auth.router)
app.include_router(songs.router)
app.include_router(playlists.router)


# 全局异常处理
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": f"HTTP_{exc.status_code}",
            "message": exc.detail,
            "details": {}
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    print(f"Unhandled exception: {exc}")  # 添加调试日志
    return JSONResponse(
        status_code=500,
        content={
            "error": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected error occurred",
            "details": {"exception": str(exc)}
        }
    )


# 根路径
@app.get("/")
def read_root():
    return {
        "message": "Welcome to MelodyCommons API",
        "docs": "/docs",
        "redoc": "/redoc"
    }


# 健康检查
@app.get("/health")
def health_check():
    return {"status": "healthy", "message": "MelodyCommons API is running"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
