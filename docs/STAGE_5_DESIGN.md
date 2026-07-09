# 阶段 5 设计：实现流式输出

## 目标

阶段 5 的目标是把阶段 4 的“一次性返回 AI 报告”升级为“边生成边展示”。

用户提交表单后，前端应逐步看到 AI 复盘报告内容；生成完成后，后端保存完整报告到 SQLite，前端刷新历史列表并选中新记录。

## 范围

- 后端新增流式创建接口。
- 后端调用 OpenAI-compatible streaming Chat Completions。
- 前端逐段读取流式内容并实时展示。
- 流式完成后保存完整记录到 SQLite。
- 生成成功后刷新历史列表并展示新记录详情。
- 生成失败时保留表单内容。

## 暂不做

- 正式 Markdown 渲染。
- 复杂重试机制。
- 中途取消生成。
- 多模型选择 UI。
- Agent / Tool Calling。

## 接口设计

新增接口：

```text
POST /api/reflections/stream
```

请求体与阶段 4 创建接口一致，不包含 `ai_report`：

```json
{
  "session_id": "string",
  "event_text": "string",
  "emotion_tags": ["焦虑", "委屈"],
  "emotion_intensity": 7,
  "automatic_thoughts": "string",
  "body_reaction": "string",
  "focus_area": "综合分析"
}
```

响应使用 Server-Sent Events 风格文本流：

```text
event: delta
data: {"content":"# 情绪复盘报告"}

event: delta
data: {"content":"\\n\\n## 1. 事件简要总结"}

event: done
data: {"record_id":1}
```

错误事件：

```text
event: error
data: {"message":"LLM API request failed..."}
```

## 为什么使用 SSE 风格

SSE 风格格式简单，适合“服务端持续推送文本片段给浏览器”的场景。

阶段 5 不引入 WebSocket，原因是当前需求是单向流：

```text
后端 -> 前端
```

不需要实时双向通信。

## 后端设计

新增能力：

- `llm_client.py` 增加流式生成函数。
- `reflections.py` 增加 `/stream` 路由。
- 流式过程中累积完整报告文本。
- 模型流结束后创建 `ReflectionRecord` 并保存数据库。
- 保存成功后发送 `done` 事件，返回 `record_id`。

关键流程：

```text
接收 ReflectionCreate
-> 调用模型 streaming API
-> 每收到一段 content 就 yield delta 事件
-> 同时 append 到 full_report
-> 模型结束
-> full_report 保存到 SQLite
-> yield done 事件，带 record_id
```

## 前端设计

前端新增状态：

- `streamingReport`：当前实时生成中的报告文本。
- `isStreaming`：是否正在流式生成。

提交流程：

```text
用户提交表单
-> 前端请求 /api/reflections/stream
-> 读取 response.body
-> 遇到 delta 事件就追加到 streamingReport
-> 遇到 done 事件就刷新历史列表，并查询/选中新记录
-> 成功后清空表单
-> 失败时保留表单
```

展示策略：

- 生成中优先展示 `streamingReport`。
- 生成完成后展示数据库返回的详情记录。
- 暂时用 `whitespace-pre-wrap` 保留换行，不做 Markdown 渲染。

## 错误处理

- 缺少 `LLM_API_KEY`：返回 `error` 事件。
- 模型 API 报错：返回 `error` 事件，包含安全截断后的错误摘要。
- 前端读取流失败：显示错误提示，并保留表单内容。
- 保存数据库失败：返回 `error` 事件。

## 与阶段 4 的关系

阶段 4 保留非流式创建接口：

```text
POST /api/reflections
```

阶段 5 新增流式接口：

```text
POST /api/reflections/stream
```

这样可以保留一个简单、可回退的非流式接口，也方便对比学习。

## 验收

- 前端提交表单后能看到 AI 内容逐步出现。
- 流式完成后后端保存完整报告到 SQLite。
- 历史列表刷新后能看到新记录。
- 新记录详情能展示完整 AI 报告。
- 生成失败时表单内容不清空。
- 后端缺少 API Key 或模型报错时，前端能显示错误。
- 前端 `npm run build` 通过。
- 后端 Python 语法检查通过。
