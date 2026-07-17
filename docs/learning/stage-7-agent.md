# 阶段 7 学习笔记：Agent / Tool Calling

## Schemas 数据结构

### `AgentToolCallView` 和 `ToolExecutionResult` 的区别

这两个结构都描述一次工具调用，但使用场景不同。

`ToolExecutionResult` 是后端内部使用的完整工具执行结果：

- `tool_name`：调用了哪个工具。
- `arguments`：调用工具时传入的参数，是工具输入。
- `content`：工具执行后的完整返回内容，是工具输出，会继续传回模型用于推理。
- `result_summary`：工具结果摘要。
- `status`：工具执行状态。
- `error_message`：工具错误信息。

`AgentToolCallView` 是返回给前端展示的工具调用摘要：

- 包含 `tool_name`、`arguments`、`result_summary`、`status`、`error_message`。
- 不包含 `content`，避免把完整历史记录或较长工具结果直接暴露在前端工具日志里。

可以理解为：

```text
ToolExecutionResult = 后端和模型看的完整版本
AgentToolCallView = 前端用户看的摘要版本
```

`arguments` 是工具输入，`content` 是工具输出。

`dict[str, Any]` 表示这是一个 Python 字典，key 是字符串，value 可以是任意类型。因为不同工具的参数结构不同，例如：

```json
{ "limit": 5 }
{ "query": "焦虑", "limit": 5 }
{ "record_id": 12 }
```


## `agent_client.py` 的职责

`agent_client.py` 是模型 API 和本地工具执行器之间的调度器。

它自己不直接查数据库，真正查数据库的是 `tools.py`；它也不负责前端展示，前端展示的是 `AgentPanel.tsx`。

它负责的核心流程是：

```text
用户问题
-> 发给模型，并附带 tools 定义
-> 模型返回 tool_calls
-> 后端执行工具
-> 把工具结果 role=tool 发回模型
-> 模型生成最终回答
```

关键理解：

```text
模型 API 负责判断是否要调用工具
FastAPI 后端负责真正执行工具
agent_client.py 负责把模型 API 和工具执行器串起来
```

## `messages` 在 Tool Calling 中的变化

Agent Loop 中的 `messages` 是发给模型的上下文数组，会随着工具调用逐步追加内容。

一开始只有系统提示词和用户问题：

```json
[
  {
    "role": "system",
    "content": "你是一个情绪复盘行动助手..."
  },
  {
    "role": "user",
    "content": "帮我找最近焦虑相关的复盘"
  }
]
```

第一次请求模型后，如果模型决定调用工具，会返回一条 `role=assistant` 的消息，里面带 `tool_calls`：

```json
{
  "role": "assistant",
  "content": null,
  "tool_calls": [
    {
      "id": "call_001",
      "type": "function",
      "function": {
        "name": "search_reflections",
        "arguments": "{\"query\":\"焦虑\",\"limit\":5}"
      }
    }
  ]
}
```

后端会把这条 assistant 工具调用消息追加回 `messages`，再执行工具。

工具执行完成后，后端再追加一条 `role=tool` 的消息，把工具结果传回模型：

```json
{
  "role": "tool",
  "tool_call_id": "call_001",
  "content": "{\"records\":[{\"id\":3,\"event_summary\":\"直播前担心表现不好\"}],\"count\":1}"
}
```

第二次请求模型时，模型就能看到：

```text
user: 用户问题
assistant: 我想调用 search_reflections
tool: 这是 search_reflections 的执行结果
```

然后模型返回最终 `role=assistant` 回答，不再带 `tool_calls`，Agent Loop 结束。

## `json.dumps` 和 `json.loads` 的区分

`json.dumps`：把 Python 对象转换成 JSON 字符串。可以理解成把 Python 数据“丢出去 / dump 成字符串”。

```py
json.dumps({"query": "焦虑"}, ensure_ascii=False)
```

结果是字符串：

```json
"{\"query\": \"焦虑\"}"
```

`json.loads`：把 JSON 字符串加载成 Python 对象。可以理解成从字符串里“load 回 Python 数据”。

```py
json.loads("{\"query\": \"焦虑\"}")
```

结果是 Python 字典：

```py
{"query": "焦虑"}
```

注意：`dumps` 和 `loads` 都是 Python 的 `json` 模块方法；JSON 本身是一种字符串格式，不是 Python 对象。

## 普通回答和 Tool Calling 中的 `role=assistant`

不使用 Agent、普通 LLM 调用时，模型返回的消息通常是：

```json
{
  "role": "assistant",
  "content": "这是模型生成的回答..."
}
```

使用 Agent / Tool Calling 时，模型返回的消息仍然是 `role=assistant`，只是它可能不直接返回最终内容，而是返回 `tool_calls`：

```json
{
  "role": "assistant",
  "content": null,
  "tool_calls": [
    {
      "id": "call_001",
      "type": "function",
      "function": {
        "name": "search_reflections",
        "arguments": "{\"query\":\"焦虑\"}"
      }
    }
  ]
}
```

所以关键区别不是 `role` 变了，而是：

```text
普通 LLM：assistant 返回 content
Tool Calling：assistant 可能返回 tool_calls
```

工具执行结果才是 `role=tool`。这条 `role=tool` 消息不是模型生成的，而是后端执行工具后追加进 `messages`，再发回模型看的。

## `tools.py` 补充概念

### `limit` 的含义

`limit` 表示最多返回多少条记录。比如 `limit=5` 就是最多返回 5 条历史复盘。后端会用 `_clamp_limit` 把它限制在 1 到 10 之间，避免模型传入过大的数量导致查询结果太长。

### 为什么 `get_reflection_detail_tool` 查询 `ReflectionReference`

