# AI 情绪复盘助手 MVP PRD

## 1. 项目名称

AI 情绪复盘助手

## 2. 项目定位

这是一个心理学自助记录工具，帮助用户对一次情绪事件进行结构化复盘。

产品目标不是提供心理咨询、心理治疗或精神疾病诊断，而是帮助用户：

- 记录发生了什么
- 识别当时的情绪
- 梳理自动想法
- 发现可能的认知偏差
- 生成更平衡的看法
- 得到一个小而具体的行动建议

## 3. 产品边界

本产品不提供：

- 心理疾病诊断
- 心理治疗
- 医疗建议
- 药物建议
- 危机干预
- 替代专业心理咨询师的服务

页面需要展示免责声明：

> 本工具仅用于心理学自助记录和情绪复盘，不提供诊断、治疗或医疗建议。如你正在经历严重痛苦、自伤想法或紧急危机，请立即联系身边可信任的人或当地专业机构。

## 4. 第一版目标

完成一个最小 AI 全栈闭环：

React / Next.js 前端 -> FastAPI 后端 -> SQLite 数据库存储 -> 调用大模型 API -> 流式输出 AI 复盘报告 -> 保存历史记录 -> 前端展示历史记录

第一版重点是练习：

- 前端表单
- 后端接口
- SQLite 数据存储
- LLM API 调用
- 流式响应
- Markdown 展示
- 错误处理
- 基础隐私和安全提示

## 5. 技术栈

### 前端

- Next.js
- React
- TypeScript
- Tailwind CSS
- Markdown 渲染库，例如 `react-markdown`

### 后端

- Python
- FastAPI
- SQLite
- SQLModel 或 SQLAlchemy
- Pydantic
- python-dotenv

### AI

第一版接入一个大模型 API：

- DeepSeek API
- 或 OpenAI API
- 或通义千问 API

API Key 必须只存在后端环境变量中，不允许暴露到前端。

## 6. 用户流程

### 6.1 首次进入

用户打开首页后看到：

- 产品名称
- 产品说明
- 免责声明
- “开始复盘”按钮

### 6.2 填写情绪复盘表单

用户填写以下字段：

- 事件描述：今天发生了什么？
- 情绪标签：焦虑、愤怒、委屈、悲伤、羞耻、内疚、失望、压力、其他
- 情绪强度：1-10 分
- 自动想法：当时脑子里冒出了什么念头？
- 身体反应：如心跳加速、胸闷、胃不舒服、头痛、疲惫等
- 重点分析方向：情绪理解、认知偏差、人际关系、行动建议、综合分析

### 6.3 生成 AI 复盘报告

用户点击“生成复盘报告”后：

- 前端向后端提交表单
- 后端调用大模型 API
- 前端以流式方式展示生成内容
- 生成完成后，后端将完整记录保存到 SQLite
- 前端展示生成完成状态

### 6.4 查看历史记录

用户可以查看历史复盘列表。

列表展示：

- 创建时间
- 情绪标签
- 情绪强度
- 事件摘要
- 是否已反馈

用户点击某条记录后，可以查看完整详情。

### 6.5 删除历史记录

用户可以删除某条历史记录。

### 6.6 用户反馈

用户可以对 AI 复盘结果反馈：

- 有帮助
- 没帮助

反馈保存到数据库。

## 7. AI 输出格式

AI 复盘报告需要使用 Markdown 格式，结构固定为：

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

要求：

- 语气温和、克制、不说教
- 不做医学诊断
- 不声称用户患有某种疾病
- 不承诺疗效
- 不替代专业心理咨询
- 如果用户内容涉及自伤、自杀、伤害他人等风险，需要优先给出安全提示，而不是普通复盘

## 8. 数据库设计

使用 SQLite。

表名：`reflection_records`

字段：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| id | integer | primary key |
| session_id | string | 匿名会话 ID |
| event_text | text | 事件描述 |
| emotion_tags | string | 情绪标签 |
| emotion_intensity | integer | 情绪强度 |
| automatic_thoughts | text | 自动想法 |
| body_reaction | text | 身体反应 |
| focus_area | string | 重点分析方向 |
| ai_report | text | AI 复盘报告 |
| feedback | string, nullable | 用户反馈 |
| created_at | datetime | 创建时间 |
| updated_at | datetime | 更新时间 |

