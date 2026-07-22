# 阶段 9 设计：LangChain 组件化

## 目标

阶段 8 已通过原生 OpenAI-compatible HTTP API 手写完成：

```text
消息历史
-> 模型 Tool Calling 判断
-> 后端执行工具
-> 模型 SSE 流式回答
-> 保存会话和消息
```

阶段 9 的目标不是用框架替换现有业务控制，而是用 LangChain 的标准组件重构模型调用层，并为 Agent 增加一个可选的内置知识库检索工具。

```text
阶段 8：理解原生协议和手写 Agent Loop
-> 阶段 9：理解 LangChain 如何抽象模型、消息、Prompt、Tool、Retriever
-> 阶段 10：使用 LangGraph 编排更复杂的状态图
```

## 为什么现在引入 LangChain

当前项目已经有真实的会话、RAG、工具调用和 SSE，因此可以把框架抽象与已理解的底层实现逐项对比：

| 阶段 8 原生实现 | 阶段 9 LangChain 抽象 |
| --- | --- |
| `httpx.AsyncClient` + `/chat/completions` | `ChatOpenAI` |
| `dict` 形式的 `messages` | `SystemMessage`、`HumanMessage`、`AIMessage`、`ToolMessage` |
| `TOOL_DEFINITIONS` JSON Schema | LangChain `@tool` / `StructuredTool` |
| 手写 `stream=true` SSE 解析 | `astream()` 返回文本片段 / 消息块 |
| 手写 Prompt 字符串拼接 | `ChatPromptTemplate` |

引入框架的目的是减少重复协议适配、学习行业常用抽象，而不是把数据库、权限和业务逻辑交给框架。

## 阶段范围

### 本阶段包含

- 安装 `langchain` 与 `langchain-openai`。
- 用 `ChatOpenAI` 封装当前 OpenAI-compatible 反代 API。
- 将会话历史转换为 LangChain Message 对象。
- 将当前 System Prompt / 用户 Prompt 改为 `ChatPromptTemplate` 或等价消息模板。
- 用 LangChain Tool 定义生成模型可理解的工具 Schema，并用 `bind_tools()` 绑定模型。
- 使用 LangChain `AIMessage.tool_calls` 读取模型的工具调用意图。
- 使用 `ToolMessage` 将真实工具结果交回模型。
- 使用 `astream()` 获取最终回答的流式文本，再沿用现有 FastAPI SSE 事件协议。
- 为当前 RAG 检索增加一个 LangChain Retriever 适配层，复用已有知识块、Embedding 和引用来源逻辑。
- 为 Agent 增加 `search_knowledge_base` 工具：模型可在需要理论资料或练习建议依据时主动检索内置知识库，而不是每轮对话都强制注入 RAG 上下文。
- 让 `tool_runner` 同时支持现有同步 SQLite 工具和需要调用 Embedding API 的异步知识库检索工具。
- 建立后端模型配置解析层，允许未来显式区分报告模型、Agent 模型和摘要模型。

### 本阶段不包含

- 不使用 `create_agent` 等高层 Agent 执行器替代现有 Agent Loop。
- 不引入 LangGraph、状态图、摘要记忆、长期记忆或 Human-in-the-loop。
- 不改变前端 API、Next.js Chat UI、会话表和消息表。
- 不允许前端传入任意模型名。
- 不做自动重试、主备模型切换或自动降级。
- 不接入 LangSmith、Agent Chat UI 或 Gradio；LangSmith 放在阶段 12 评估。
- 不替换 SQLite / RAG 数据结构；PostgreSQL / pgvector 放在阶段 11。

## 核心边界

LangChain 负责模型交互抽象；项目后端仍负责业务与安全边界：

```text
LangChain
├─ 创建模型客户端
├─ 组织模型消息
├─ 声明工具 Schema
├─ 读取模型 tool_calls
└─ 流式读取模型输出

项目后端
├─ 校验 session_id 与 conversation_id 归属
├─ 读取/保存 Agent 会话和消息
├─ 将可信 session_id 注入工具调用
├─ 工具白名单、参数解析和执行（同步数据库工具与异步 RAG 工具）
├─ 工具日志关联 assistant_message_id
└─ 对前端维持既有 SSE 事件协议
```

模型仍然只提出工具调用意图，不能直接读 SQLite、修改用户数据、请求 Embedding API 或访问任意外部网络。

## 目标架构

