# 阶段 3 设计方案：前端表单和历史记录

## 1. 阶段目标

阶段 3 的目标是让前端和阶段 2 的后端 CRUD 接口完成联调：

- 实现情绪复盘表单
- 前端生成并保存 `session_id`
- 调用后端接口创建测试复盘记录
- 展示历史记录列表
- 展示历史记录详情
- 删除历史记录

阶段 3 不接入大模型，不实现流式输出，不做 Markdown 渲染。

## 2. 页面策略

阶段 3 先采用单页实现，继续使用：

```text
frontend/app/page.tsx
```

页面分成三块：

- 情绪复盘表单
- 历史记录列表
- 选中记录详情

选择单页的原因：

- 阶段 3 重点是前后端联调，不是路由系统。
- 单页更容易理解表单、列表、详情之间的状态变化。
- 等 MVP 后续体验完善时，再考虑拆页面或增加路由。

## 3. session_id 方案

第一版不做登录系统，前端使用匿名 `session_id` 隔离用户数据。

前端首次加载时：

1. 检查 `localStorage` 是否已有 `session_id`。
2. 如果没有，则使用 `crypto.randomUUID()` 生成。
3. 保存到 `localStorage`。
4. 后续所有请求都带上该 `session_id`。

建议 localStorage key：

```text
emotion_reflection_session_id
```

## 4. 表单字段

阶段 3 表单字段对应 PRD：

| 字段 | 说明 |
| --- | --- |
| `event_text` | 事件描述 |
| `emotion_tags` | 情绪标签，可多选 |
| `emotion_intensity` | 情绪强度，1-10 |
| `automatic_thoughts` | 自动想法 |
| `body_reaction` | 身体反应 |
| `focus_area` | 重点分析方向 |

阶段 3 暂不接入 LLM，因此提交给后端测试创建接口时，暂时使用固定测试报告：

```text
阶段 3 前端联调测试报告
```

该字段会作为 `ai_report` 传给后端。阶段 4 接入大模型后，再改成后端生成。

## 5. API 调用

阶段 3 使用阶段 2 已实现的接口：

```text
POST   /api/reflections
GET    /api/reflections?session_id=xxx
GET    /api/reflections/{id}?session_id=xxx
DELETE /api/reflections/{id}?session_id=xxx
```

暂不优先实现反馈交互。反馈接口已在后端实现，可在后续阶段补充按钮和联调。

## 6. 前端目录拆分

阶段 3 建议新增：

```text
frontend/app/components/
  ReflectionForm.tsx
  HistoryList.tsx
  ReflectionDetail.tsx

frontend/app/lib/
  api.ts
  session.ts

frontend/app/types/
  reflection.ts
```

职责说明：

- `ReflectionForm.tsx`：情绪复盘表单。
- `HistoryList.tsx`：历史记录列表。
- `ReflectionDetail.tsx`：选中记录详情。
- `api.ts`：封装前端请求后端的 fetch 方法。
- `session.ts`：生成和读取匿名 `session_id`。
- `reflection.ts`：前端使用的 TypeScript 类型定义。
- `page.tsx`：组装页面、管理主要状态、协调组件和 API 调用。

## 7. 状态管理

阶段 3 不引入 Zustand、Redux 等额外状态管理库。

仅使用 React 内置状态能力：

- `useState`
- `useEffect`

主要状态：

- `sessionId`
- `records`
- `selectedRecord`
- `isLoading`
- `isSubmitting`
- `error`

## 8. 本地运行

启动后端：

```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload
```

启动前端：

```bash
cd frontend
nvm use 20
npm run dev
```

打开：

```text
http://localhost:3000
```

## 9. 验收标准

阶段 3 完成后，需要验证：

- 用户可以填写情绪复盘表单。
- 前端可以生成并保存 `session_id`。
- 表单提交后，后端 SQLite 中能保存记录。
- 历史记录列表能展示当前 `session_id` 的记录。
- 点击历史记录能展示完整详情。
- 用户可以删除历史记录。
- 删除后列表和详情状态能正确更新。
- 刷新页面后，`session_id` 保持不变，历史记录仍可查询。
- 前端和后端接口能正常联调。

## 10. 暂不做范围

阶段 3 不做：

- LLM API 调用
- 流式输出
- Markdown 渲染
- 复杂表单校验
- 用户登录
- RAG
- Agent 工作流
- 多页面路由
- 生产级 UI 完善
