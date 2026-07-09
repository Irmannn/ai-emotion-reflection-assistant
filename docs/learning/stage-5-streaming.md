# 阶段 5 学习笔记：流式输出

## `llm_client.py`

### `_build_chat_request_body` 参数里的 `*` 是什么意思？

`*` 表示它后面的参数必须用关键字传参。

例如：

```python
_build_chat_request_body(payload, stream=True)
```

不推荐也不允许写成：

```python
_build_chat_request_body(payload, True)
```

这样可以让调用方明确知道 `True` 是传给 `stream` 的，代码可读性更好。

### 为什么保留非流式的 `generate_reflection_report`？

阶段 4 已经实现了非流式接口 `POST /api/reflections`，阶段 5 是新增流式接口，不是删除旧接口。

保留非流式方法有几个作用：

- 作为回退方案，流式接口出问题时仍然可以使用非流式接口。
- 方便对比学习非流式和流式调用的差异。
- 避免破坏已有接口。

### `AsyncIterator` 是什么？

`AsyncIterator[str]` 表示函数会“异步地、一段一段地产出字符串”。

普通函数通常一次性返回完整结果：

```python
return "完整报告"
```

流式函数会分多次产出结果：

```python
yield "第一段"
yield "第二段"
```

因为模型输出来自网络请求，需要等待，所以这里用异步迭代器，并通过 `async for` 一段一段读取。

### `await response.aread()` 是什么意思？

`response.aread()` 是异步读取响应体的完整原始内容。

这里主要用于错误场景：如果模型接口返回 `400`、`500` 等错误，后端需要把错误响应体读出来，方便定位问题。

`a` 可以理解为 async 版本，`aread()` 就是异步读取。

### `.decode("utf-8", errors="replace")` 是做什么的？

`response.aread()` 读到的是 bytes，也就是二进制数据，不是字符串。

`.decode("utf-8")` 会把 bytes 按 UTF-8 编码转成字符串。

`errors="replace"` 表示如果遇到无法解码的字符，不直接报错，而是用替代字符替换掉，让错误处理更稳定。

### `response.aiter_lines()` 是做什么的？

`response.aiter_lines()` 会异步地一行一行读取流式响应。

OpenAI-compatible 流式接口通常会返回多行文本：

```text
data: {"choices":[{"delta":{"content":"第一段"}}]}

data: {"choices":[{"delta":{"content":"第二段"}}]}

data: [DONE]
```

所以后端按行读取，再解析每一行里的 `data:` 内容。

### `json.loads` 是什么？

`json.loads` 用于把 JSON 字符串转换成 Python 数据结构。

例如：

```python
json.loads('{"name": "Tom"}')
```

会得到 Python 字典：

```python
{"name": "Tom"}
```

`loads` 里的 `s` 可以理解成 string，表示从字符串加载 JSON。

### `data["choices"][0]["delta"].get("content")` 是流式专用格式吗？

基本可以这么理解。OpenAI-compatible Chat Completions 的非流式响应通常从这里取完整内容：

```python
data["choices"][0]["message"]["content"]
```

流式响应通常从这里取当前片段：

```python
data["choices"][0]["delta"].get("content")
```

流式响应里不是每个片段都一定有 `content`，有些片段可能只包含角色、结束原因等元信息，所以这里用 `.get("content")`，避免缺少字段时直接报错。

### 为什么流式响应里可能有不是 `data:` 开头的行？

SSE / 流式响应里可能出现不承载业务内容的行，例如空行、注释行、心跳行，或者服务商返回的其他元信息。

当前项目只关心真正的数据行：

```text
data: {...}
```

所以代码写成：

```python
if not line.startswith("data: "):
    continue
```

意思是：不是数据行就跳过，不影响后续继续读取流。

### 不写 `.get("content")` 会报错吗？

可能会。

如果写成：

```python
content = data["choices"][0]["delta"]["content"]
```

当某个流式片段的 `delta` 里没有 `content` 字段时，会抛出 `KeyError`。

写成：

```python
content = data["choices"][0]["delta"].get("content")
```

如果没有 `content`，会返回 `None`，不会报错。

然后再通过：

```python
if content:
    yield content
```

只有真的有文本内容时才输出，适合处理流式响应。

## `reflections.py`

### `json.dumps` 是什么意思？

`json.dumps` 用于把 Python 数据结构转换成 JSON 字符串。

例如 Python 字典：

```python
{"content": "你好"}
```

可以转换成 JSON 字符串：

```json
{"content": "你好"}
```

它和 `json.loads` 方向相反：

```text
json.loads：JSON 字符串 -> Python 数据
json.dumps：Python 数据 -> JSON 字符串
```

