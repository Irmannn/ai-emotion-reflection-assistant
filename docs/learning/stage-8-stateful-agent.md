# 阶段 8 学习笔记：有状态流式 Agent

## 为什么聊天消息和工具结果要分开持久化

阶段 8 中，`AgentMessage` 只保存用户消息和最终助手回答；模型调用工具时产生的完整工具结果不作为普通聊天消息保存，而是写入 `AgentToolCallLog`。

```text
AgentMessage
├─ user：用户原始问题
└─ assistant：最终自然语言回答

AgentToolCallLog
└─ 本条 assistant 回答调用了什么工具、传了什么参数、得到什么结果摘要
```

原因有三个：

- 后续多轮对话只需要“用户说了什么、助手最终回答了什么”作为主要上下文。若把完整工具结果也不断放入历史，输入会变长，消耗更多 Token。
- 工具结果可能包含较长的复盘原文、RAG 资料片段或结构化数据；它们适合本轮模型推理，不适合直接作为普通聊天记录反复发送。
- 前端恢复会话时，可以把工具调用摘要展示在对应助手回答下方，既能追溯 Agent 做过什么，也不会把完整敏感数据直接展示出来。

一次 Tool Calling 在本轮模型上下文中的临时结构仍然是：

```text
user：帮我查询焦虑相关复盘
assistant：请求调用 search_reflections
tool：工具返回完整查询结果
assistant：基于结果给出最终回答
```

其中 `role=tool` 只在当前 Agent Loop 中用于将工具结果交回模型。会话数据库长期保存的重点是最终 `user` / `assistant` 消息，以及可追溯的工具调用日志。

## `conversation_service.py` 语法与排序

### `order_by` 的两个参数

```python
.order_by(AgentMessage.created_at.asc(), AgentMessage.id.asc())
```

排序有优先级：先按创建时间升序；若两条消息创建时间相同，再按自增 `id` 升序。这样聊天记录总能稳定地按发生顺序显示。

### `reversed(messages)`

为了高效取最近 N 条历史，数据库先按“最新在前”查询：

```python
.order_by(...desc()).limit(N)
```

`reversed(messages)` 会反向遍历这个列表，让模型最终收到“最早在前、最新在后”的正常对话顺序。它不修改原列表，而是返回一个反向遍历器。

### `tuple[AgentMessage, AgentMessage]`

```python
def create_exchange(...) -> tuple[AgentMessage, AgentMessage]:
```

表示函数固定返回两个 `AgentMessage`，对应新保存的用户消息和新创建的 `pending` 助手消息：

```python
user_message, assistant_message = create_exchange(...)
```

这与 `list[AgentMessage]` 不同：元组强调固定两个位置，列表表示数量可变。

### 为什么更新会话也要 `session.add(conversation)`

`create_exchange` 会修改已有会话的标题和 `updated_at`。将 `conversation` 传给 `session.add()`，再执行一次 `session.commit()`，会把以下变化一起写入数据库：

```text
新增 user_message
新增 pending assistant_message
更新 conversation.title 与 conversation.updated_at
```

已经由当前 Session 查询出的对象通常也能被自动追踪；显式 `add` 能让“这次会更新会话”更清晰，并保证它参与本次提交。

### `" ".join(content.split())`

这个表达式用于生成干净的会话标题：

```python
content.split()
```

按任意空白切分文本，自动忽略连续空格、换行和制表符；再用单个空格重新拼接：

```python
"  我今天开会   被否定了\n\n很难受  "
-> ["我今天开会", "被否定了", "很难受"]
-> "我今天开会 被否定了 很难受"
```

## `stream_agent_chat` 的核心流程

`stream_agent_chat` 是阶段 8 的异步 Agent Loop。它不直接保存消息或生成 HTTP SSE 文本，而是向路由层逐个 `yield` 业务事件：

```text
conversation_service 准备当前会话最近消息
-> agent_client 在最前面加入 System Prompt
-> 非流式请求模型，携带 tools 与 tool_choice="auto"
-> 模型是否返回 tool_calls？
   ├─ 是：yield tool_started
   │     -> 后端 tool_runner 执行本地工具并保存日志
   │     -> yield tool_completed
   │     -> 将完整工具结果作为 role="tool" 放回本轮 messages
   │     -> 再次请求模型判断
   └─ 否：以 stream=true 和 tool_choice="none" 请求最终回答
         -> 每收到一个文本片段 yield delta
         -> Agent Loop 结束
```

`MAX_AGENT_TOOL_ROUNDS = 3` 限制最多工具循环次数，避免模型持续请求工具造成无限循环和不可控成本。达到上限时直接返回明确错误；不会自动重试、换模型或降级为其他流程。

### 为什么先非流式判断工具，再流式输出最终回答

