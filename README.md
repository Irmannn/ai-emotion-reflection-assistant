# AI Emotion Reflection Assistant

一个面向学习和简历展示的 AI 情绪复盘助手 MVP。

项目目标是完成一个最小 AI 全栈闭环：

- Next.js + React + TypeScript 前端
- FastAPI 后端
- SQLite 数据库存储
- 后端调用大模型 API
- 流式输出 AI 复盘报告
- 历史记录和反馈保存

## 当前阶段

项目按阶段推进，当前处于阶段 3：前端表单和历史记录。

- 创建前端 Next.js 项目结构
- 创建后端 FastAPI 项目结构
- 提供后端健康检查接口
- 编写本地启动说明
- 接入 SQLite 数据库
- 实现复盘记录基础 CRUD 接口
- 实现前端情绪复盘表单
- 实现前端历史记录列表、详情和删除

## 学习目标

这个项目用于从前端开发逐步转型到 LLM / Agent 应用工程师。第一阶段重点不是复杂 Agent 能力，而是先完成一个可运行、可迭代、可展示的 AI 产品闭环。

## 项目资料

- `docs/PRD.md`：产品需求文档
- `docs/DEVELOPMENT_PLAN.md`：阶段化开发要求
- `LEARNING_NOTES.md`：学习疑问、阶段复盘和项目笔记
- `learing-road-overview.png`：学习路线图
- `tk-learning-method.png`：自学方法参考

## 项目结构

```text
.
├── frontend/               # Next.js 前端
├── backend/                # FastAPI 后端
├── docs/                   # PRD 和阶段开发计划
├── AGENTS.md               # Codex 协作规则
├── LEARNING_NOTES.md       # 学习笔记
└── README.md
```

## 环境要求

- Node.js 20+
- npm 10+
- Python 3.11+
- pip / venv

当前前端和后端是两个独立服务，本地开发时需要分别启动。

## 启动前端

```bash
cd frontend
nvm use 20
npm install
npm run dev
```

浏览器打开：

```text
http://localhost:3000
```

## 启动后端

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
uvicorn app.main:app --reload
```

健康检查：

```bash
curl http://localhost:8000/health
```

预期返回：

```json
{"status":"ok"}
```

## 阶段 1 验收标准

- 前端页面可以通过 `http://localhost:3000` 打开
- 后端 `GET /health` 返回 `{"status":"ok"}`
- README 写清楚前后端启动方式

## 阶段 2 验收标准

- 后端启动时可以自动初始化 SQLite 数据库
- 可以创建测试复盘记录
- 可以查询历史记录列表
- 可以查询历史记录详情
- 可以提交反馈
- 可以删除历史记录
- 不同 `session_id` 之间的数据不会互相泄露

## 阶段 3 验收标准

- 用户可以填写情绪复盘表单
- 前端可以生成并保存 `session_id`
- 表单提交后，后端 SQLite 中能保存记录
- 历史记录列表能展示当前 `session_id` 的记录
- 点击历史记录能展示完整详情
- 用户可以删除历史记录
- 刷新页面后，`session_id` 保持不变

## 当前本机环境备注

- 仓库包含 `.nvmrc`，前端应使用 Node.js 20。
- 如果当前 shell 默认是 Node.js 16，请先执行 `nvm use 20`。
- 如果创建 Python 虚拟环境时报 `ensurepip is not available`，需要先安装系统包 `python3.12-venv`。