```text
FastAPI Router / conversation_service
-> LangChain Agent Adapter
   -> ChatOpenAI.bind_tools(langchain_tools)
   -> AIMessage.tool_calls
   -> tool_runner 执行真实工具
      ├─ 同步：查询当前用户的 SQLite 复盘记录
      └─ 异步：调用 Embedding API 并检索内置知识库
   -> ToolMessage 回传工具结果
   -> ChatOpenAI.astream() 产生最终文本
-> 现有 SSE event_generator
-> Next.js Chat UI
```

与阶段 8 对比，数据库、路由、SSE 事件名和前端都不需要改变。主要替换的是 `agent_client.py` 与 `llm_client.py` 内部的模型协议适配代码。

## 后端目录设计

建议新增：

```text
backend/app/langchain/
├── __init__.py
├── chat_model.py        # ChatOpenAI 工厂与模型配置解析
├── messages.py          # dict 历史 <-> LangChain Message 转换
├── prompts.py           # ChatPromptTemplate
├── tools.py             # @tool / StructuredTool 定义，仅描述模型可调用能力
└── retriever.py         # 复用现有 RAG 检索的 LangChain Retriever 适配层
```

主要修改：

```text
backend/app/settings.py
  - 解析默认模型、可选 Agent 模型、可选报告模型。

backend/app/llm_client.py
  - 使用 LangChain ChatOpenAI 调用报告模型和流式输出。

backend/app/agent/agent_client.py
  - 使用 LangChain Message、bind_tools、AIMessage.tool_calls、ToolMessage、astream。

backend/app/agent/tool_runner.py
  - 继续是唯一的真实工具执行入口；不允许 LangChain Tool 绕过它直接读数据库或调用 RAG。
  - 保留同步 SQLite 工具执行，并增加异步知识库检索工具执行入口。

backend/app/rag/retrieval.py
  - 保留现有检索算法；由 Retriever 适配层调用，不复制检索逻辑。

backend/requirements.txt
  - 增加 LangChain 相关依赖。
```

## 模型配置层

当前只有一个 `LLM_MODEL`。阶段 9 将保留它作为默认值，并支持后续显式配置：

```text
LLM_MODEL                 # 默认模型，必填
LLM_AGENT_MODEL           # 可选；为空时使用 LLM_MODEL
LLM_REPORT_MODEL          # 可选；为空时使用 LLM_MODEL
LLM_SUMMARY_MODEL         # 仅预留给阶段 10 的会话摘要能力
```

配置层只决定“某类任务显式使用哪个模型”。本阶段不实现：

```text
主模型失败 -> 自动尝试备用模型
```

任何降级或自动重试策略仍须用户明确确认后再实施。

## Tool Calling 设计

### LangChain Tool 的作用

现有 `list_reflections`、`search_reflections`、`get_reflection_detail`，以及新增的 `search_knowledge_base`，会用 `@tool` 或 `StructuredTool` 声明名称、说明、参数类型和描述，传给：

```python
model.bind_tools(langchain_tools)
```

模型返回的工具调用将由 `AIMessage.tool_calls` 提供标准结构，例如：

```python
{
    "name": "search_reflections",
    "args": {"query": "焦虑", "limit": 5},
    "id": "call_...",
}
```

### 真实执行仍由 `tool_runner.py` 完成

LangChain Tool 在这里主要负责“向模型声明工具契约”，而不是绕过业务层直接执行数据库函数。

执行链保持为：

```text
AIMessage.tool_calls
-> 转为 JSON 参数
-> execute_tool_call(..., session_id, session, conversation_id, assistant_message_id)
-> ToolExecutionResult
-> ToolMessage(content=完整结果 JSON, tool_call_id=调用 ID)
-> 回到模型
```

这样仍能保证：

- `session_id` 只由后端注入。
- 工具名必须通过白名单。
- 工具日志必须写入数据库。
- 模型参数无法直接控制数据库 Session 或越权读取其他用户数据。

### Agent 可选 RAG 工具

普通复盘报告的 RAG 是固定流程：每次创建报告前都检索资料并写入 Prompt。Agent 对话不应每轮都附带全部检索结果，否则会增加 Token 消耗，并可能把无关资料带入回答。

因此 Agent 使用可选工具：

```text
用户提问
-> 模型判断是否需要内置理论资料
-> 若需要，提出 search_knowledge_base(query, limit) 调用
-> 后端异步执行 Embedding + 向量检索
-> 返回片段、来源、标题和相似度给模型
-> 模型基于检索结果生成回答
```

`search_knowledge_base` 只检索项目内置、已确认可发送给 Embedding 服务商的资料。它不访问用户私有复盘记录；私有记录仍只能通过带后端注入 `session_id` 的历史复盘工具访问。