### `ensure_ascii=False` 是什么意思？

`json.dumps` 默认可能会把中文转成 Unicode 转义：

```json
{"content":"\u4f60\u597d"}
```

加上：

```python
ensure_ascii=False
```

会保留中文：

```json
{"content":"你好"}
```

这样流式响应里的中文更可读。

### `StreamingResponse` 是什么？

`StreamingResponse` 是 FastAPI 提供的流式响应能力。

普通接口通常是后端准备好完整 JSON 后一次性返回。

`StreamingResponse` 是后端一边生成内容，一边分批发送给前端，适合大模型输出、文件下载、日志实时输出等场景。

### `sse_event` 是做什么的？

`sse_event` 把 Python 数据包装成 SSE 风格文本事件。

例如：

```python
sse_event("delta", {"content": "你好"})
```

会生成：

```text
event: delta
data: {"content":"你好"}
```

项目里用它统一生成三种事件：

- `delta`：模型生成的一段内容。
- `done`：生成完成，并返回保存后的 `record_id`。
- `error`：生成失败。

### 为什么 `for content in stream_reflection_report(payload)` 前面要加 `async`？

`stream_reflection_report(payload)` 返回的是 `AsyncIterator[str]`，也就是异步迭代器。

普通 `for` 用来遍历同步数据，例如已经在内存里的数组。

`async for` 用来遍历异步数据流，例如模型通过网络一段一段返回的内容。

在当前项目里：

```python
async for content in stream_reflection_report(payload):
```

意思是：异步等待模型每一段输出；每收到一段，就进入循环体处理一次。

## `api.ts`

### `getReader()` 是做什么的？

`response.body` 是浏览器里的可读流，`getReader()` 用来拿到这个流的读取器。

拿到读取器后，就可以通过：

```ts
await reader.read()
```

一块一块读取后端推过来的数据。

普通 JSON 接口不需要 `getReader()`，因为普通接口可以直接用 `response.json()` 一次性读完整响应。

### `TextDecoder()` 是做什么的？

`reader.read()` 读到的 `value` 是二进制数据，不是字符串。

`TextDecoder` 用来把二进制数据转换成字符串。

它和后端的 bytes decode 类似：

```python
bytes.decode("utf-8")
```

前端对应写法是：

```ts
decoder.decode(value)
```

### `decoder.decode(value, { stream: true })` 为什么要传 `stream`？

因为流式数据是分块传输的，一个 UTF-8 字符可能被拆在两个网络块里。

`stream: true` 表示这是流式解码，不要把当前块当作最终完整输入；如果当前块结尾有半个字符，解码器会保留状态，等下一块到来后继续解码。

循环结束后再调用：

```ts
decoder.decode()
```

是为了把解码器中可能残留的内容做最后收尾。

### `buffer` 是做什么的？

`buffer` 是字符串缓存区。

网络每次读到的数据块不保证刚好是一个完整 SSE 事件。可能第一次只读到半个事件，第二次才读到剩下半个。

所以需要先把数据放进 `buffer`，再按 SSE 事件分隔符 `\n\n` 切出完整事件。

### 为什么要 `messages.pop()`？

代码：

```ts
const messages = buffer.split("\n\n");
buffer = messages.pop() ?? "";
```

`split("\n\n")` 后，最后一段可能是不完整事件。

`messages.pop()` 会把最后一段取出来，放回 `buffer`，等待下一块网络数据补齐。

剩下的 `messages` 才是可以安全处理的完整事件。

### `streamCreateReflection` 整体在做什么？

`streamCreateReflection` 是前端阶段 5 的流式请求函数。

它负责：

- 把表单数据 POST 给后端 `/api/reflections/stream`。
- 读取 `response.body` 流。
- 把二进制块解码成字符串。
- 把字符串拆成 SSE message。
- 遇到 `delta` 就调用 `onDelta` 让页面追加显示。
- 遇到 `done` 就返回 `{ record_id }`。
- 遇到 `error` 就抛出错误，让页面显示失败提示。

### 为什么需要 `nextResult`？

`handleStreamMessage` 处理不同事件时返回值不同：

- `delta`：只追加内容，返回 `null`。
- `done`：返回 `{ record_id: number }`。
- `error`：直接抛错。

`nextResult` 表示当前这一条 message 有没有产生最终结果。

如果当前 message 是 `done`，`nextResult` 就会有值，然后赋给外层的 `result`。

### 为什么循环结束后还要处理 `buffer`？

循环结束表示网络流结束，但 `buffer` 里可能还残留最后一段尚未处理的文本。

所以需要：

```ts
buffer += decoder.decode();
if (buffer.trim()) {
  const nextResult = handleStreamMessage(buffer, handlers);
  ...
}
```

