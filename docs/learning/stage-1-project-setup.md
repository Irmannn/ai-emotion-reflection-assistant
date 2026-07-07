# 阶段 1：项目骨架与基础环境

## 阶段目标

- 创建前端 Next.js 项目结构。
- 创建后端 FastAPI 项目结构。
- 前后端可以分别启动。
- 后端提供 `/health` 健康检查接口。
- README 写清楚本地启动方式。

## 核心理解

### 前后端职责

- 前端负责页面、交互、表单输入、请求后端 API。
- 后端负责接口、数据库、模型调用、API Key 保护。
- 本地开发时前端和后端是两个独立服务。

### Next.js

- React 是 UI 库，Next.js 是基于 React 的应用框架。
- Next.js 提供路由、构建、开发服务器、服务端渲染、静态生成、部署约定等工程能力。
- 当前项目选择 Next.js，是因为它适合 AI Web App / SaaS Demo / 简历项目，也方便后续扩展页面和部署。

### FastAPI

- FastAPI 用来定义后端 API。
- `uvicorn` 是 ASGI Server，负责监听端口、接收请求、交给 FastAPI 处理。
- `GET /health` 是健康检查接口，用来确认后端服务正常。

## 关键文件

- `frontend/app/layout.tsx`：全局布局。
- `frontend/app/page.tsx`：首页。
- `frontend/app/globals.css`：全局样式。
- `backend/app/main.py`：FastAPI 应用入口。
- `.nvmrc`：声明 Node.js 版本。
- `.gitignore`：忽略依赖、构建缓存、虚拟环境、数据库等本地文件。

## 前端基础概念

### `.tsx`

`.tsx` 表示 TypeScript + JSX。React 组件通常返回 TSX，用来描述页面 UI。

### `layout.tsx` 和 `page.tsx`

- `app/page.tsx` 自动对应首页 `/`。
- `app/layout.tsx` 自动作为布局，不需要手动 import `page.tsx`。
- Next.js 会把页面作为 `children` 传给布局。

### Tailwind CSS

- Tailwind 是 utility-first / 原子化 CSS 框架。
- `tailwind.config.ts` 里的 `content` 决定 Tailwind 扫描哪些文件生成 class。
- `theme.extend` 可以扩展项目自定义颜色等 token。
- `@tailwind base/components/utilities` 是 Tailwind 全局样式入口。

### `.next`

`.next` 是 Next.js 自动生成的构建/运行缓存目录，不需要手写或提交。

## 环境与命令

### `.nvmrc`

`.nvmrc` 声明项目期望的 Node.js 版本。本项目使用 Node 20。

在 Git Bash / nvm-windows 场景中，`nvm use` 可能不能自动读取 `.nvmrc`，所以 README 中显式写：

```bash
nvm use 20
```

### `npm install` 和 `npm ci`

- `npm install`：用于首次创建项目、新增依赖、升级依赖，可能更新 `package-lock.json`。
- `npm ci`：严格按 `package-lock.json` 干净安装，适合 clone 后安装、CI 构建、验证可复现环境。

### `--prefer-offline`

`npm ci --prefer-offline` 表示优先使用本地 npm 缓存，缓存缺失时仍可联网下载。

### CI/CD

- CI：持续集成，代码提交后自动安装依赖、构建、测试。
- CD：持续交付/部署，检查通过后自动发布到环境。

### Python 后端启动命令

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
uvicorn app.main:app --reload
```

- `python3 -m venv .venv`：创建虚拟环境。
- `source .venv/bin/activate`：激活虚拟环境。
- `python -m pip install -r requirements.txt`：用当前 Python 对应的 pip 安装依赖。
- `uvicorn app.main:app --reload`：启动 FastAPI，开发时自动重载。

## 阶段卡点

- WSL 中创建 Python 虚拟环境时可能缺少 `python3.12-venv`。
- `sudo apt install python3.12-venv` 是用 Ubuntu 系统包管理器安装创建虚拟环境所需组件。
- `/mnt/c` 下运行项目可能出现文件监听、缓存和 SQLite 写入问题，后续已迁移到 WSL 原生目录。

## 阶段复盘

- 日期：2026-06-29
- 已完成：前端 Next.js 骨架、后端 FastAPI 骨架、`/health`、README。
- 当前理解：先完成可运行的前后端分离骨架，再逐步接数据库和 LLM。