工具调用不是普通文本，而是模型返回的完整结构化数据，例如：

```json
{
  "role": "assistant",
  "tool_calls": [
    {
      "function": {
        "name": "search_reflections",
        "arguments": "{\"query\":\"焦虑\"}"
      }
    }
  ]
}
```

后端必须先完整拿到 `tool_calls`，才能校验工具名和参数并执行工具。因此第一段请求不写 `stream: true`，使用默认非流式响应。

当模型不再请求工具后，第二段请求才设置：

```python
"stream": True
"tool_choice": "none"
```

含义是：最终自然语言回答逐段流向前端，并且本轮不允许再突然产生新的工具调用。这样前端只需要处理稳定的文本 `delta`，工具执行过程由前面的业务事件单独展示。

### 模型“判断是否调用工具”的代码位置

`stream_agent_chat()` 每轮循环一开始会执行：

```python
data = await _post_tool_decision(client, request_messages)
assistant_message = _extract_assistant_message(data)
tool_calls = assistant_message.get("tool_calls") or []
```

`_post_tool_decision()` 的请求体携带：

```python
"tools": TOOL_DEFINITIONS
"tool_choice": "auto"
```

并且没有 `"stream": True`。`tool_choice="auto"` 不是额外问模型一句“要不要用工具”，而是把工具定义交给模型，让模型自行决定直接回答还是返回 `tool_calls`。后端通过 `if not tool_calls` 判断最终选择。

### 有工具调用时发生什么

当 `tool_calls` 不为空时，后端按每个工具调用执行：

```text
1. yield tool_started
   前端立即显示“某工具执行中”。

2. tool_runner 执行真正的后端工具
   例如 search_reflections_tool 查询当前 session 的复盘记录。

3. 工具调用日志保存到数据库
   关联当前 conversation_id 和 assistant_message_id。

4. yield tool_completed
   前端将“执行中”更新为成功或失败摘要。

5. 将完整工具结果追加为 role="tool" 消息
   交回模型作为下一轮推理依据。

6. 回到 Agent Loop，再次请求模型
   模型可以继续调用工具，也可以停止调用并进入最终流式回答。
```

模型只提出工具调用意图；实际访问数据库、注入可信 `session_id`、执行函数和保存日志的都是 FastAPI 后端。

### 上游 SSE 为什么可按行 `json.loads`

模型 API 的单个文本事件通常是：

```text
data: {"choices":[{"delta":{"content":"你"}}]}
```

后端使用：

```python
async for line in response.aiter_lines():
    payload = line[6:]
    data = json.loads(payload)
```

`line[6:]` 只去掉固定前缀 `"data: "`。虽然底层网络可能把 JSON 拆进多个数据块，`response.aiter_lines()` 会先缓存并拼接，直到读到换行符才返回完整的一行。因此 `json.loads(payload)` 执行时拿到的是完整 JSON，而不是半截网络数据。

当前模型 API 每个 JSON 使用一行 `data:`。SSE 协议也允许一个事件有多个 `data:` 行；若服务商这样发送，后端就需要先按空行拼成完整事件，再解析 JSON，类似前端的 `parseStreamMessage()`。

## `agent.py`：保存消息并转发 SSE

### `event_generator()` 的完整职责

`event_generator()` 是定义在流式路由内部的异步生成器。它可以直接使用外层已准备好的 `conversation`、`user_message`、`assistant_message`、`context_messages` 和数据库 `session`。

完整流程：

```text
路由先校验 conversation_id 属于当前 session_id
-> 保存用户消息，并创建一条 pending 助手消息
-> 查询最近历史，组成 context_messages
-> event_generator 启动 SSE
-> 先发送 conversation 事件
-> 消费 agent_client 产生的 tool_started / tool_completed / delta 业务事件
-> 每收到 delta：一边拼接到 answer_parts，一边立即发送给前端
-> 正常结束：将 pending 助手消息更新为 completed，发送 done
-> 发生错误：将 pending 助手消息更新为 failed，发送 error
```

它不重新执行工具逻辑，只把 `agent_client.py` 的业务事件包装为 SSE 文本；同时收集全部 `delta`，以便流结束后一次性把完整回答保存到数据库。

### 为什么先发送 `conversation` 事件

流刚开始时，路由会发送新会话、新用户消息和空的 `pending` 助手消息：

```text
conversation 事件
-> 前端立即显示用户刚发送的内容
-> 前端立即显示“Agent 正在生成”的助手气泡
-> 后续 tool 事件和 delta 文本持续填充这个气泡
```

这样用户不必等模型生成第一个字，界面就已经有即时反馈。`done` 事件到达后，前端再用数据库中的最终助手消息替换临时气泡。

### `perf_counter()`：测量耗时

