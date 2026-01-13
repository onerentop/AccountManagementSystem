# Google 账户管理系统 - 产品需求文档 (PRD)

> **版本**: 1.0.0
> **创建日期**: 2026-01-14
> **状态**: 待开发

---

## 目录

1. [项目概述](#1-项目概述)
2. [用户研究](#2-用户研究)
3. [功能需求](#3-功能需求)
4. [数据模型](#4-数据模型)
5. [技术架构](#5-技术架构)
6. [安全设计](#6-安全设计)
7. [UI/UX 规范](#7-uiux-规范)
8. [实现路线图](#8-实现路线图)
9. [验收标准](#9-验收标准)

---

## 1. 项目概述

### 1.1 产品定位

一个安全、高效的 Google 账户管理系统，用于管理多个 Google 账户的凭证信息，支持便捷的增删改查操作，并提供加密存储保护。

### 1.2 核心价值

| 价值点 | 描述 |
|--------|------|
| **安全性** | 主密码保护 + AES-256 加密存储，敏感信息绝不明文暴露 |
| **高效性** | 快速搜索、一键复制、批量操作，显著提升管理效率 |
| **易用性** | 现代简约界面，零学习成本 |
| **可靠性** | 本地存储，数据完全自主掌控 |

### 1.3 项目范围

**包含**:
- Web 应用 (本地部署)
- 账户 CRUD 操作
- 加密存储
- 搜索和筛选
- 数据导入导出

**不包含**:
- 云同步功能
- 移动端 App
- 多用户协作
- 浏览器自动填充插件

### 1.4 技术选型概览

| 层面 | 技术 |
|------|------|
| **前端** | Vue 3 + TypeScript + Tailwind CSS |
| **后端** | Python + FastAPI |
| **数据库** | SQLite + SQLCipher (加密) |
| **认证** | JWT + Argon2id |

---

## 2. 用户研究

### 2.1 目标用户

**主要用户画像**:
- 管理多个 Google 账户的个人用户
- 有 GPT 会员等订阅服务需要管理
- 需要安全存储账户凭证
- 技术背景用户，可本地部署

### 2.2 用户痛点

| 痛点 | 当前解决方案 | 问题 |
|------|--------------|------|
| 账户多，记不住 | Excel 表格管理 | 密码明文存储，不安全 |
| 查找效率低 | Ctrl+F 搜索 | 无法多维度筛选 |
| 复制账密繁琐 | 手动选择复制 | 效率低，易出错 |
| 无法分类管理 | 多个工作表 | 维护困难 |

### 2.3 使用场景

**场景 1: 快速登录**
> 用户需要登录某个 Google 账户，打开管理系统 → 搜索账号 → 一键复制密码 → 粘贴登录

**场景 2: 账户维护**
> 用户新购买了一批账户，导入 Excel → 批量添加标签 → 更新备注信息

**场景 3: 账户审计**
> 用户需要检查所有 GPT 会员账户状态，按标签筛选 → 查看列表 → 导出报告

---

## 3. 功能需求

### 3.1 功能优先级矩阵

| 优先级 | 功能模块 | 说明 |
|--------|----------|------|
| **P0** | 核心 CRUD | 基础账户管理功能 |
| **P0** | 主密码认证 | 安全核心 |
| **P0** | 加密存储 | 安全核心 |
| **P1** | 搜索筛选 | 提升效率关键 |
| **P1** | 一键复制 | 高频操作 |
| **P1** | 数据导入 | 迁移现有数据 |
| **P2** | 标签管理 | 分类组织 |
| **P2** | 数据导出 | 备份需求 |
| **P2** | 深色模式 | 用户体验 |
| **P3** | 批量操作 | 效率提升 |

### 3.2 详细功能规格

#### 3.2.1 认证模块 (P0)

**F-AUTH-001: 主密码设置**
- 首次使用时引导设置主密码
- 密码强度检测 (最少 8 位，包含大小写和数字)
- 密码确认输入

**F-AUTH-002: 主密码登录**
- 每次打开应用需验证主密码
- 错误次数限制 (5次后锁定 5 分钟)
- 支持 "记住我" (可选，存储加密 token)

**F-AUTH-003: 会话管理**
- 登录后生成 JWT Token
- 默认 30 分钟无操作自动锁定
- 支持手动锁定

**F-AUTH-004: 修改主密码**
- 需验证当前密码
- 修改后重新加密所有数据

---

#### 3.2.2 账户管理模块 (P0)

**F-ACCT-001: 查看账户列表**
- 表格形式展示账户
- 分页显示 (默认每页 20 条)
- 支持按列排序
- 密码列默认隐藏 (显示 ******)

**F-ACCT-002: 添加账户**
- 表单输入账户信息
- 必填字段: 账号
- 可选字段: 密码、备注、来源、标签等
- 保存前验证邮箱格式

**F-ACCT-003: 编辑账户**
- 点击账户行进入编辑模式
- 实时保存或手动保存
- 修改历史记录 (可选)

**F-ACCT-004: 删除账户**
- 单个删除需二次确认
- 批量删除需显示数量确认
- 软删除 (可恢复) 或硬删除 (不可恢复)

**F-ACCT-005: 查看账户详情**
- 点击展开完整信息
- 显示创建/更新时间
- 显示关联标签

---

#### 3.2.3 搜索筛选模块 (P1)

**F-SRCH-001: 全局搜索**
- 顶部搜索框
- 实时搜索 (debounce 300ms)
- 搜索范围: 账号、备注、标签
- 高亮匹配文本

**F-SRCH-002: 高级筛选**
- 按来源筛选
- 按标签筛选 (多选)
- 按 GPT 会员状态筛选
- 按创建时间范围筛选

**F-SRCH-003: 筛选组合**
- 多条件 AND 组合
- 保存常用筛选条件 (可选)

---

#### 3.2.4 快捷操作模块 (P1)

**F-QUIK-001: 一键复制账号**
- 点击账号旁复制图标
- 复制成功显示 Toast 提示
- 快捷键支持 (可选)

**F-QUIK-002: 一键复制密码**
- 点击密码行复制按钮
- 需先解锁密码显示 (点击眼睛图标)
- 复制后 30 秒自动清除剪贴板
- 显示倒计时

**F-QUIK-003: 快捷键支持**
- `Ctrl+F` / `Cmd+F`: 聚焦搜索
- `Ctrl+N` / `Cmd+N`: 新增账户
- `Escape`: 关闭弹窗

---

#### 3.2.5 标签管理模块 (P2)

**F-TAG-001: 标签 CRUD**
- 创建新标签 (名称 + 颜色)
- 编辑标签
- 删除标签 (同时解除关联)

**F-TAG-002: 账户打标签**
- 编辑账户时选择标签
- 支持多标签
- 标签自动补全

**F-TAG-003: 按标签浏览**
- 侧边栏标签列表
- 点击标签筛选账户
- 显示每个标签的账户数量

---

#### 3.2.6 数据导入导出模块 (P1/P2)

**F-IO-001: Excel 导入 (P1)**
- 上传 .xlsx 或 .xls 文件
- 字段映射界面
- 预览导入数据
- 冲突处理策略 (跳过/覆盖/合并)
- 导入进度显示

**F-IO-002: 数据导出 (P2)**
- 导出格式: Excel / CSV / JSON
- 选择导出字段
- 选择导出范围 (全部/筛选结果/选中项)
- 密码导出选项 (明文/脱敏/排除)

**F-IO-003: 数据备份 (P2)**
- 导出加密备份文件
- 备份恢复功能
- 自动备份 (可选)

---

#### 3.2.7 界面与体验 (P2)

**F-UI-001: 深色模式**
- 明暗主题切换
- 跟随系统设置 (可选)
- 平滑过渡动画

**F-UI-002: 响应式布局**
- 桌面端优化 (1280px+)
- 平板适配 (768px-1279px)
- 移动端基础适配 (< 768px)

**F-UI-003: 加载状态**
- 骨架屏加载
- 操作中 Loading 指示
- 错误状态友好提示

---

## 4. 数据模型

### 4.1 实体关系图

```
┌─────────────────┐       ┌─────────────────┐
│    Account      │       │      Tag        │
├─────────────────┤       ├─────────────────┤
│ id (PK)         │       │ id (PK)         │
│ email           │◄──────│ name            │
│ password_enc    │   M:N │ color           │
│ note            │       │ created_at      │
│ sub2api         │       └─────────────────┘
│ source          │
│ browser         │       ┌─────────────────┐
│ gpt_membership  │       │  AccountTag     │
│ family_group    │       ├─────────────────┤
│ recovery_email  │       │ account_id (FK) │
│ totp_secret_enc │◄──────│ tag_id (FK)     │
│ created_at      │   1:N └─────────────────┘
│ updated_at      │
└─────────────────┘

┌─────────────────┐
│   SystemConfig  │
├─────────────────┤
│ key (PK)        │
│ value           │
│ updated_at      │
└─────────────────┘
```

### 4.2 数据表详细定义

#### accounts 表

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | UUID | PK | 主键 |
| email | VARCHAR(255) | NOT NULL, UNIQUE | 账号邮箱 |
| password_encrypted | BLOB | NULL | AES-256 加密密码 |
| note | TEXT | NULL | 备注 |
| sub2api | BOOLEAN | DEFAULT FALSE | 是否有 sub2api |
| source | VARCHAR(50) | NULL | 来源 (自建/购买等) |
| browser | VARCHAR(50) | NULL | 登录浏览器 |
| gpt_membership | VARCHAR(20) | NULL | GPT 会员状态 |
| family_group | VARCHAR(100) | NULL | 所属家庭组 |
| recovery_email | VARCHAR(255) | NULL | 辅助邮箱 |
| totp_secret_encrypted | BLOB | NULL | 2FA 密钥 (加密) |
| is_deleted | BOOLEAN | DEFAULT FALSE | 软删除标记 |
| created_at | DATETIME | NOT NULL | 创建时间 |
| updated_at | DATETIME | NOT NULL | 更新时间 |

#### tags 表

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | UUID | PK | 主键 |
| name | VARCHAR(50) | NOT NULL, UNIQUE | 标签名称 |
| color | VARCHAR(7) | DEFAULT '#6366f1' | 标签颜色 (HEX) |
| created_at | DATETIME | NOT NULL | 创建时间 |

#### account_tags 表

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| account_id | UUID | FK → accounts.id | 账户 ID |
| tag_id | UUID | FK → tags.id | 标签 ID |
| PRIMARY KEY | (account_id, tag_id) | | 联合主键 |

#### system_config 表

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| key | VARCHAR(50) | PK | 配置键 |
| value | TEXT | NOT NULL | 配置值 |
| updated_at | DATETIME | NOT NULL | 更新时间 |

配置项示例:
- `master_password_hash`: 主密码哈希 (Argon2id)
- `encryption_salt`: 加密盐值
- `session_timeout`: 会话超时时间
- `theme`: 主题设置

---

## 5. 技术架构

### 5.1 系统架构图

```
┌──────────────────────────────────────────────────────────────┐
│                        Client (Browser)                       │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                    Vue 3 Application                     │ │
│  │  ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌─────────┐ │ │
│  │  │  Views    │ │Components │ │   Store   │ │ Router  │ │ │
│  │  │ - Login   │ │ - Table   │ │ - Pinia   │ │ - Auth  │ │ │
│  │  │ - Home    │ │ - Form    │ │ - State   │ │ - Guard │ │ │
│  │  │ - Account │ │ - Modal   │ │           │ │         │ │ │
│  │  └───────────┘ └───────────┘ └───────────┘ └─────────┘ │ │
│  └─────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
                              │
                              │ HTTP/REST API
                              ▼
┌──────────────────────────────────────────────────────────────┐
│                    Backend (FastAPI)                          │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                      API Layer                           │ │
│  │  ┌───────────┐ ┌───────────┐ ┌───────────┐             │ │
│  │  │ /auth     │ │ /accounts │ │ /tags     │             │ │
│  │  │ - login   │ │ - CRUD    │ │ - CRUD    │             │ │
│  │  │ - logout  │ │ - search  │ │           │             │ │
│  │  └───────────┘ └───────────┘ └───────────┘             │ │
│  └─────────────────────────────────────────────────────────┘ │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                    Service Layer                         │ │
│  │  ┌───────────┐ ┌───────────┐ ┌───────────┐             │ │
│  │  │ AuthSvc   │ │AccountSvc │ │ CryptoSvc │             │ │
│  │  └───────────┘ └───────────┘ └───────────┘             │ │
│  └─────────────────────────────────────────────────────────┘ │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                    Data Layer                            │ │
│  │  ┌───────────┐ ┌───────────┐                            │ │
│  │  │ SQLAlchemy│ │  Models   │                            │ │
│  │  │   ORM     │ │           │                            │ │
│  │  └───────────┘ └───────────┘                            │ │
│  └─────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────┐
│              SQLite + SQLCipher (Encrypted)                   │
│                     accounts.db.enc                           │
└──────────────────────────────────────────────────────────────┘
```

### 5.2 目录结构

```
AccountManagementSystem/
├── docs/                      # 文档
│   └── PRD.md
├── backend/                   # 后端代码
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py           # FastAPI 入口
│   │   ├── config.py         # 配置
│   │   ├── api/              # API 路由
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── accounts.py
│   │   │   └── tags.py
│   │   ├── models/           # 数据模型
│   │   │   ├── __init__.py
│   │   │   ├── account.py
│   │   │   └── tag.py
│   │   ├── schemas/          # Pydantic 模式
│   │   │   ├── __init__.py
│   │   │   ├── account.py
│   │   │   └── auth.py
│   │   ├── services/         # 业务逻辑
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py
│   │   │   ├── account_service.py
│   │   │   └── crypto_service.py
│   │   └── utils/            # 工具函数
│   │       ├── __init__.py
│   │       └── security.py
│   ├── requirements.txt
│   └── pyproject.toml
├── frontend/                  # 前端代码
│   ├── src/
│   │   ├── main.ts
│   │   ├── App.vue
│   │   ├── views/
│   │   │   ├── LoginView.vue
│   │   │   ├── HomeView.vue
│   │   │   └── SettingsView.vue
│   │   ├── components/
│   │   │   ├── AccountTable.vue
│   │   │   ├── AccountForm.vue
│   │   │   ├── SearchBar.vue
│   │   │   └── TagSelector.vue
│   │   ├── stores/
│   │   │   ├── auth.ts
│   │   │   └── accounts.ts
│   │   ├── router/
│   │   │   └── index.ts
│   │   └── styles/
│   │       └── main.css
│   ├── package.json
│   └── vite.config.ts
├── data/                      # 数据目录 (gitignore)
│   └── accounts.db.enc
├── google.xlsx               # 原始数据文件
└── README.md
```

### 5.3 API 设计

#### 认证 API

| 方法 | 端点 | 说明 |
|------|------|------|
| POST | /api/auth/setup | 首次设置主密码 |
| POST | /api/auth/login | 登录验证 |
| POST | /api/auth/logout | 登出 |
| POST | /api/auth/lock | 手动锁定 |
| PUT | /api/auth/password | 修改主密码 |

#### 账户 API

| 方法 | 端点 | 说明 |
|------|------|------|
| GET | /api/accounts | 获取账户列表 (分页) |
| GET | /api/accounts/:id | 获取账户详情 |
| POST | /api/accounts | 创建账户 |
| PUT | /api/accounts/:id | 更新账户 |
| DELETE | /api/accounts/:id | 删除账户 |
| POST | /api/accounts/import | 导入 Excel |
| GET | /api/accounts/export | 导出数据 |

#### 标签 API

| 方法 | 端点 | 说明 |
|------|------|------|
| GET | /api/tags | 获取所有标签 |
| POST | /api/tags | 创建标签 |
| PUT | /api/tags/:id | 更新标签 |
| DELETE | /api/tags/:id | 删除标签 |

---

## 6. 安全设计

### 6.1 安全架构

```
┌─────────────────────────────────────────────────────────────┐
│                      Security Layers                         │
├─────────────────────────────────────────────────────────────┤
│ Layer 1: Authentication                                      │
│   ├── Master Password → Argon2id Hash                       │
│   └── JWT Token (HS256, 30min expiry)                       │
├─────────────────────────────────────────────────────────────┤
│ Layer 2: Authorization                                       │
│   └── Route Guards (前端) + Middleware (后端)                │
├─────────────────────────────────────────────────────────────┤
│ Layer 3: Data Encryption                                     │
│   ├── Sensitive Fields → AES-256-GCM                        │
│   └── Database → SQLCipher                                  │
├─────────────────────────────────────────────────────────────┤
│ Layer 4: Transmission                                        │
│   └── HTTPS (production) / localhost only (dev)             │
└─────────────────────────────────────────────────────────────┘
```

### 6.2 加密策略

#### 主密码处理

```python
# 使用 Argon2id 密钥派生
from argon2 import PasswordHasher

ph = PasswordHasher(
    time_cost=3,           # 迭代次数
    memory_cost=65536,     # 64MB 内存
    parallelism=4,         # 并行度
    hash_len=32,           # 输出长度
    salt_len=16            # 盐长度
)

# 存储: 只存储哈希，不存储明文
password_hash = ph.hash(master_password)
```

#### 敏感字段加密

```python
# AES-256-GCM 加密
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

def encrypt_field(plaintext: str, key: bytes) -> bytes:
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    ciphertext = aesgcm.encrypt(nonce, plaintext.encode(), None)
    return nonce + ciphertext

def decrypt_field(encrypted: bytes, key: bytes) -> str:
    aesgcm = AESGCM(key)
    nonce = encrypted[:12]
    ciphertext = encrypted[12:]
    return aesgcm.decrypt(nonce, ciphertext, None).decode()
```

### 6.3 会话安全

| 措施 | 说明 |
|------|------|
| JWT 过期 | 30 分钟无操作后 Token 失效 |
| 刷新机制 | 活跃操作时自动续期 |
| 单设备限制 | 可选，新登录使旧会话失效 |
| 锁定功能 | 支持手动锁定，需重新输入密码 |

### 6.4 剪贴板安全

```javascript
// 复制密码后自动清除
const copyPassword = async (password: string) => {
  await navigator.clipboard.writeText(password)

  // 30秒后清除
  setTimeout(async () => {
    const current = await navigator.clipboard.readText()
    if (current === password) {
      await navigator.clipboard.writeText('')
    }
  }, 30000)
}
```

---

## 7. UI/UX 规范

### 7.1 设计原则

1. **简洁高效**: 减少点击，快速完成任务
2. **信息分层**: 重要信息突出，次要信息隐藏
3. **反馈及时**: 操作有响应，状态有提示
4. **一致性**: 组件样式和交互保持统一

### 7.2 颜色规范

#### 浅色主题

| 用途 | 颜色 | HEX |
|------|------|-----|
| Primary | Indigo | #6366f1 |
| Secondary | Slate | #64748b |
| Success | Emerald | #10b981 |
| Warning | Amber | #f59e0b |
| Danger | Rose | #f43f5e |
| Background | White | #ffffff |
| Surface | Gray-50 | #f8fafc |
| Text Primary | Gray-900 | #0f172a |
| Text Secondary | Gray-500 | #64748b |

#### 深色主题

| 用途 | 颜色 | HEX |
|------|------|-----|
| Primary | Indigo-400 | #818cf8 |
| Background | Gray-900 | #0f172a |
| Surface | Gray-800 | #1e293b |
| Text Primary | Gray-100 | #f1f5f9 |
| Text Secondary | Gray-400 | #94a3b8 |

### 7.3 页面布局

```
┌─────────────────────────────────────────────────────────────┐
│                      Header (64px)                           │
│  ┌──────┐ ┌────────────────────────────┐ ┌────┐ ┌────────┐ │
│  │ Logo │ │        Search Bar          │ │ +  │ │ Avatar │ │
│  └──────┘ └────────────────────────────┘ └────┘ └────────┘ │
├─────────────────────────────────────────────────────────────┤
│ Sidebar │                Main Content                        │
│ (240px) │                                                    │
│         │  ┌─────────────────────────────────────────────┐  │
│ ┌─────┐ │  │              Filter Bar                     │  │
│ │ All │ │  └─────────────────────────────────────────────┘  │
│ │ 40  │ │                                                    │
│ └─────┘ │  ┌─────────────────────────────────────────────┐  │
│         │  │                                             │  │
│ Tags:   │  │              Account Table                  │  │
│ ┌─────┐ │  │                                             │  │
│ │ Pro │ │  │  ┌───────────────────────────────────────┐ │  │
│ │ 25  │ │  │  │ Email       Password  Source  Tags   │ │  │
│ └─────┘ │  │  ├───────────────────────────────────────┤ │  │
│ ┌─────┐ │  │  │ xxx@...     ******    自建    [Pro]  │ │  │
│ │ GPT │ │  │  │ yyy@...     ******    购买    [GPT]  │ │  │
│ │ 15  │ │  │  └───────────────────────────────────────┘ │  │
│ └─────┘ │  │                                             │  │
│         │  └─────────────────────────────────────────────┘  │
│         │                                                    │
│         │  ┌─────────────────────────────────────────────┐  │
│         │  │              Pagination                     │  │
│         │  └─────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### 7.4 关键交互

#### 账户行操作

```
┌────────────────────────────────────────────────────────────┐
│ ☐ │ xxx@gmail.com │ ****** 👁 📋 │ 自建 │ [Pro] │ ⋮ │
└────────────────────────────────────────────────────────────┘
      │                 │    │              │
      │                 │    └── 复制密码    └── 更多操作菜单
      │                 └── 显示/隐藏密码        - 编辑
      └── 点击复制账号                           - 删除
                                                  - 管理标签
```

#### 表单设计

- 标签使用浮动标签 (Floating Label)
- 输入框使用柔和边框和聚焦效果
- 错误提示使用内联方式
- 保存按钮固定在表单底部

---

## 8. 实现路线图

### 8.1 开发阶段

```
Phase 1: 核心功能 (MVP)                           [Week 1-2]
├── 后端基础框架搭建
├── 数据库设计与加密
├── 主密码认证
├── 账户 CRUD API
├── 前端基础框架
├── 登录页面
├── 账户列表页
└── 基础搜索功能

Phase 2: 增强功能                                  [Week 3]
├── 一键复制功能
├── Excel 导入
├── 标签管理
├── 高级筛选
└── 数据导出

Phase 3: 体验优化                                  [Week 4]
├── 深色模式
├── 响应式适配
├── 批量操作
├── 键盘快捷键
└── 性能优化

Phase 4: 测试与部署                                [Week 5]
├── 单元测试
├── E2E 测试
├── 安全审计
├── 部署文档
└── 用户指南
```

### 8.2 里程碑

| 里程碑 | 交付物 | 完成标准 |
|--------|--------|----------|
| M1 | MVP 可用 | 可完成基本登录、查看、搜索 |
| M2 | 功能完整 | 所有 P0/P1 功能可用 |
| M3 | 体验优化 | 深色模式、响应式、快捷键 |
| M4 | 上线就绪 | 测试通过、文档完整 |

---

## 9. 验收标准

### 9.1 功能验收

| 功能 | 验收条件 |
|------|----------|
| 登录 | 正确密码可登录，错误密码有提示 |
| 账户列表 | 正确显示所有账户，支持分页 |
| 搜索 | 300ms 内返回结果，高亮匹配 |
| 复制 | 点击即复制，Toast 反馈 |
| 导入 | 40 条数据 5 秒内完成导入 |

### 9.2 性能验收

| 指标 | 标准 |
|------|------|
| 首屏加载 | < 2s |
| API 响应 | < 500ms |
| 搜索响应 | < 300ms |
| 内存占用 | < 200MB |

### 9.3 安全验收

| 检查项 | 要求 |
|--------|------|
| 密码存储 | 无明文存储 |
| 数据库 | 加密存储 |
| 会话 | 超时自动锁定 |
| 剪贴板 | 自动清除 |

---

## 附录

### A. 现有数据字段映射

| Excel 列 | 数据库字段 | 说明 |
|----------|------------|------|
| 账号 | email | 直接映射 |
| 密码 | password_encrypted | 加密存储 |
| 备注 | note | 直接映射 |
| sub2api | sub2api | 转换为布尔值 |
| 来源 | source | 直接映射 |
| 登录浏览器 | browser | 直接映射 |
| 是否是gpt会员 | gpt_membership | 直接映射 |
| 所属家庭 | family_group | 直接映射 |
| 辅助邮箱 | recovery_email | 直接映射 |
| 2fa | totp_secret_encrypted | 加密存储 |

### B. 参考资料

- [FastAPI 官方文档](https://fastapi.tiangolo.com/)
- [Vue 3 官方文档](https://vuejs.org/)
- [SQLCipher 官方文档](https://www.zetetic.net/sqlcipher/)
- [Tailwind CSS](https://tailwindcss.com/)
- [Argon2 密码哈希](https://github.com/P-H-C/phc-winner-argon2)

---

> **文档维护**
> 本文档应随项目进展持续更新。任何需求变更需在此处记录并注明版本。
