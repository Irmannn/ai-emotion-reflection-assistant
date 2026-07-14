# 阶段 6 设计：RAG 知识库检索增强

## 目标

阶段 6 的目标是让 AI 复盘报告不只依赖模型自身知识，而是能先检索项目内置的情绪复盘/心理学自助资料，再结合资料生成回答。

阶段 6 完成后，用户提交复盘时，后端会：

```text
用户输入
-> 生成检索 query
-> 检索相关知识片段
-> 把知识片段注入 Prompt
-> 调用大模型生成复盘报告
-> 保存 AI 报告和引用来源
-> 前端展示报告和参考资料
```

## MVP 范围

阶段 6 只做基础 RAG 闭环：

- 内置少量心理学/情绪复盘知识资料。
- 将资料切分成 chunk。
- 为 chunk 生成 embedding。
- 将 chunk 和 embedding 存到 SQLite。
- 用户提交复盘时，基于输入检索 top-k 相关 chunk。
- 将检索结果注入 Prompt。
- AI 报告中体现“参考资料依据”。
- 前端展示本次复盘使用到的参考资料。

## 暂不做

- 文件上传。
- 复杂 PDF / Word 解析。
- 多知识库管理。
- Reranker。
- 自动化检索评测。
- 向量数据库服务化部署。
- 权限系统。
- 完整 RAG 安全体系。

这些能力后续可放到阶段 6 后半或阶段 8。

## 为什么先用内置资料

第一版 RAG 的重点是理解完整链路：

```text
资料 -> chunk -> embedding -> 检索 -> 注入 Prompt -> 带依据生成
```

如果一开始就做文件上传、PDF 解析和多知识库管理，容易把学习重点从 RAG 主链路转移到文件工程细节上。

因此阶段 6 先使用项目内置 Markdown 文档作为知识库资料。

## 建议目录结构

```text
backend/
├── knowledge_base/
│   ├── emotion_basics.md
│   ├── cognitive_distortions.md
│   └── communication_and_action.md
├── app/
│   ├── rag/
│   │   ├── __init__.py
│   │   ├── chunking.py
│   │   ├── embeddings.py
│   │   ├── retrieval.py
│   │   └── ingestion.py
│   ├── models.py
│   ├── schemas.py
│   ├── prompts.py
│   └── llm_client.py
```

## 数据模型设计

新增知识 chunk 表：

```text
knowledge_chunks
```

建议字段：

```text
id              主键
source          来源文件名或资料名
title           chunk 标题
content         chunk 文本内容
embedding       embedding 向量，第一版可用 JSON 字符串保存
created_at      创建时间
```

第一版先把 embedding 存在 SQLite 中，格式可用 JSON 字符串：

```json
[0.012, -0.034, 0.128]
```

这样不需要额外启动向量数据库，便于学习和本地运行。

## Embedding 方案

阶段 6 需要新增 embedding 调用能力。

当前已验证阿里百炼工作空间 OpenAI-compatible embedding 接口可用：

```env
EMBEDDING_API_KEY=阿里百炼 API Key
EMBEDDING_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
EMBEDDING_MODEL=text-embedding-v4
EMBEDDING_DIMENSIONS=1024
```

如果使用百炼工作空间专属 endpoint，可以将 `EMBEDDING_BASE_URL` 替换为控制台提供的工作空间地址，例如：

```env
EMBEDDING_BASE_URL=https://你的工作空间地址/compatible-mode/v1
```

注意：生成报告的 `LLM_*` 配置和向量生成的 `EMBEDDING_*` 配置分开维护。当前项目可以继续使用现有 LLM 反代 API 生成报告，同时使用阿里百炼生成 embedding。

后端新增函数：

```python
generate_embedding(text: str) -> list[float]
```

用于：

- 知识库入库时，为每个 chunk 生成向量。
- 用户提交复盘时，为检索 query 生成向量。

## Chunking 方案

第一版使用简单规则切分：

