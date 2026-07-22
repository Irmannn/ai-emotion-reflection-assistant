# 阶段 9：LangChain 组件化学习笔记

## 同步数据库工具与异步 RAG 工具

### 结论

“同步还是异步”不由数据是否来自外部决定，而由代码采用的调用方式和底层驱动决定。

### 当前 `tool_runner` 为什么是同步的

当前 `tool_runner` 统一执行的工具包括：

- `list_reflections`：查询项目自己的 SQLite 数据库。
- `search_reflections`：按关键词查询 SQLite 数据库。
- `get_reflection_detail`：查询一条 SQLite 复盘详情。

这些工具都是普通 `def` 函数，内部使用同步的 SQLModel / SQLite 调用，例如 `session.exec(...)`。调用时需要等待查询完成后才能继续当前执行路径，因此它们是同步工具。`tool_runner` 当前不调用模型 API 或其他外部 HTTP API。

### 为什么后续知识库检索工具需要异步

RAG 检索通常需要先调用 Embedding API。该步骤是网络 I/O，应使用 `await` 异步等待：等待 API 返回时，FastAPI 的事件循环可以处理其他请求，而不是一直阻塞。

因此，阶段 9 若为 Agent 增加“搜索内置知识库”工具，工具执行器需要同时支持：

- 同步本地数据库工具。
- 异步 RAG 工具：Embedding API 请求加本地向量检索。

本地数据库也可以使用异步驱动和异步会话；当前 MVP 为了保持 SQLite + SQLModel 的代码易理解，使用同步数据库访问。

## 工具消息：内存上下文与数据库持久化

### 阶段 8 的原生 `role="tool"`

阶段 8 中，模型提出工具调用意图后，后端执行真实工具，并在当前请求的 `request_messages` 列表中追加原生 OpenAI-compatible 消息：

```python
{
    "role": "tool",
    "tool_call_id": "call_...",
    "content": "工具执行结果 JSON",
}
```

它用于下一次模型 API 请求，让模型读取工具结果后生成最终回答。该字典只存在于当前 Agent Loop 的内存中，不会保存为 `AgentMessage` 数据库记录。

### 阶段 9 的 LangChain `ToolMessage`

阶段 9 将上述原生字典替换为 LangChain 对象：

```python
ToolMessage(content="工具执行结果 JSON", tool_call_id="call_...")
```

它们承担同一职责：都是将后端真实执行的工具结果交回模型。当前一轮的模型消息会依次包含 `SystemMessage`、`HumanMessage`、模型返回的 `AIMessage`，以及 `ToolMessage`。

### 什么会保存到数据库

项目不会把完整工具结果作为 `AgentMessage(role="tool")` 保存。每轮对话会保存：

```text
AgentMessage
├─ user：用户输入
└─ assistant：最终自然语言回答

AgentToolCallLog
├─ 工具名
├─ 参数 JSON
├─ 状态
├─ 结果摘要
└─ 错误信息
```

Chat UI 展示的“工具调用成功 / 检索到 N 条资料”来自 `AgentToolCallLog` 的摘要，不是完整 `ToolMessage` 内容。这个设计不是因为 UI 没展示就不保存，而是项目刻意避免持久化可能很长的原始工具结果。

下一轮对话会从 `AgentMessage` 中读取已完成的 `user` 和 `assistant` 消息，因此模型能看到上一轮最终回答，但不会自动重新获得上一轮完整工具结果。

### 为什么数据库仍保存普通 `role` / `content`

`HumanMessage`、`AIMessage`、`ToolMessage` 是 LangChain 的 Python 运行时对象。数据库可以保存它们序列化后的 JSON，但当前项目选择保存框架无关的领域字段：

```python
{"role": "user", "content": "..."}
```

调用模型前再由 `messages.py` 转成 LangChain Message。这样数据库、FastAPI 接口和前端不绑定 LangChain；未来替换框架时，历史会话数据不需要随之迁移。兼容阶段 8 已有数据是附带好处，不是主要原因。

