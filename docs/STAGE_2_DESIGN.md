# 阶段 2 设计方案：SQLite 数据库

## 1. 阶段目标

阶段 2 的目标是让后端具备持久化能力：

- 接入 SQLite
- 创建 `reflection_records` 表
- 实现数据库初始化
- 实现历史记录基础 CRUD 接口
- 通过 `session_id` 隔离不同用户的匿名数据

阶段 2 不接入前端页面、不调用大模型、不实现流式输出。

## 2. 技术选型

使用：

- SQLite
- SQLModel

选择原因：

- SQLite 是本地文件数据库，不需要单独安装数据库服务，适合 MVP 阶段。
- SQLModel 基于 SQLAlchemy 和 Pydantic，和 FastAPI 配合自然，适合初学阶段理解 ORM、数据模型和接口模型。

## 3. 后端目录拆分

阶段 2 后端建议拆分为：

```text
backend/app/
  __init__.py
  main.py
  database.py
  models.py
  schemas.py
  routers/
    __init__.py
    reflections.py
```

职责说明：

- `database.py`：数据库连接、Session 创建、初始化表。
- `models.py`：数据库表模型。
- `schemas.py`：API 请求和响应结构。
- `routers/reflections.py`：复盘记录相关接口。
- `main.py`：创建 FastAPI app，挂载路由。

## 4. 数据表设计

表名：

```text
reflection_records
```

字段：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `id` | integer | 主键 |
| `session_id` | string | 匿名会话 ID |
| `event_text` | text | 事件描述 |
| `emotion_tags` | string | 情绪标签，阶段 2 先用逗号拼接字符串保存 |
| `emotion_intensity` | integer | 情绪强度，范围 1-10 |
| `automatic_thoughts` | text | 自动想法 |
| `body_reaction` | text | 身体反应 |
| `focus_area` | string | 重点分析方向 |
| `ai_report` | text | AI 复盘报告，阶段 2 可使用测试内容 |
| `feedback` | string, nullable | 用户反馈，可为空 |
| `created_at` | datetime | 创建时间 |
| `updated_at` | datetime | 更新时间 |

## 5. 接口设计

### 5.1 创建测试记录

阶段 2 需要能创建测试数据，用于验证 CRUD。

```http
POST /api/reflections
```

请求体：

```json
{
  "session_id": "demo-session",
  "event_text": "今天和同事沟通不顺",
  "emotion_tags": ["焦虑", "委屈"],
  "emotion_intensity": 7,
  "automatic_thoughts": "是不是我表达能力很差",
  "body_reaction": "胸闷",
  "focus_area": "综合分析",
  "ai_report": "测试复盘报告"
}
```

说明：

- 正式项目中记录会在生成 AI 报告后保存。
- 阶段 2 先提供创建接口，方便独立验证数据库和 CRUD。

### 5.2 获取历史记录列表

```http
GET /api/reflections?session_id=demo-session
```

返回：

```json
[
  {
    "id": 1,
    "event_summary": "今天和同事沟通不顺",
    "emotion_tags": "焦虑,委屈",
    "emotion_intensity": 7,
    "feedback": null,
    "created_at": "2026-07-01T10:00:00"
  }
]
```

### 5.3 获取历史记录详情

```http
GET /api/reflections/{id}?session_id=demo-session
```

只允许获取当前 `session_id` 对应的记录。

### 5.4 删除历史记录

```http
DELETE /api/reflections/{id}?session_id=demo-session
```

只允许删除当前 `session_id` 对应的记录。

### 5.5 提交反馈

```http
POST /api/reflections/{id}/feedback
```

请求体：

```json
{
  "session_id": "demo-session",
  "feedback": "helpful"
}
```

`feedback` 可选值：

- `helpful`
- `not_helpful`

## 6. session_id 数据隔离

第一版不做登录系统。

前端后续会生成匿名 `session_id`，后端所有查询、详情、删除、反馈操作都必须带 `session_id`。

后端规则：

- 列表只返回当前 `session_id` 的记录。
- 详情只允许读取当前 `session_id` 的记录。
- 删除只允许删除当前 `session_id` 的记录。
- 反馈只允许更新当前 `session_id` 的记录。

这样可以避免用户通过 ID 访问或修改其他匿名用户的数据。

## 7. 验收方式

阶段 2 完成后，需要验证：

- 后端启动时可以自动初始化 SQLite 数据库。
- 可以创建测试记录。
- 可以查询历史记录列表。
- 可以查询历史记录详情。
- 可以提交 `helpful` / `not_helpful` 反馈。
- 可以删除历史记录。
- 不同 `session_id` 之间的数据不会互相泄露。

可使用：

```text
http://localhost:8000/docs
```

或 `curl` 命令进行验证。

## 8. 暂不做范围

阶段 2 不做：

- 前端表单联调
- LLM API 调用
- 流式输出
- RAG
- Agent 工作流
- 用户登录
- 权限系统
- 生产级数据库迁移工具