说明：

- 第一版不做登录系统
- 前端生成一个匿名 `session_id`，保存在 `localStorage`
- 每次请求都带上 `session_id`
- 后端根据 `session_id` 查询对应历史记录
- `localStorage` 只允许保存 `session_id` 和表单草稿
- 正式历史记录必须保存到 SQLite

## 9. 后端接口设计

### 9.1 生成复盘报告

`POST /api/reflections/stream`

请求体：

```json
{
  "session_id": "string",
  "event_text": "string",
  "emotion_tags": ["焦虑", "委屈"],
  "emotion_intensity": 7,
  "automatic_thoughts": "string",
  "body_reaction": "string",
  "focus_area": "综合分析"
}
```

响应：

- 使用流式响应
- 前端逐步接收 AI 生成内容
- 生成完成后保存数据库
- 最后返回 `record_id`

### 9.2 获取历史记录列表

`GET /api/reflections?session_id=xxx`

返回：

```json
[
  {
    "id": 1,
    "event_summary": "string",
    "emotion_tags": "焦虑,委屈",
    "emotion_intensity": 7,
    "feedback": null,
    "created_at": "datetime"
  }
]
```

### 9.3 获取历史记录详情

`GET /api/reflections/{id}?session_id=xxx`

返回完整记录。

### 9.4 删除历史记录

`DELETE /api/reflections/{id}?session_id=xxx`

只允许删除当前 `session_id` 对应的数据。

### 9.5 提交反馈

`POST /api/reflections/{id}/feedback`

请求体：

```json
{
  "session_id": "string",
  "feedback": "helpful"
}
```

`feedback` 可选值：

- `helpful`
- `not_helpful`

## 10. 前端页面设计

### 10.1 首页 / 复盘页

包含：

- 产品标题
- 免责声明
- 情绪复盘表单
- 生成按钮
- 清空按钮
- 生成中的 loading 状态
- AI 流式输出区域
- Markdown 渲染

### 10.2 历史记录页

包含：

- 历史记录列表
- 情绪标签
- 情绪强度
- 创建时间
- 事件摘要
- 删除按钮
- 查看详情按钮

### 10.3 历史详情页

包含：

- 原始输入
- AI 复盘报告
- 用户反馈按钮
- 删除按钮

## 11. 错误处理

需要处理：

- 表单为空
- 情绪强度不在 1-10 之间
- 后端接口异常
- 大模型 API 调用失败
- 网络中断
- 流式输出中断
- 数据库写入失败

前端需要给用户清晰提示，例如：

- “生成失败，请稍后重试”
- “网络异常，请检查连接”
- “请先填写事件描述”

## 12. 安全与隐私

第一版需要做到：

- API Key 不暴露到前端
- 页面展示隐私提示
- 用户可以删除历史记录
- 不采集真实姓名、手机号、身份证等个人身份信息
- 不做登录系统
- 不把内容发送给除大模型 API 以外的第三方服务

## 13. 暂不做的功能

第一版不做：

- 用户登录
- 支付
- 心理测评量表
- 专业咨询师匹配
- RAG 知识库
- Agent 工作流
- 长期记忆
- 多轮对话
- 向量数据库
- 移动端 App
- 数据可视化大屏

## 14. 第一版验收标准

项目完成后，需要满足：

- 前端可以填写情绪复盘表单
- 后端 FastAPI 可以正常启动
- SQLite 数据库可以自动初始化
- 后端可以调用大模型 API
- 前端可以看到流式输出
- AI 报告使用 Markdown 展示
- 生成完成后记录保存到 SQLite
- 前端可以查看历史记录
- 前端可以查看历史详情
- 前端可以删除历史记录
- 用户可以提交“有帮助 / 没帮助”反馈
- 页面有免责声明
- API Key 不暴露在前端
- 项目 README 写清楚启动方式
