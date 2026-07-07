# 阶段 4 设计：接入大模型 API

## 目标

阶段 4 的目标是把阶段 3 的“测试报告”替换为真实的大模型生成报告。

本阶段只实现非流式调用，流式输出放到阶段 5。

## 范围

- 后端从 `.env` 读取大模型配置。
- 后端封装 OpenAI-compatible Chat Completions 调用。
- 后端根据用户复盘表单生成结构化 Markdown 报告。
- 创建复盘记录时，先调用大模型生成 `ai_report`，再保存到 SQLite。
- 前端继续沿用阶段 3 表单、历史列表和详情展示。
- API Key 只允许存在后端环境变量中，不进入前端代码。

## 暂不做

- 流式输出。
- Markdown 渲染组件。
- 多模型切换 UI。
- RAG / Agent / Tool Calling。
- 登录和用户系统。

## 后端设计

新增模块：

- `app/settings.py`：读取环境变量。
- `app/llm_client.py`：封装模型 API 调用。
- `app/prompts.py`：集中管理系统提示词和用户提示词。

环境变量：

```env
LLM_API_KEY=
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4o-mini
LLM_TIMEOUT_SECONDS=60
```

说明：

- `LLM_API_KEY` 必填。
- `LLM_BASE_URL` 支持 OpenAI-compatible endpoint，例如 OpenAI、DeepSeek 或通义千问兼容接口。
- `LLM_MODEL` 根据所用服务商填写。

## 接口变化

`POST /api/reflections`

阶段 3：

- 前端传入 `ai_report` 测试字符串。
- 后端直接保存。

阶段 4：

- 前端不再传 `ai_report`。
- 后端根据表单内容调用大模型生成 `ai_report`。
- 生成成功后保存完整记录。
- 生成失败时返回明确错误，不保存空报告。

## AI 输出格式

要求模型返回固定 Markdown 结构：

```markdown
# 情绪复盘报告

## 1. 事件简要总结

## 2. 主要情绪识别

## 3. 可能的核心担忧

## 4. 可能存在的认知偏差

## 5. 更平衡的解释

## 6. 可以问自己的 3 个问题

## 7. 一个 10 分钟内能完成的小行动

## 8. 温和提醒
```

## 验收

- 后端缺少 `LLM_API_KEY` 时返回清晰错误。
- 模型 API 返回错误状态码时，后端返回可排查的上游错误摘要，但不暴露 API Key。
- 配置有效 API Key 后，前端提交表单可以得到 AI 复盘报告。
- AI 报告保存到 SQLite。
- 历史详情可以展示保存后的报告。
- `npm run build` 通过。
- 后端 Python 文件语法检查通过。