工具结果需包含可读的资料来源信息，供模型在回答中说明参考依据；前端仍沿用现有工具调用状态展示，不在本阶段新增独立的引用卡片 UI。

### 同步与异步工具边界

当前历史复盘工具使用同步 SQLModel / SQLite `session.exec(...)`，因此是同步工具。新增知识库检索在向量比较前需要请求 Embedding API，这是网络 I/O，应使用 `await` 异步等待。

同步或异步不由数据是否“来自外部”决定，而由底层驱动与调用方式决定。`tool_runner` 是统一执行入口，不代表其中所有工具必须采用同一种执行方式。

## Message 与 Prompt 设计

阶段 8 的历史消息目前是：

```python
{"role": "user", "content": "..."}
```

阶段 9 会转换为：

```text
SystemMessage     -> Agent System Prompt
HumanMessage      -> 用户消息
AIMessage         -> 助手回答或模型工具调用请求
ToolMessage       -> 后端真实工具结果
```

`ChatPromptTemplate` 用于固定 System Prompt、RAG 上下文和当前用户输入的组合。它不保存会话记忆；会话历史仍然从项目数据库读取。

## RAG Retriever 适配

阶段 6 的检索实现继续负责生成 Embedding、计算相似度并返回来源。阶段 9 新增 Retriever 适配器，并让普通报告和 Agent 知识库工具都复用它：

```text
LangChain Retriever 输入：query
-> 调用现有按 query 检索的实现
-> 转成 LangChain Document
-> 保留 source、title、score 等 metadata
```

这一步的学习重点是：Retriever 是统一接口，不等于必须立刻更换向量数据库或检索算法。

## 流式输出设计

阶段 8 的前端 SSE 协议保持不变：

```text
conversation
tool_started
tool_completed
delta
done
error
```

内部变化是最终回答从手写 `httpx.aiter_lines()` 读取上游 SSE，改为：

```python
async for chunk in model.astream(messages):
    yield chunk.content
```

若 `chunk.content` 不是字符串，适配层需要安全忽略或转为文本片段。上游异常仍转换为项目已有的错误事件；不会改为非流式，也不会自动切换模型。

## 实施顺序

1. 增加依赖并验证当前反代 API 能被 `ChatOpenAI` 调用。
2. 实现模型配置解析与 `ChatOpenAI` 工厂。
3. 实现 Message / Prompt 转换，先改造普通复盘报告调用。
4. 实现 LangChain Tool Schema，并保留现有 `tool_runner.py`。
5. 改造 Agent Loop：`bind_tools()`、`AIMessage.tool_calls`、`ToolMessage`、`astream()`。
6. 增加 Retriever 适配层，接入现有 RAG 检索。
7. 为 Agent 声明 `search_knowledge_base` Schema，并在 `tool_runner` 实现异步执行与工具日志。
8. 验证原有复盘流、Agent 历史工具流、Agent 知识库工具流、多轮会话和历史恢复均不回归。

## 验收

- 当前反代 API 可通过 `ChatOpenAI` 完成普通调用、Tool Calling 和流式调用。
- 普通复盘报告仍能使用 RAG 资料并流式输出。
- Agent 在现有 Chat UI 中仍能调用历史复盘工具并展示工具状态。
- Agent 在确有需要时能调用 `search_knowledge_base`，并基于返回的资料来源生成回答。
- 不需要资料的问题不强制调用知识库工具。
- 工具调用仍经过 `tool_runner.py`，工具日志仍关联当前会话和助手消息。
- 同一会话的多轮上下文与刷新恢复不回归。
- 未配置 `LLM_AGENT_MODEL` / `LLM_REPORT_MODEL` 时，仍使用 `LLM_MODEL`。
- 上游失败时仍只返回错误，不自动重试、切换模型或降级。

## 完成后的学习检查点

- 能解释 LangChain 和当前原生 HTTP 实现分别替代、保留哪些部分。
- 能区分 `ChatOpenAI`、Message、Prompt、Tool、Retriever 的职责。
- 能解释 `bind_tools()`、`AIMessage.tool_calls`、`ToolMessage` 的数据流。
- 能解释为什么 LangChain Tool 不应绕过项目的 `tool_runner.py`。
- 能区分普通复盘的固定 RAG 与 Agent 按需 Tool RAG，并说明同步 SQLite 工具和异步 Embedding 检索工具的边界。
- 能解释 LangChain 与阶段 10 LangGraph 的边界。