## `ChatPromptTemplate` 中的 `"{user_prompt}"`

`"{user_prompt}"` 是 LangChain `ChatPromptTemplate` 的变量占位符，不是 Python f-string。定义模板时它保留原样：

```python
ChatPromptTemplate.from_messages(
    [
        ("system", SYSTEM_PROMPT),
        ("human", "{user_prompt}"),
    ]
)
```

调用下面的方法时才会替换变量并生成真正的 LangChain 消息对象：

```python
REFLECTION_PROMPT.format_messages(user_prompt=full_text)
```

结果相当于：

```python
[
    SystemMessage(content=SYSTEM_PROMPT),
    HumanMessage(content=full_text),
]
```

这里的 `full_text` 来自 `build_reflection_user_prompt()`，其中包含复盘表单字段、RAG 检索资料和输出要求。`ChatPromptTemplate` 只组织消息，不调用模型；随后才由 `ChatOpenAI.ainvoke()` 或 `astream()` 发送请求。

## LangChain Tool Schema 为什么抛出 `RuntimeError`

`app/langchain/tools.py` 中的 `@tool` 函数只用于让 LangChain 从函数名、参数类型、`Annotated` 参数说明和 docstring 生成模型可理解的工具 Schema。例如：

```python
@tool
def search_reflections(...) -> str:
    """Search current-session reflections by keywords."""
    raise RuntimeError("Tool schemas are executed by app.agent.tool_runner, not directly by LangChain.")
```

因此直接调用这些函数或调用 `tool.invoke(...)` 会抛出 `RuntimeError`。原因是 Python 一旦执行函数调用，就会进入函数体；而这里的函数体只有 `raise RuntimeError(...)`。例如：

```python
list_reflections.invoke({"limit": 5})
```

会进入 `list_reflections()` 并报错。这是刻意的保护：防止 LangChain Tool 绕过项目的 `tool_runner.py`，直接访问数据库或 RAG。

正常 Agent 流程不会执行这个函数体：

```text
bind_tools() 将 Schema 告诉模型
-> 模型返回 AIMessage.tool_calls（只是调用意图）
-> agent_client.py 读取意图
-> tool_runner.py 校验工具名、注入可信 session_id、写工具日志
-> app/agent/tools.py 执行真实工具
-> ToolMessage 将结果交回模型
```

也就是说，“模型提出调用工具”不等于“LangChain 直接执行该 `@tool` 函数”。

## 阶段 8 与阶段 9：LangChain 省掉了什么

阶段 8 为了理解底层协议，项目手写了 OpenAI-compatible API 的请求与响应处理：

```text
拼接 /chat/completions URL
-> 拼 Authorization / Content-Type 请求头
-> 拼 model、messages、temperature、stream 等 JSON 请求体
-> 使用 httpx 发普通或流式请求
-> 手动读取 response.json()
-> 手动取 choices[0].message.content
-> 手动解析 SSE 的 data: 行、[DONE]、choices[0].delta.content
```

阶段 9 将这些协议适配交给 LangChain：

```text
ChatOpenAI
-> 管理 OpenAI-compatible 请求格式与响应格式

ChatPromptTemplate
-> 组织 SystemMessage、HumanMessage 模板

ainvoke()
-> 返回非流式 AIMessage

astream()
-> 返回流式 AIMessageChunk

@tool / bind_tools() / AIMessage.tool_calls / ToolMessage
-> 组织工具 Schema 与工具调用消息格式
```

项目仍保留业务与安全边界：Prompt 内容、RAG、数据库读写、可信 `session_id` 注入、工具白名单、工具日志、FastAPI SSE 协议、错误映射，以及“不自动重试/降级”。LangChain 减少的是重复的模型协议适配代码，不是替项目做业务决策。