`ReflectionReference` 是阶段 6 RAG 保存的“复盘记录使用过哪些知识库参考资料”。查复盘详情时顺便查它，是为了让 Agent 不只看到用户复盘和 AI 报告，还能看到这条报告当时引用了哪些 RAG 资料。

### `**_reflection_summary(record)` 的作用

`**` 用在字典里表示展开字典。`**_reflection_summary(record)` 会把摘要字段展开到新的字典中，然后继续追加详情字段。

### `isoformat()` 的作用

`record.created_at.isoformat()` 会把 Python 的 `datetime` 时间对象转换成 ISO 格式字符串，方便 JSON 返回和前端展示。

### `_matched_reason` 的匹配逻辑

`_matched_reason` 主要匹配字段值，不是匹配字段名。比如 query 是“焦虑”，会去事件描述、情绪标签、自动想法、身体反应、AI 报告等字段内容里查有没有“焦虑”。命中后返回字段名作为说明，例如“情绪标签匹配 焦虑”。

### `fields.items()` 得到什么

`fields.items()` 会把字典转换成一组 key/value 对，用于循环：

```py
for label, value in fields.items():
```

这里 `label` 是字段中文名，比如“情绪标签”；`value` 是对应字段内容，比如“焦虑,委屈”。

### `min(max(limit, 1), 10)` 的作用

这是把 `limit` 框定在 1 到 10 之间：

```text
max(limit, 1)  先保证不小于 1
min(..., 10)   再保证不大于 10
```

所以 limit 小于 1 会变成 1，大于 10 会变成 10。

### 工具返回内容主要给模型看

`tools.py` 里的工具函数返回内容，主要是给模型继续推理使用，不是直接原样展示给用户。

例如 `get_reflection_detail_tool` 返回 `ai_report`、`references` 等较完整内容，是为了让模型基于这些信息生成最终回答。

前端展示的是 `AgentToolCallView` 里的工具调用摘要，例如“查询到 3 条复盘记录”，而不是完整工具返回的 `content`。

## `tool_runner.py` 补充概念

### `Callable` 是什么

`Callable` 是 Python 的类型声明，表示“可调用对象”，通常可以理解为函数。

例如：

```py
def hello() -> str:
    return "hi"
```

`hello` 就是一个 `Callable`，因为可以执行：

```py
hello()
```

### `Callable[..., dict[str, Any]]` 的含义

```py
ToolFunction = Callable[..., dict[str, Any]]
```

表示定义一个类型别名：

```text
ToolFunction = 参数不固定、返回 dict[str, Any] 的函数
```

其中：

- `Callable`：可调用对象，通常是函数。
- `...`：参数列表不固定。
- `dict[str, Any]`：返回值是字典，key 是字符串，value 可以是任意类型。

这里使用 `...` 是因为不同工具函数参数不同：

```py
list_reflections_tool(session_id, session, limit=5)
search_reflections_tool(session_id, session, query, limit=5)
get_reflection_detail_tool(session_id, session, record_id)
```

但它们返回值都可以统一看作：

```py
dict[str, Any]
```

### `tools.py` 和 `tool_runner.py` 的区别

`tools.py` 负责定义工具：

- 定义给模型看的工具 schema：`TOOL_DEFINITIONS`。
- 编写真实工具函数：`list_reflections_tool`、`search_reflections_tool`、`get_reflection_detail_tool`。
- 查询数据库并返回工具结果。

`tool_runner.py` 负责执行工具：

- 接收模型返回的 `tool_name` 和 `arguments`。
- 从 `TOOL_REGISTRY` 白名单里找到对应工具函数。
- 解析 arguments。
- 注入后端可信的 `session_id` 和数据库 `session`。
- 执行工具函数。
- 捕获错误。
- 写入工具调用日志。

一句话：

```text
tools.py 说明“有哪些工具、工具怎么做事”
tool_runner.py 负责“模型点名要用工具时，安全地找到并执行它”
```

## `AgentPanel.tsx` 补充概念

### `textarea rows={3}`

`rows={3}` 表示 textarea 默认显示 3 行文本高度。

它不是限制用户最多只能输入 3 行，只是控制初始可见高度。用户输入更多内容时，文本框可能滚动或按 CSS 样式展示。

### 为什么 `onSubmit` 返回 `Promise<void>`

`AgentPanel` 的 `onSubmit` 类型是：

```ts
onSubmit: (message: string) => Promise<void>;
```

因为提交后会触发异步流程：

```text
调用后端 API
等待模型返回
更新 result 状态
处理错误
切换 loading 状态
```

`Promise` 表示这是异步函数。

`void` 表示这个函数不把结果返回给 `AgentPanel` 使用。真正的结果会在父组件 `page.tsx` 中通过 state 更新。

所以：

```tsx
await onSubmit(trimmedMessage);
```

意思是等待父组件完成异步请求和状态更新，而不是从 `onSubmit` 里拿返回值。

## TypeScript `Record` 和 Python `dict` 的类比

`Record` 是 TypeScript 的工具类型，用来描述对象的 key 和 value 类型。

```ts
Record<string, unknown>
```

可以理解成：

```text
这是一个对象
key 是 string
value 是 unknown
```

它和 Python 的 `dict` 很像：

```text
TypeScript: Record<string, unknown>
Python:     dict[str, Any]
```

它们都可以表达“key 是字符串，value 可以是多种类型”的参数对象。

区别是：

```text
Record 是 TypeScript 的类型工具，只用于前端类型检查。
dict 是 Python 的真实数据结构，运行时真的存在。
```

在本项目里，它们表达的是同一个数据概念：工具调用参数对象。

```ts
arguments: Record<string, unknown>
```

```py
arguments: dict[str, Any]
```