```python
started_at = perf_counter()
duration_ms = int((perf_counter() - started_at) * 1000)
```

`perf_counter()` 是 Python 提供的高精度、单调递增计时器，适合测量代码执行耗时。它不代表现实日期时间，不能用于显示“现在几点”；系统时间被手动修改时，它也不会倒退。这里用它记录一次 Agent 请求从开始到成功或失败经历了多少毫秒。

`datetime.now()` 用于记录真实日期时间；`perf_counter()` 用于计算经过了多久。

### 为什么会有 `asyncio.CancelledError`

异步任务可能被框架主动取消，例如用户关闭页面、浏览器断开 SSE 请求、服务器关闭或上游任务被取消。此时 Python 会在等待点抛出 `asyncio.CancelledError`，它更像“停止任务的控制信号”，不一定代表业务代码写错。

路由捕获它后先把数据库中 `pending` 助手消息标记为 `failed`，避免永久卡在生成中；随后必须再次 `raise`，让 FastAPI/asyncio 正确结束这个已取消的请求，不能把取消信号吞掉。

### SSE 响应头

```python
headers={
    "Cache-Control": "no-cache",
    "X-Accel-Buffering": "no",
}
```

- `Cache-Control: no-cache`：浏览器或中间缓存不能直接复用旧的 SSE 内容，应请求服务器确认最新数据。聊天流不应被当成可复用的普通页面响应。
- `X-Accel-Buffering: no`：Nginx 识别的响应头，要求它不要把 SSE 内容攒到一大段后再发送，而是尽快把每个文本片段转发给浏览器。未使用 Nginx 时通常会被忽略。

## `database.py`：旧 SQLite 表的兼容迁移

`SQLModel.metadata.create_all(engine)` 只能创建不存在的新表，不能为已经存在的表自动新增字段。阶段 8 为阶段 7 已存在的 `agent_tool_calls` 增加 `conversation_id` 和 `assistant_message_id` 时，需要额外执行轻量迁移。

### `with engine.begin() as connection`

```python
with engine.begin() as connection:
```

从数据库 `engine` 开启一个底层连接和事务：执行数据库结构检查与改表操作；全部成功后提交；离开代码块后自动关闭连接。它用于表结构操作，不是 API 请求中查询业务数据的 `Session`。

### SQLite `PRAGMA table_info(...)`

```sql
PRAGMA table_info(agent_tool_calls)
```

`PRAGMA` 是 SQLite 查询内部数据库信息的特殊命令。`table_info` 会返回某张表的字段信息，例如字段名、类型等，用于判断旧表是否已经包含阶段 8 新增的列。

### 集合推导式提取字段名

```python
columns = {row[1] for row in rows}
```

SQLite 返回的每一行 `row` 包含一列字段的信息，`row[1]` 是列名。集合结果例如：

```python
{"id", "session_id", "tool_name", "created_at"}
```

随后可直接判断：

```python
if "conversation_id" not in columns:
```

### 只在缺字段时执行 `ALTER TABLE`

```sql
ALTER TABLE agent_tool_calls ADD COLUMN conversation_id VARCHAR
```

只有确认字段不存在时才新增。第一次启动会补齐字段；之后再次启动会跳过，不会重复加字段或报错。这种“重复执行仍得到正确结果”的性质叫幂等。

这一段是本地 SQLite MVP 的轻量兼容方案。阶段 11 迁 PostgreSQL 后，应使用正式迁移工具（如 Alembic）管理数据库结构变更。

## 为什么会话 ID 和消息 ID 使用不同类型

当前模型中：

```text
AgentConversation.id = UUID 字符串
AgentMessage.id = 自增整数
```

这不是必须不一致，而是按用途做的选择。

- 会话 ID 会出现在前端接口路径中，例如 `/conversations/{conversation_id}/messages`。UUID 不依赖当前数据库最大值、全局唯一，也不容易被顺序猜测，适合对外定位一个长期存在的会话。
- 消息 ID 主要用于单个数据库中的高频新增、关联和稳定排序。自增整数简洁，适合内部记录。

因此对应的关联字段类型也必须保持一致：

```text
AgentToolCallLog.conversation_id      -> VARCHAR，关联 UUID 字符串会话 ID
AgentToolCallLog.assistant_message_id -> INTEGER，关联自增整数消息 ID
```

大型项目也常见统一方案：全部 UUID，或单体应用全部使用 bigint / int。当前 MVP 的混合方案合理，但会增加一点类型心智负担。

## 前端读取 SSE 时为什么需要 `buffer`

`reader.read()` 每次返回的是底层网络数据块，不保证刚好包含一个完整 SSE 事件。一个事件可能被拆开：

```text
第一次读取：event: delta\ndata: {"content":"你最
第二次读取：近"}\n\n
```

