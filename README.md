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

项目按阶段推进，当前处于阶段 5：实现流式输出。

- 创建前端 Next.js 项目结构
- 创建后端 FastAPI 项目结构
- 提供后端健康检查接口
- 编写本地启动说明
- 接入 SQLite 数据库
- 实现复盘记录基础 CRUD 接口
- 实现前端情绪复盘表单
- 实现前端历史记录列表、详情和删除
- 后端读取大模型环境变量
- 后端调用大模型生成 Markdown 复盘报告
- 前端提交后实时展示 AI 流式输出
- 流式完成后保存完整报告到 SQLite

## 学习目标

这个项目用于从前端开发逐步转型到 LLM / Agent 应用工程师。第一阶段重点不是复杂 Agent 能力，而是先完成一个可运行、可迭代、可展示的 AI 产品闭环。

## 项目资料

- `docs/PRD.md`：产品需求文档
- `docs/DEVELOPMENT_PLAN.md`：阶段化开发要求
- `docs/STAGE_5_FLOW.md`：阶段 5 流式输出流程图
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
cp .env.example .env
uvicorn app.main:app --reload
```

首次接入大模型前，需要编辑 `backend/.env`：

```env
LLM_API_KEY=你的模型服务 API Key
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4o-mini
LLM_TIMEOUT_SECONDS=60
```

`LLM_BASE_URL` 使用 OpenAI-compatible endpoint。你可以根据所用服务商改成 DeepSeek、OpenAI 或通义千问兼容接口地址。

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

## 阶段 4 验收标准

- 后端可以从 `.env` 读取大模型配置
- API Key 不暴露到前端代码
- 前端提交表单后，后端可以生成 AI 复盘报告
- AI 报告保存到 SQLite
- 历史详情可以展示 AI 报告
- 缺少 `LLM_API_KEY` 时，前端可以看到明确错误提示

## 阶段 5 验收标准

- 前端提交表单后能看到 AI 内容逐步出现
- 流式完成后后端保存完整报告到 SQLite
- 历史列表刷新后能看到新记录
- 新记录详情能展示完整 AI 报告
- 生成失败时表单内容不清空
- 后端缺少 API Key 或模型报错时，前端能显示错误

## 当前本机环境备注

- 仓库包含 `.nvmrc`，前端应使用 Node.js 20。
- 如果当前 shell 默认是 Node.js 16，请先执行 `nvm use 20`。
- 如果创建 Python 虚拟环境时报 `ensurepip is not available`，需要先安装系统包 `python3.12-venv`。
- 如果 Next.js dev server 在 `/mnt/c` 下出现 `.next` module/chunk 报错，先确认 Node.js 20，必要时删除 `.next` 后重启。
