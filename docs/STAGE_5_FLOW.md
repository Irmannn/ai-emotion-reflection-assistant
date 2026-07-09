# 阶段 5 流式输出流程图

## 总链路

```mermaid
flowchart TD
  A[用户填写复盘表单] --> B[page.tsx 调用 streamCreateReflection]
  B --> C[api.ts POST /api/reflections/stream]
  C --> D[reflections.py stream_create_reflection]
  D --> E[llm_client.py stream_reflection_report]
  E --> F[模型服务 Streaming Chat Completions]

  F --> G[模型返回一段 delta content]
  G --> E
  E --> H[reflections.py yield SSE delta 事件]
  H --> I[api.ts 读取 response.body]
  I --> J[调用 onDelta 追加到 streamingReport]
  J --> K[页面实时展示生成中的 AI 报告]

  F --> L[模型返回 DONE]
  L --> M[reflections.py 拼接 chunks 得到完整 ai_report]
  M --> N[保存 ReflectionRecord 到 SQLite]
  N --> O[yield SSE done 事件 record_id]
  O --> P[api.ts 返回 record_id]
  P --> Q[page.tsx 刷新历史列表并拉取详情]
  Q --> R[页面展示完整复盘详情]

  E --> S[模型/API 异常]
  D --> T[yield SSE error 事件]
  S --> T
  T --> U[api.ts throw Error]
  U --> V[page.tsx 显示错误并保留表单内容]
```

## 前端读取流细节

```mermaid
flowchart TD
  A[fetch /api/reflections/stream] --> B{response.ok?}
  B -- 否 --> C[readErrorMessage 读取错误]
  C --> D[throw Error]

  B -- 是 --> E{response.body 存在?}
  E -- 否 --> D
  E -- 是 --> F[response.body.getReader]
  F --> G[创建 TextDecoder 和 buffer]

  G --> H[reader.read 读取一个二进制块]
  H --> I{done?}
  I -- 否 --> J[TextDecoder 解码为字符串]
  J --> K[追加到 buffer]
  K --> L[按空行 split 成 messages]
  L --> M[messages.pop 保存可能不完整的最后一段]
  M --> N[逐条 handleStreamMessage]

  N --> O{event 类型}
  O -- delta --> P[JSON.parse data 取 content]
  P --> Q[handlers.onDelta content]
  Q --> H

  O -- done --> R[保存 result record_id]
  R --> H

  O -- error --> D

  I -- 是 --> S[decoder.decode 收尾]
  S --> T{buffer 还有内容?}
  T -- 是 --> N
  T -- 否 --> U{result 存在?}
  U -- 否 --> D
  U -- 是 --> V[return record_id]
```

## 关键理解

- 后端模型流和前端接口流不是同一个流，但后端把模型流转成了前端可读的 SSE 风格文本流。
- `delta` 用于实时展示内容，`done` 用于告诉前端保存完成，`error` 用于告诉前端生成失败。
- 前端不能对流式响应使用 `response.json()`，需要用 `response.body.getReader()` 一块一块读取。
- `buffer` 的作用是保存未完整到达的 SSE 事件，避免网络分块导致解析错误。
