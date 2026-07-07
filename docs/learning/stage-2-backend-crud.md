# 阶段 2：SQLite 数据库与 CRUD 接口

## 阶段目标

- 接入 SQLite。
- 使用 SQLModel 定义 `reflection_records` 表。
- 拆分数据库、模型、schema、路由文件。
- 实现创建、列表、详情、删除、反馈接口。
- 通过 `session_id` 做匿名数据隔离。

## 核心文件

- `backend/app/database.py`：数据库 engine、Session、建表。
- `backend/app/models.py`：数据库表模型。
- `backend/app/schemas.py`：API 请求体和响应体结构。
- `backend/app/routers/reflections.py`：复盘记录 CRUD 路由。
- `backend/app/main.py`：FastAPI 应用入口，挂载路由和初始化数据库。

## 数据库与 ORM

### ORM

ORM 是 Object-Relational Mapping，对象关系映射。它用 Python 类和对象表达数据库表和记录，减少手写 SQL。

### `models.py`

`ReflectionRecord(SQLModel, table=True)` 对应 SQLite 表 `reflection_records`。

- 类属性对应表字段。
- `Field(...)` 添加数据库/校验配置。
- `primary_key=True` 表示主键。
- `index=True` 表示建索引。
- `default_factory=utc_now` 表示每次创建记录时调用函数生成默认值。

### 索引

索引可以理解成数据库为字段建立目录。经常按 `session_id` 查询，所以给它建索引可以减少全表扫描。

### UTC 时间

- 数据库存 UTC。
- 展示时再转用户本地时间。
- SQLite 没有真正的带时区 datetime 类型，读出时可能丢失时区标记。

## `database.py`

### `engine`

`engine` 是数据库入口/连接工厂。

### `Session`

`Session` 是 ORM 层的一次数据库操作会话，业务代码通过 `session.add/exec/commit/delete` 操作数据库。

### `with Session(engine) as session`

这是上下文管理器，用来创建并自动关闭数据库 Session。

### `yield session`

FastAPI 依赖注入中，`yield session` 把数据库 Session 暂时交给接口函数使用；接口结束后退出 `with`，自动关闭 Session。

### `check_same_thread=False`

SQLite 默认要求连接只在创建它的线程里使用。FastAPI 同步接口可能在线程池执行，所以常配置 `check_same_thread=False`。

## `schemas.py`

### `models.py` vs `schemas.py`

- `models.py` 面向数据库，定义怎么存。
- `schemas.py` 面向 API，定义怎么收和怎么返。

### `table=True`

- 有 `table=True`：数据库表模型。
- 没有 `table=True`：普通 API 数据结构，不建表。

### `Literal`

`Literal["helpful", "not_helpful"]` 限制字段只能取固定值，类似 TypeScript 的字符串联合类型。

### `list[str]`

Python 的 `list[str]` 对应 JSON 数组和 TypeScript 的 `string[]`。

## `reflections.py`

### `APIRouter`

`APIRouter` 用于模块化管理一组相关接口。FastAPI 不像 Next/Nuxt 那样目录自动生成路由，需要显式创建 router、注册接口、在 `main.py` 中 include。

### path / query / payload

- path 参数：路径模板里的 `{record_id}`。
- query 参数：URL `?session_id=xxx`。
- payload/body：POST 请求体 JSON。

### `Depends(get_session)`

FastAPI 依赖注入，表示接口需要数据库 Session，框架自动调用 `get_session()`。

### `Query(..., min_length=1)`

`...` 表示必填，`min_length=1` 表示最短长度为 1。

### `session.add / commit / refresh`

- `add`：把对象加入 Session 管理。
- `commit`：把变更提交到数据库。
- `refresh`：从数据库重新读取最新对象，常用于拿到新生成的 id 和默认值。

## `/docs`

FastAPI 自动根据路由、请求体、响应体、类型标注和校验规则生成 Swagger UI 文档，可直接测试接口。

## 阶段卡点

- 后端接口验证时曾出现 500，原因是服务仍运行旧代码/旧 schema 状态。
- `--reload` 不一定能恢复所有运行态问题，必要时重启后端并刷新 `/docs`。

## 阶段复盘

- 日期：2026-07-01
- 已完成：SQLite + SQLModel + CRUD 接口。
- 验证结果：创建、列表、详情、反馈、删除、session 隔离均通过。
