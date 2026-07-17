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
-> 有状态 Agent
-> LangChain 组件化
-> LangGraph 状态工作流
-> RAG 与数据层升级
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
| 基础全栈工程 | TypeScript、React / Next.js、组件、状态管理、FastAPI、REST API、数据库、日志、Docker、Linux | 已覆盖前端、FastAPI、REST、SQLite、Linux 基础；阶段 11/12 补 PostgreSQL、Docker、鉴权、系统化日志 |
| LLM 应用基础 | OpenAI-compatible API、Prompt Engineering、上下文管理、Token / 成本、错误重试、多轮对话、模型切换、流式响应 | 已覆盖 API、Prompt、基础错误处理、流式响应；阶段 8 补多轮上下文，阶段 9 补模型抽象，阶段 12 补成本、自动重试和降级 |
| RAG | 文档解析、Chunking、Embedding、向量数据库、检索、重排、引用来源 | 阶段 6 覆盖基础 RAG；阶段 11 补 pgvector、Reranker 和检索评估 |
| Agent / 工作流 | Tool Calling、LangChain / LangGraph、Workflow、Planning、Memory、Human-in-the-loop、多步骤任务执行 | 阶段 7 已覆盖原生 Tool Calling、工具日志和权限边界；阶段 8 补短期会话记忆，阶段 9 学 LangChain，阶段 10 学 LangGraph、摘要/长期记忆和 Human-in-the-loop |
| 生产化与运维 | 日志、Tracing、反馈闭环、Prompt 版本、评测、缓存、限流、异步任务、成本控制、CI/CD、异常处理 | 阶段 12 覆盖核心生产化能力 |
| 加分项 | Dify / Coze、LlamaIndex、AutoGen、MCP、本地模型、vLLM、Reranker、多 Agent、AI Coding 工具 | 不作为 MVP 主线；MCP 可在阶段 10 后扩展，Reranker 作为阶段 11 增强项 |

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

### 阶段 7：原生 Agent / Tool Calling 工作流

MVP 必做：

- 设计可被 AI 调用的后端工具函数。
- 实现 Tool Calling 基础流程。
- 让 AI 根据用户输入决定是否查询历史记录或复盘详情。
- 工具调用日志。
- 工具权限边界。

阶段 7 后续阶段处理：

- 阶段 8：多轮对话、上下文管理和短期会话记忆。
- 阶段 9：LangChain 基础。
- 阶段 10：LangGraph、摘要/长期记忆和 Human-in-the-loop。
- 后续加分项：MCP 初步了解。

### 阶段 8：有状态流式 Agent

MVP 必做：

- Agent 会话、消息和工具调用结果持久化。
- 多轮对话与最近消息上下文管理。
- Agent SSE 流式回答与工具执行过程事件。
- 手动重试、失败内容保留、模型名和耗时记录。

阶段边界：

- 先完成短期会话记忆，不提前实现摘要记忆、跨会话长期记忆或 LangGraph。

### 阶段 9：LangChain 组件化

- 用 LangChain 的模型、消息、Prompt、Tool 和 Retriever 抽象现有 LLM、RAG 和工具调用能力。
- 建立后端模型配置层，理解模型切换的基础结构。
- 保留业务工具执行、数据库访问和权限校验在自有后端代码中。

### 阶段 10：LangGraph 状态工作流

- 用状态图编排记忆读取、RAG、工具循环、回答生成和结果保存。
- 实现摘要记忆、基础长期记忆和 Human-in-the-loop。
- 理解节点、状态、分支、循环和可恢复工作流。

### 阶段 11：RAG 与数据层升级

- SQLite 迁移 PostgreSQL，使用 pgvector 处理向量检索。
- 引入 Reranker、检索测试集和引用质量评估。
- 建立 RAG 无命中降级及 Prompt Injection 基础防护。

### 阶段 12：生产化与简历展示

- LLM Evals / 回归评测、Tracing、Prompt 版本、Token 成本统计。
- 自动重试、主备模型降级、限流、缓存和异常处理。
- Docker / 部署 / CI/CD、README、截图、项目亮点和简历描述。
- 可选 WebSocket 长任务进度练习；文本生成场景继续优先使用 SSE。

## 当前不提前实现的内容

以下内容有价值，但不适合在阶段 6 一开始就做：

- PostgreSQL / pgvector：基础 RAG 与 Agent 跑通后，于阶段 11 统一升级。
- LangChain：在理解原生 API、Tool Calling 和 SSE 后，于阶段 9 作为组件抽象引入。
- LangGraph：在已有会话、上下文和工具循环基础上，于阶段 10 作为状态工作流框架引入。
- Reranker 和自动评测：属于 RAG 质量优化，放到阶段 11/12。
- 完整安全体系：先建立风险意识，系统化防护放到阶段 12。

## 学习原则

- 优先做能放进简历的项目能力，不只堆概念。
- 每个阶段都要有可运行、可验证的产物。
- 工具和框架为项目目标服务，不为了使用某个框架而改造项目。
- 先建立工程闭环，再逐步补质量、安全、评测和部署。
