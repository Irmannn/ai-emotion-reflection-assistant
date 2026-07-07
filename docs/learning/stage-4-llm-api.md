# 阶段 4：大模型 API 接入

## 阶段目标

- 后端从 `.env` 读取模型 API Key。
- 后端封装模型调用函数。
- 根据用户输入生成结构化 Markdown 复盘报告。
- 非流式返回并保存到 SQLite。
- 前端展示 AI 报告。

## 新增文件

- `backend/.env.example`：环境变量模板。
- `backend/app/settings.py`：读取 `.env` 配置。
- `backend/app/prompts.py`：管理系统提示词和用户提示词。
- `backend/app/llm_client.py`：调用 OpenAI-compatible Chat Completions API。
- `docs/STAGE_4_DESIGN.md`：阶段 4 方案设计。

## `.env` 与 API Key 安全

`.env.example` 是模板，可以提交 GitHub；`.env` 是本地真实配置，不能提交。

API Key 只能放后端，因为浏览器 DevTools 能看到前端打包产物、Sources、Network 请求、本地存储和 DOM。只要 API Key 出现在前端代码或请求头里，就可能泄露。

正确链路：

```text
前端 -> FastAPI 后端 -> 大模型服务
```

## `settings.py`

### `Settings(BaseSettings)`

`Settings` 继承 `BaseSettings`，由 Pydantic 负责从环境变量读取配置、类型转换和校验。

核心价值：

- 配置对象化：`settings.llm_api_key`。
- 可缓存：`@lru_cache`。
- 类型转换/校验：例如 `"60"` 转成 `int`。
- 编辑器提示更好。

### `alias`

`alias="LLM_API_KEY"` 表示 `.env` 里的大写变量映射到 Python 字段 `llm_api_key`。

### `model_config`

`model_config = SettingsConfigDict(extra="ignore")` 是 Pydantic v2 特殊类配置，不是普通环境变量字段。

## Python 类和装饰器

- `class Settings(BaseSettings)` 里的括号表示继承。
- `Settings()` 才是创建对象并传参。
- 普通类用 `__init__` 接收参数；Pydantic/BaseSettings 由父类提供初始化逻辑。
- `@lru_cache` 是装饰器，给 `get_settings()` 增加缓存能力。
- `@router.post` 也是装饰器，用来注册 FastAPI 接口。

## `prompts.py`

### Prompt 分层

- `SYSTEM_PROMPT`：角色、安全边界、禁止事项、语气、输出格式。
- user prompt：本次具体输入和任务。

简单记：

```text
system 管“你是谁、边界是什么、格式怎么输出”
user 管“这次要处理什么内容”
```

### 三引号字符串

`"""..."""` 本质是多行字符串。

- 放在模块/类/函数开头且不赋值：docstring。
- 赋值给变量：普通多行字符串。
- `f"""...{value}..."""` 是多行 f-string。

## `llm_client.py`

### 请求 URL

`base_url.rstrip("/")` 去掉右侧 `/`，避免拼出双斜杠。

函数名前加 `_` 是约定：这是模块内部辅助函数，不建议外部直接调用。

### `temperature`

控制模型输出随机性：

- 低：稳定、保守。
- 高：发散、有创意但更容易跑偏。

当前 `0.4` 适合情绪复盘这种需要稳定、克制的场景。

### `httpx.AsyncClient`

`async with httpx.AsyncClient(...) as client` 管理 HTTP 客户端连接资源。

和其他上下文管理器区别：

- `with Session(engine)`：数据库会话。
- `async with httpx.AsyncClient()`：HTTP 网络连接。
- `with open(...)`：文件句柄。

### `json=request_body`

`httpx` 会把 Python dict/list 序列化成 JSON 请求体。

### `raise_for_status()`

检查 HTTP 状态码。2xx 不处理；4xx/5xx 抛 `httpx.HTTPStatusError`。

### 响应解析

OpenAI-compatible Chat Completions 常见响应：

```json
{
  "choices": [
    {
      "message": {
        "role": "assistant",
        "content": "模型生成内容"
      }
    }
  ]
}
```

所以模型文本在：

```py
data["choices"][0]["message"]["content"]
```

### 错误处理

- 缺少 `LLM_API_KEY`：返回 503。
- 上游模型 API 错误：返回 502。
- 响应格式异常：返回 502。

不要所有错误都返回 500。500 是未知后端错误，排查成本高。

阶段 4 增加了上游错误摘要：截取响应正文前 500 字符，不输出请求头或 API Key。

## async / await

`await` 对当前函数来说是等待结果；对整个异步服务来说，会把执行权让给事件循环，等待网络 IO 时可以处理其他任务。

事件循环可以理解成异步任务调度器：任务等待 IO 时切出去，结果回来后再切回来。

## Clash / SOCKS 代理

Clash 可能设置：

```bash
HTTP_PROXY
HTTPS_PROXY
ALL_PROXY=socks5://...
```

`httpx` 默认读取代理环境变量。如果代理是 SOCKS，需要安装：

```text
httpx[socks]
```

它会额外安装 `socksio`。

可用下面命令检查代理环境：

```bash
env | grep -i proxy
```

## `reflections.py` 阶段 4 变化

创建接口从阶段 3 的“前端传测试 `ai_report`”改为：

```text
前端提交表单
-> 后端调用 generate_reflection_report(payload)
-> 生成成功后创建 ReflectionRecord
-> 保存 SQLite
```

如果模型生成失败，不保存空报告记录。

路由层只做编排：接收请求、调用 LLM、写数据库、返回响应。Prompt 和 HTTP 调用细节分别放到 `prompts.py` 和 `llm_client.py`。

## 阶段卡点

- `.env` 修改后需要重启后端，因为 `get_settings()` 有缓存，`--reload` 不一定监听 `.env`。
- `gpt-4o-mini` 不适用于当前 Cockpit/Codex 反代，需改成 `/models` 返回的可用模型。
- Clash 代理导致 `httpx` 需要 SOCKS 支持，已改为 `httpx[socks]`。

## 阶段复盘

- 日期：2026-07-05
- 已完成：`.env` 配置、Prompt 管理、OpenAI-compatible 非流式调用、保存 AI 报告。
- 验证结果：前端提交表单后可生成 AI 报告并保存历史记录。
- 额外修复：生成失败时保留用户表单输入。
