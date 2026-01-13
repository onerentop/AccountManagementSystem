# Google 账户管理系统

一个安全、高效的 Google 账户凭证管理系统，支持加密存储、快速搜索和一键复制。

## 功能特性

- 🔐 **安全加密** - 主密码保护 + AES-256 加密存储
- 📋 **一键复制** - 快速复制账号密码，30秒后自动清除剪贴板
- 🔍 **快速搜索** - 实时搜索账号、备注、标签
- 🏷️ **标签管理** - 多维度分类账户
- 📥 **Excel 导入** - 从现有 Excel 一键导入账户
- 📤 **数据导出** - 支持 Excel/CSV/JSON 格式
- 🌙 **深色模式** - 支持明暗主题切换

## 技术栈

### 后端
- Python 3.10+
- FastAPI
- SQLite + SQLAlchemy
- Argon2 + AES-256-GCM 加密

### 前端
- Vue 3 + TypeScript
- Pinia 状态管理
- Vue Router
- Tailwind CSS

## 快速开始

### 1. 克隆项目

```bash
cd D:\workspace\projects\AccountManagementSystem
```

### 2. 安装后端依赖

```bash
cd backend
pip install -r requirements.txt
```

### 3. 安装前端依赖

```bash
cd frontend
npm install
```

### 4. 启动开发服务器

**终端 1 - 后端:**
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**终端 2 - 前端:**
```bash
cd frontend
npm run dev
```

### 5. 访问应用

打开浏览器访问 http://localhost:5173

首次使用时，系统会引导您设置主密码。

## 项目结构

```
AccountManagementSystem/
├── backend/                # 后端代码
│   ├── app/
│   │   ├── api/           # API 路由
│   │   ├── models/        # 数据模型
│   │   ├── schemas/       # Pydantic 模式
│   │   ├── services/      # 业务逻辑
│   │   └── utils/         # 工具函数
│   └── requirements.txt
├── frontend/               # 前端代码
│   ├── src/
│   │   ├── api/           # API 客户端
│   │   ├── components/    # Vue 组件
│   │   ├── stores/        # Pinia 状态
│   │   ├── views/         # 页面视图
│   │   └── types/         # TypeScript 类型
│   └── package.json
├── data/                   # 数据目录 (自动创建)
├── docs/                   # 文档
│   └── PRD.md             # 产品需求文档
└── google.xlsx            # 原始账户数据
```

## API 文档

启动后端后访问 http://localhost:8000/docs 查看 Swagger API 文档。

## 安全说明

- 所有密码使用 AES-256-GCM 加密存储
- 主密码使用 Argon2id 算法哈希
- 会话 30 分钟无操作自动锁定
- 复制密码 30 秒后自动清除剪贴板

## 数据备份

数据存储在 `data/accounts.db` 文件中，定期备份此文件即可。

## License

MIT