这一步是收尾处理，避免最后一个事件因为没有及时被 `\n\n` 切出来而丢失。

### `readErrorMessage` 是做什么的，为什么里面还要 `catch`？

`readErrorMessage` 负责从失败响应里尽量读出后端返回的错误信息。

后端错误有时是 JSON：

```json
{"detail":"LLM_API_KEY is not configured"}
```

但也可能是纯文本、HTML 或空响应。

所以需要 `try/catch`：如果 JSON 解析失败，就返回通用错误：

```ts
Request failed: ${response.status}
```

避免“错误处理代码自己又报错”。

### 为什么 `response.json()` 也要 `await`？

`response.json()` 会读取响应体并解析 JSON，这个过程是异步的。

所以它返回 `Promise`，需要写：

```ts
await response.json()
```

才能拿到真正的 JS 对象。

### `(await response.json()) as { detail?: string }` 是什么语法？

拆开看：

```ts
await response.json()
```

表示拿到响应 JSON 对象。

```ts
as { detail?: string }
```

是 TypeScript 类型断言，表示“我认为这个对象大概长这样”：

```ts
{
  detail?: string
}
```

`detail?` 表示 `detail` 字段可能存在，也可能不存在。

### `line.slice("event:".length).trim()` 是做什么的？

假设一行文本是：

```text
event: delta
```

`"event:".length` 是 `6`。

```ts
line.slice("event:".length)
```

会截取出：

```text
 delta
```

再调用：

```ts
.trim()
```

会去掉首尾空格，得到：

```text
delta
```

所以这句代码的作用是：从 `event: delta` 这一行里提取出事件名。

### `streamCreateReflection`、`handleStreamMessage`、`parseStreamMessage` 的分工

`streamCreateReflection` 的最终返回值是 `record_id`。

中间的流式内容不是通过返回值拿到的，而是通过：

```ts
handlers.onDelta(content)
```

交给页面追加展示。

`parseStreamMessage` 不是组装 SSE 事件，而是解析 SSE 事件。

后端 `sse_event` 负责把数据组装成 SSE 风格文本；前端 `parseStreamMessage` 负责把这段文本拆回 `{ event, data }`。

### SSE 数据拆分例子

后端可能连续返回：

```text
event: delta
data: {"content":"你好"}

event: delta
data: {"content":"，这是第二段"}

event: done
data: {"record_id":12}

```

前端第一层按 `\n\n` 拆，这是拆“事件和事件”：

```ts
const messages = buffer.split("\n\n");
```

得到：

```ts
[
  'event: delta\ndata: {"content":"你好"}',
  'event: delta\ndata: {"content":"，这是第二段"}',
  'event: done\ndata: {"record_id":12}',
  ''
]
```

然后对每个完整 message 调用 `parseStreamMessage`。

例如传入：

```text
event: delta
data: {"content":"你好"}
```

`parseStreamMessage` 内部第二层按 `\n` 拆，这是拆“同一个事件里的每一行”：

```ts
const lines = rawMessage.split("\n");
```

得到：

```ts
[
  "event: delta",
  'data: {"content":"你好"}'
]
```

最终解析成：

```ts
{
  event: "delta",
  data: '{"content":"你好"}'
}
```

然后 `handleStreamMessage` 再用 `JSON.parse(message.data)` 得到真正的数据对象，并调用 `handlers.onDelta(content)`。

### `trimStart()` 和 `dataLines.join("\n")`

`trimStart()` 只删除开头空白，不删除尾部空白。

例如：

```text
data: {"content":"你好"}
```

去掉 `data:` 后会得到：

```text
 {"content":"你好"}
```

前面多了一个空格，`trimStart()` 会把这个开头空格去掉。

`dataLines.join("\n")` 是为了处理同一个 SSE 事件里有多行 `data:` 的情况。

例如：

```text
event: delta
data: 第一行
data: 第二行
```

会得到：

```ts
dataLines = ["第一行", "第二行"]
```

再通过：

```ts
dataLines.join("\n")
```

拼成：

```text
第一行
第二行
```

注意：`\n\n` 是事件之间的分隔符；`dataLines.join("\n")` 是同一个事件内部多行 `data` 的合并。

### `api.ts` 流式数据格式转换链路

`api.ts` 里的流式数据可以按“数据格式变化”来理解：

```text
后端返回的网络数据
-> Uint8Array 二进制块
-> SSE 文本字符串
-> 单条 SSE message 字符串
-> { event, data } 普通 JS 对象
-> data 内部的 JSON 字符串
-> 业务 JS 对象
-> 页面状态 streamingReport / result
```

对应代码流程：

