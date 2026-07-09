# AI / Agent 工程师能力地图与项目阶段覆盖

本文用于记录从前端开发转型到 LLM / Agent 应用工程师时，需要补齐的能力点，以及这些能力在当前项目中的阶段归属。

## 总体路线

当前项目路线按能力递进推进：

```text
基础全栈闭环
-> LLM API 应用
-> 流式输出
-> RAG 知识库检索增强
-> Agent / Tool Calling 工作流
-> 生产化与简历展示
```

这条路线对应学习优先级：

```text
先做出可用 AI 产品闭环
再让 AI 能基于资料回答
再让 AI 能调用工具做事
最后补生产化、评测、安全和部署
```

## 路线图学习点覆盖情况

| 能力模块 | 路线图学习点 | 当前覆盖情况 |
| --- | --- | --- |
| 基础全栈工程 | TypeScript、React / Next.js、组件、状态管理、FastAPI、REST API、数据库、日志、Docker、Linux | 已覆盖前端、FastAPI、REST、SQLite、Linux 基础；未覆盖 Docker、鉴权、系统化日志、PostgreSQL / MySQL |
| LLM 应用基础 | OpenAI-compatible API、Prompt Engineering、上下文管理、Token / 成本、错误重试、多轮对话、模型切换、流式响应 | 已覆盖 API、Prompt、上下文、错误处理、流式响应；未系统覆盖 Token / 成本、多轮对话、模型切换 |
| RAG | 文档解析、Chunking、Embedding、向量数据库、检索、重排、引用来源 | 阶段 6 覆盖基础 RAG；Reranker 和检索评估作为后续增强 |
| Agent / 工作流 | Tool Calling、LangChain / LangGraph、Workflow、Planning、Memory、Human-in-the-loop、多步骤任务执行 | 阶段 7 覆盖 Tool Calling、简单工作流、Memory、Human-in-the-loop、LangGraph 基础 |
| 生产化与运维 | 日志、Tracing、反馈闭环、Prompt 版本、评测、缓存、限流、异步任务、成本控制、CI/CD、异常处理 | 阶段 8 覆盖 |
| 加分项 | Dify / Coze、LlamaIndex、AutoGen、MCP、本地模型、vLLM、Reranker、多 Agent、AI Coding 工具 | 不作为 MVP 主线；MCP、Reranker 可作为阶段 7/8 加分项 |

## 后续阶段归属

### 阶段 6：RAG 知识库检索增强

MVP 必做：

- 内置或导入少量知识库资料。
- 文档解析。
- 文本切分 Chunking。
- Embedding 向量化。
- 向量检索 top-k。
- 将检索结果注入 Prompt。
- AI 报告展示参考依据或引用片段。
- 无检索命中时降级为普通 LLM 复盘。

阶段 6 后半或后续增强：

- Reranker。
- 检索效果评估。
- RAG 安全基础提醒，例如外部资料 Prompt Injection 风险。

### 阶段 7：Agent / Tool Calling 工作流

MVP 必做：

- 设计可被 AI 调用的后端工具函数。
- 实现 Tool Calling 基础流程。
- 让 AI 根据用户输入决定是否查询历史记录、生成行动计划或更新反馈。
- 引入简单工作流状态，避免只做单轮问答。
- 工具调用日志。

阶段 7 后半或加分项：

- Memory / 状态管理。
- Human-in-the-loop，关键操作前需要用户确认。
- LangGraph 基础。
- 工具权限边界。
- MCP 初步了解。

### 阶段 8：生产化与简历展示

MVP 必做：

- Markdown 渲染。
- 表单校验。
- Loading / Error / Retry 状态。
- 免责声明和隐私提示完善。
- README、截图、项目亮点和简历描述完善。

生产化增强：

- LLM Evals / 回归评测。
- Tracing / Observability。
- Prompt 版本管理。
- Token 成本统计。
- 缓存、限流、超时、重试。
- Prompt Injection / 敏感信息防护。
- Docker / 部署 / CI/CD。
- PostgreSQL 或 MySQL。

## 当前不提前实现的内容

以下内容有价值，但不适合在阶段 6 一开始就做：

- MySQL / PostgreSQL：更偏生产化数据库替换，放到阶段 8。
- 复杂 Agent：需要 RAG、工具调用、状态管理基础，放到阶段 7。
- LangChain / LangGraph 全量学习：先围绕项目需要引入，不为了套框架而套框架。
- Reranker 和自动评测：属于 RAG 质量优化，基础 RAG 跑通后再做。
- 完整安全体系：RAG 和 Agent 阶段先建立风险意识，系统化防护放到阶段 8。

## 学习原则

- 优先做能放进简历的项目能力，不只堆概念。
- 每个阶段都要有可运行、可验证的产物。
- 工具和框架为项目目标服务，不为了使用某个框架而改造项目。
- 先建立工程闭环，再逐步补质量、安全、评测和部署。
