# 通用概念词典

## Web 与 API

### 同源与跨域

浏览器判断同源看三项：协议、完整主机名、端口。三者完全一致才是同源。

### CORS

CORS 是浏览器的跨域安全机制。当前项目中前端 `localhost:3000` 请求后端 `localhost:8000`，端口不同，所以需要后端允许跨域。

### REST API

REST API 把后端数据看作资源，用 URL 表示资源，用 HTTP 方法表示动作。

- GET：获取数据。
- POST：创建/提交。
- PUT：整体更新。
- PATCH：局部更新。
- DELETE：删除数据。

### path / query / payload

- path：路径参数，例如 `/api/reflections/{id}`。
- query：URL `?` 后面的参数。
- payload/body：请求体 JSON。

## JSON 与时间

### JSON

JSON 只有 string、number、boolean、null、object、array 等基础类型，没有 datetime。

### UTC

UTC 是全球统一时间基准，不是时间戳。数据库一般存 UTC，展示时转本地时间。

### `Date` 和 `toLocaleString`

前端 `new Date(...)` 把时间字符串转成 JS Date 对象。`toLocaleString` 按浏览器语言、地区、时区格式化展示。

## Git 与环境

### `.env.example` 和 `.env`

- `.env.example`：配置模板，可以提交。
- `.env`：本地真实配置，包含密钥，不能提交。

### `.gitignore`

忽略依赖、构建缓存、虚拟环境、数据库、密钥文件等本地生成物。

### WSL 原生目录

当前有效项目目录：

```bash
/home/yunyun/projects/mind-intelligence-agent
```

旧目录 `/mnt/c/yun_project/mind-intelligence-agent` 不再作为开发目录，避免文件监听、SQLite 和缓存问题。

## Python 基础

### `-m`

`python -m module` 表示按模块名运行当前 Python 环境里的模块。

### `with` / `async with`

上下文管理器语法，用来保证资源用完释放。

- `with open(...)`：文件。
- `with Session(engine)`：数据库 Session。
- `async with httpx.AsyncClient()`：异步 HTTP 客户端。

### tuple

tuple 是 Python 的有序、通常不可修改的数据结构，用圆括号表示。例如 `("a", "b")`。

### 装饰器

`@xxx` 放在函数上方，表示给函数附加能力，本质类似 `func = xxx(func)`。

## TypeScript / React

### `Promise<T>`

表示异步结果。成功 resolve 出 `T`，失败 reject 错误。

### 泛型 `<T>`

类型参数，让函数返回类型由调用方决定。

### 可选链 `?.`

`init?.headers` 表示 `init` 是 `null` 或 `undefined` 时不继续读取属性，直接返回 `undefined`。

### 类型断言 `as`

告诉 TypeScript 按某个类型看待值，不改变运行时值。

### React 函数组件

函数接收 props/state，返回 TSX 描述 UI。现代 React 主流是函数组件 + Hooks。