## `ainvoke()`、`astream()` 与消息内容格式

- `await model.ainvoke(messages)`：非流式调用，返回一条完整的 `AIMessage`。
- `async for chunk in model.astream(messages)`：流式调用，逐个返回 `AIMessageChunk`。

两种消息对象的 `.content` 都可能是普通字符串，也可能是内容块列表；这不严格由“流式或非流式”决定，而取决于模型供应商及返回内容类型。`_message_text()` 将两种形式统一为一个字符串：字符串直接返回；列表则按顺序拼接字符串块和 `{"text": "..."}` 文本块。

流式时，每个 chunk 仍先通过 `_message_text()` 变成一个完整字符串，再由外层 `yield content` 输出。若直接逐个 `yield parts`，会人为拆成更多 SSE 事件；当前写法保证非流式和流式最终都复用同一种“消息 -> 字符串”的转换规则。

阶段 8 手写解析只预期 `choices[0].message.content` 或 `choices[0].delta.content` 是字符串。LangChain 消息适配后需要额外兼容内容块列表，但当前 `_message_text()` 也不是对所有供应商格式的无限兼容层；不认识的块会被安全忽略。

## 错误对象的 `status_code`

`getattr(exc, "status_code", None)` 读取异常上可能存在的状态码。网络错误、超时、配置错误等异常通常没有该属性，会得到 `None`；第三方异常的同名属性也不一定保证是整数。因此 `isinstance(status_code, int)` 后才把它作为 HTTP 状态码写入错误文本；否则返回通用的异常类型信息。

## LangChain Retriever 的 Pydantic 配置与字段

### Pydantic 是什么

Pydantic 是 Python 的数据模型库：它依据类型声明创建对象、校验和转换数据，并支持将对象序列化为字典或 JSON。项目的 `SQLModel` 建立在 Pydantic 之上；LangChain 的 `BaseRetriever` 也是 Pydantic 风格对象。

`ConfigDict` 是 Pydantic 的配置对象，不是 SQLModel 类型。类属性 `model_config` 用于配置当前 Pydantic 模型的行为：

```python
model_config = ConfigDict(arbitrary_types_allowed=True)
```

`arbitrary_types_allowed=True` 表示允许字段持有 Pydantic 不认识的任意 Python 对象。这里需要它，是因为 Retriever 的 `session` 字段保存了运行中的 SQLModel `Session` 数据库会话对象。

### `exclude=True` 的作用

```python
session: Any = Field(exclude=True)
latest_chunks: list[RetrievedChunk] = Field(default_factory=list, exclude=True)
```

`exclude=True` 不表示字段不存在，也不表示不保存到 Retriever 对象。Retriever 实例运行时仍持有 `session` 和 `latest_chunks`；它表示当 Pydantic 将 Retriever 序列化为字典或 JSON 时，排除这些内部字段。

因此：

```text
model_config
-> 配置 Pydantic 如何处理 Retriever 对象

session 字段
-> 临时保存在 Retriever 实例内，供本次检索读 SQLite

exclude=True
-> 不把 Session、内部检索缓存输出到序列化数据
```

`model_config` 本身不存储 `session`，也不会把 Session 写入数据库；实际持有 Session 的是 Retriever 实例字段。

### Retriever 与回调管理器

Retriever（检索器）是“输入查询文本，输出资料 Document 列表”的标准接口。它不一定是向量检索：关键词检索、向量检索、混合检索、网页搜索都可以包装为 Retriever。当前项目的 Retriever 内部复用 Embedding + 余弦相似度 + Top-K。

`run_manager` 是 LangChain 框架在调用 Retriever 时传入的回调管理器，不是当前业务主动传给它的普通回调函数。它可以在检索开始、结束或报错时通知追踪、日志、监控等组件；当前没有接入追踪平台，因此只保留框架要求的参数而不使用。后续接入 LangSmith 时可利用这一链路记录检索过程。