因此前端先把每次解码后的文本累加到：

```ts
let buffer = "";
buffer += decoder.decode(value, { stream: true });
```

再用 SSE 的事件结束标记 `"\n\n"` 切分：

```ts
const messages = buffer.split("\n\n");
buffer = messages.pop() ?? "";
```

- 切出的前几段是完整事件，可以立即解析。
- 最后一段可能还不完整，放回 `buffer` 等下一次网络数据继续拼接。

流结束后还会调用 `decoder.decode()`，刷新 `TextDecoder` 内部未输出的字节，避免流末尾的多字节中文字符丢失。

## `URLSearchParams`：构造 Query 参数

`URLSearchParams` 是浏览器内置的查询参数处理工具。当前项目主要用它把对象编码成 URL 中 `?` 后面的参数：

```ts
const params = new URLSearchParams({ session_id: sessionId });
params.toString();
// "session_id=abc-123"
```

拼接后请求类似：

```text
/api/agent/conversations?session_id=abc-123
```

前端负责构造和编码 Query 参数；后端 FastAPI 通过路由函数中的 `session_id: str` 读取、校验该参数。`URLSearchParams` 也可以解析已有 URL 并用 `.get()` 读取值，但当前项目主要使用它的构造能力。

## 为什么 SSE 的 `error` 事件要主动 `throw`

普通 HTTP 请求可通过 `response.ok` 判断成功或失败。但 SSE 响应一旦已经开始，HTTP 状态通常已经是 `200`：后端可能先发送了 `conversation` 或若干 `delta`，之后模型才发生 503、网络中断或其他异常。

因此前端收到：

```text
event: error
data: {"message":"..."}
```

时，不能只当作普通数据展示，而要主动：

```ts
throw new Error(data.message ?? "Agent 流式生成失败。");
```

这样 `streamAgentConversation()` 的 Promise 才会变为失败，`page.tsx` 的 `try/catch` 才能统一处理：

```text
显示错误信息
-> 将临时 pending 助手消息改为 failed
-> 不清空输入框内容
-> 用户可手动再次发送
```

`response.ok` 只能处理流开始前的 HTTP 错误；SSE 的 `error` 事件用于处理流开始后的业务或上游错误。

## Agent 历史复盘的多关键词检索

### 修改原因

原来的 `search_reflections_tool()` 将模型传入的整段查询当成一个连续字符串匹配。例如模型传：

```text
开会 同事 质疑 方案 委屈
```

而复盘原文写成“今天开会时我的方案被同事质疑，之后觉得很委屈”。词都存在，但不是同一段连续文字，旧逻辑就会返回 0 条。

阶段 8 将它改成基础多关键词检索：拆分关键词，分别匹配各字段，按命中关键词数量排序。它不替代后续阶段 11 的向量检索或 Reranker，但能解决模型传入多个简短关键词时的明显问题。

### `re.split(...)` 拆分关键词

```python
re.split(r"[\s,，、;；。！？!?]+", normalized_query)
```

`re.split` 是正则表达式版的切分。`r"..."` 是原始字符串；方括号表示“其中任意一个字符”；末尾 `+` 表示连续一个或多个都作为分隔符。

因此会按空格、中文/英文逗号、顿号、分号、句号、感叹号、问号等切分：

```text
"开会 同事，质疑、方案；委屈"
-> ["开会", "同事", "质疑", "方案", "委屈"]
```

### `dict.fromkeys(...)`：去重并保留顺序

```python
list(dict.fromkeys(term for term in terms if term))
```

- `if term` 过滤空字符串。
- 字典的 key 不会重复，`dict.fromkeys(...)` 可用于去重。
- Python 字典保留插入顺序，因此能在去重后保持关键词原本顺序。

```python
["焦虑", "焦虑", "工作"]
-> ["焦虑", "工作"]
```

### 命中数量排序

每条匹配记录暂存为：

```python
(matched_count, record, matched_reason)
```

排序：

```python
matched.sort(
    key=lambda item: (item[0], item[1].created_at),
    reverse=True,
)
```

`key=lambda item: (item[0], item[1].created_at)` 表示每个元素的排序依据是一个二元组：

```text
第一优先级：item[0]，命中关键词数量
第二优先级：item[1].created_at，复盘创建时间
```

`reverse=True` 表示倒序，因此命中更多关键词的记录排前面；命中数相同则更近的记录排前面。

### `_` 表示当前值不需要使用

```python
for _, record, matched_reason in matched[:safe_limit]:
```

元组第一项是 `matched_count`，它已经用于排序；生成最终 API 返回数据时不再需要它，因此用 `_` 接收。`_` 不是 Python 特殊语法，只是开发者约定：这个值存在，但当前代码有意不使用。
