# MelodyCommons - 共享音乐库系统

一个基于 FastAPI + Vue 3 的音乐共享平台。

## 项目结构

```
MelodyCommons/
├── MelodyCommons__backend/    # FastAPI 后端
│   ├── api/                   # API 路由
│   ├── utils/                 # 工具函数
│   ├── static/                # 静态资源（音频文件、封面）
│   ├── main.py               # 应用入口
│   ├── models.py             # 数据库模型
│   ├── schemas.py            # Pydantic 模型
│   ├── crud.py               # 数据库操作
│   ├── auth.py               # 认证相关
│   ├── database.py           # 数据库配置
│   └── requirements.txt      # Python 依赖
│
└── melodycommons__frontend/   # Vue 3 前端
    ├── src/
    ├── package.json
    └── vite.config.ts
```

## 快速启动

### 后端
```bash
cd MelodyCommons__backend
python -m uvicorn main:app --reload
```

### 前端
```bash
cd melodycommons__frontend
npm run dev
```

## 功能特性

- 🎵 音乐库管理
- 📝 歌单创建
- 🔥 热门歌曲
- 🎧 在线播放
- 🔐 用户认证

## 技术栈

**后端**: FastAPI, SQLAlchemy, SQLite
**前端**: Vue 3, TypeScript, Vite

---