```ts
const response = await fetch(`${API_BASE_URL}/api/reflections/stream`, ...)
```

这一步拿到的是 `Response` 对象。它不是最终数据，只是代表这次 HTTP 响应。

```ts
const reader = response.body.getReader();
```

`response.body` 是浏览器的可读流。`getReader()` 拿到读取器，用来一块一块读数据。

```ts
const { done, value } = await reader.read();
```

这里的 `value` 是二进制数据，类型接近 `Uint8Array`，还不是字符串，也不是 JSON 对象。

```ts
buffer += decoder.decode(value, { stream: true });
```

`TextDecoder.decode` 把二进制块转成字符串。转换后类似：

```text
event: delta
data: {"content":"你好"}

event: delta
data: {"content":"第二段"}

```

这是 SSE 文本字符串。

```ts
const messages = buffer.split("\n\n");
buffer = messages.pop() ?? "";
```

`\n\n` 是 SSE 事件之间的分隔符。

拆完后，每个 `message` 类似：

```text
event: delta
data: {"content":"你好"}
```

注意，这仍然是字符串，不是 JSON。

```ts
const message = parseStreamMessage(rawMessage);
```

`parseStreamMessage` 把 SSE 字符串：

```text
event: delta
data: {"content":"你好"}
```

解析成普通 JS 对象：

```ts
{
  event: "delta",
  data: '{"content":"你好"}'
}
```

这里的 `data` 仍然是字符串，只是它的内容符合 JSON 语法。

```ts
const data = JSON.parse(message.data) as { content?: string };
```

这一步才是 JSON 解析。

它把 JSON 字符串：

```ts
'{"content":"你好"}'
```

转成 JS 对象：

```ts
{ content: "你好" }
```

如果是 `delta`：

```ts
handlers.onDelta(data.content);
```

页面会把内容追加到 `streamingReport`。

如果是 `done`：

```ts
return JSON.parse(message.data) as StreamCreateReflectionResult;
```

得到：

```ts
{ record_id: 12 }
```

最后 `streamCreateReflection` 返回这个 result。

如果是 `error`：

```ts
throw new Error(data.message ?? "流式生成失败。");
```

交给页面显示错误。

整体记忆：

```text
reader.read()
读二进制

TextDecoder.decode()
二进制 -> SSE 字符串

buffer.split("\n\n")
SSE 字符串 -> 单条 SSE message 字符串

parseStreamMessage()
SSE message 字符串 -> { event, data }

JSON.parse(message.data)
JSON 字符串 -> JS 对象

onDelta / return result / throw Error
进入页面业务逻辑
```

### `api.ts` 三个核心职责

`streamCreateReflection` 是桥接函数。

它把底层的流式读取细节封装起来，对页面只暴露两个东西：

- 中间过程：通过 `onDelta(content)` 交给页面实时展示。
- 最终结果：通过 `return { record_id }` 告诉页面保存完成。

`handleStreamMessage` 是事件分发器。

它根据 `message.event` 分三种情况处理：

- `delta`：解析内容并调用 `onDelta`。
- `done`：返回 `{ record_id }`。
- `error`：抛出错误。

`parseStreamMessage` 只解析 SSE 外层，不解析业务 JSON。

它只负责把：

```text
event: delta
data: {"content":"你好"}
```

变成：

```ts
{ event: "delta", data: '{"content":"你好"}' }
```

真正把 `data` 变成业务对象的是 `JSON.parse(message.data)`。

## `page.tsx`

### 为什么提交新复盘时要 `setSelectedRecord(null)`？

提交新复盘时，右侧详情区如果还显示上一条历史记录，会产生混淆。

所以在 `handleCreateReflection` 开始时会执行：

```ts
setStreamingReport("");
setSelectedRecord(null);
```

意思是：

- 清空上一轮生成中的内容。
- 清空旧详情记录。
- 准备展示这一次新的流式生成内容。

否则用户提交新表单后，右侧可能还显示旧的 AI 报告，视觉上会误以为旧报告和新请求有关。

### `setStreamingReport((current) => current + content)` 里的 `current` 是当前值吗？

是。这里用的是 React state setter 的函数式更新写法。

```ts
setStreamingReport((current) => current + content);
```

React 会把当前最新的 `streamingReport` 值传给这个函数。

参数名可以自己定：

```ts
setStreamingReport((prev) => prev + content);
setStreamingReport((oldValue) => oldValue + content);
```

这里不用：

```ts
setStreamingReport(streamingReport + content);
```

是因为流式输出会连续快速触发多次更新，直接使用外层 `streamingReport` 可能拿到旧值。函数式更新更稳，它能基于 React 当前最新状态追加内容。