- 读取 Markdown 文件。
- 按二级标题或段落切分。
- 每个 chunk 控制在约 300-800 中文字符。
- 保留来源文件和标题。

暂不做复杂 token-aware chunking。

## 检索方案

第一版使用余弦相似度：

```text
query_embedding
-> 遍历 knowledge_chunks
-> 计算 cosine similarity
-> 排序
-> 取 top-k
```

默认：

```text
top_k = 3
```

数据量小，用 SQLite + Python 遍历即可。后续数据量变大再考虑 pgvector、Milvus、FAISS。

## Prompt 设计

阶段 6 需要改造用户 Prompt。

原流程：

```text
用户输入 -> Prompt -> LLM
```

新流程：

```text
用户输入 -> 检索相关资料 -> Prompt 包含资料片段 -> LLM
```

Prompt 中应明确：

- 优先参考给定资料。
- 不要把资料当成诊断依据。
- 如果资料不足，可以基于用户输入进行一般性分析。
- 报告末尾列出“参考资料”。

## 后端流程

### 知识库入库

第一版可先提供命令行脚本：

```bash
cd backend
source .venv/bin/activate
python -m app.rag.ingestion
```

流程：

```text
读取 backend/knowledge_base/*.md
-> chunking
-> 调 embedding API
-> 写入 knowledge_chunks 表
```

### 用户生成复盘

非流式和流式创建接口都应接入 RAG：

```text
ReflectionCreate payload
-> 构造检索 query
-> query embedding
-> top-k 检索
-> 构造带资料的 Prompt
-> 调用 LLM
-> 保存 AI 报告
-> 保存引用来源
-> 返回给前端
```

第一版可以优先改流式接口，非流式接口保持可用；如果改动成本不高，再让两者共用 RAG prompt 构造逻辑。

## 前端展示

详情页新增“参考资料”区域。

展示内容：

```text
资料标题
来源文件
引用片段摘要
```

生成中阶段仍然优先展示流式报告，生成完成后展示完整详情和参考资料。

## 接口和 Schema 变化

`ReflectionDetail` 建议新增：

```text
references: list[KnowledgeReference]
```

第一版如果不想新增关联表，可以先把引用来源作为 JSON 字符串保存到 `reflection_records` 中。

更清晰的方案是新增表：

```text
reflection_references
```

字段：

```text
id
reflection_id
knowledge_chunk_id
source
title
content_preview
score
```

阶段 6 建议使用新增表，因为这更贴近真实 RAG 应用的数据结构。

## 错误处理

- 知识库为空：正常降级为普通 LLM 复盘。
- Embedding API 失败：返回明确错误，前端保留表单。
- 检索无结果：正常降级为普通 LLM 复盘。
- 引用保存失败：生成失败，不保存半成品记录。

## 安全边界

阶段 6 先建立基础边界：

- 知识库资料只使用本地可信 Markdown。
- `backend/knowledge_base/*.md` 默认不提交到 Git，避免上传私有或授权不明的资料正文。
- 入库命令会把 chunk 文本发送给配置的 Embedding API 生成向量，执行前需要确认这些资料可以发送到对应服务商。
- Prompt 中明确资料仅作心理学自助参考，不构成诊断。
- 不允许知识库内容覆盖系统安全指令。

完整 Prompt Injection 防护放到阶段 8。

## 验收标准

- 可以通过命令行导入内置知识库资料。
- 数据库中能看到知识 chunk 和 embedding。
- 用户提交复盘时，后端能检索 top-k 相关资料。
- AI 报告能结合检索结果生成。
- 前端详情页能展示本次使用到的参考资料。
- 知识库为空或无命中时，系统能正常降级。
- 流式输出仍然可用。
- 生成失败时表单内容仍然保留。

## 学习重点

阶段 6 重点理解：

- 什么是 RAG。
- 为什么要 chunk。
- embedding 是什么。
- 向量相似度检索是什么。
- 检索结果如何注入 Prompt。
- 为什么需要引用来源。
- RAG 和普通 LLM 调用的区别。
