# 阶段 6 学习笔记：RAG 知识库检索增强

## `chunking.py`

### `@dataclass(frozen=True)` 是什么？

`@dataclass` 是 Python 的装饰器，用来快速创建“只存数据的类”。

它会自动生成 `__init__`、`__repr__`、`__eq__` 等常用方法。

例如：

```python
@dataclass(frozen=True)
class TextChunk:
    source: str
    title: str
    content: str
```

可以直接创建：

```python
TextChunk(source="a.md", title="标题", content="内容")
```

`frozen=True` 表示对象创建后不能再修改字段，适合表示稳定的数据片段。

### Python 类型里有 `Path` 吗？

有。

`Path` 来自 Python 标准库：

```python
from pathlib import Path
```

它是路径对象，比普通字符串路径更方便。

例如：

```python
path.name
path.stem
path.read_text()
```

### `stem` 是什么意思？

`path.stem` 是“不带后缀的文件名”。

例如：

```python
Path("龙门心智_4月.md").name
```

结果是：

```text
龙门心智_4月.md
```

```python
Path("龙门心智_4月.md").stem
```

结果是：

```text
龙门心智_4月
```

### 列表推导式执行顺序

代码：

```python
[paragraph.strip() for paragraph in text.split("\n\n") if paragraph.strip()]
```

执行顺序：

```text
1. text.split("\n\n")
2. for paragraph in ...
3. if paragraph.strip()
4. paragraph.strip()
5. 放进新列表
```

等价于：

```python
paragraphs = []
for paragraph in text.split("\n\n"):
    if paragraph.strip():
        paragraphs.append(paragraph.strip())
```

作用：

```text
按空行切段落
去掉每段首尾空白
过滤空段落
```

### `chunks.extend` 是什么？

`extend` 会把另一个列表里的元素逐个加入当前列表。

例如：

```python
chunks = ["a"]
chunks.extend(["b", "c"])
```

结果：

```python
["a", "b", "c"]
```

对比 `append`：

```python
chunks.append(["b", "c"])
```

结果是：

```python
["a", ["b", "c"]]
```

所以当要把多个 chunk 展开加入列表时，用 `extend`。

### Python 三元表达式执行顺序

代码：

```python
candidate = f"{current}\n\n{paragraph}".strip() if current else paragraph
```

结构：

```python
A if 条件 else B
```

意思是：

```text
如果 current 有值
-> candidate = f"{current}\n\n{paragraph}".strip()

否则
-> candidate = paragraph
```

等价于：

```python
if current:
    candidate = f"{current}\n\n{paragraph}".strip()
else:
    candidate = paragraph
```

### `range(0, len(text), MAX_CHUNK_LENGTH)` 是什么？

`range(start, stop, step)` 表示：

```text
从 start 开始
到 stop 之前结束
每次增加 step
```

例如：

```python
range(0, 1800, 800)
```

会生成：

```python
0, 800, 1600
```

当前项目用它按固定长度切文本：

```python
text[0:800]
text[800:1600]
text[1600:2400]
```

### `list[tuple[str, list[str]]]` 是什么意思？

这是类型声明。

从里往外看：

```text
str：字符串
list[str]：字符串数组
tuple[str, list[str]]：一个元组，第一个元素是字符串，第二个元素是字符串数组
list[tuple[str, list[str]]]：一个数组，数组里的每一项都是这种元组
```

具体数据类似：

```python
[
    ("标题1", ["第一行", "第二行"]),
    ("标题2", ["第三行", "第四行"]),
]
```

### `splitlines()` 是什么？

`splitlines()` 会按行切分字符串。

例如：

```python
"a\nb\nc".splitlines()
```

结果：

```python
["a", "b", "c"]
```

它比 `split("\n")` 更通用，因为能兼容不同系统的换行符。

### `if current_lines` 是判断数组是否为空吗？

是。

Python 里空列表是 falsy：

```python
if []:
    # 不会执行
```

非空列表是 truthy：

```python
if ["a"]:
    # 会执行
```

所以：

```python
if current_lines:
```

意思是：如果当前已经收集到了一些行，才执行。

### `lstrip("#")` 是什么？

`lstrip` 会从字符串左侧删除指定字符。

例如：

```python
"### 标题".lstrip("#")
```

结果：

```text
 标题
```

再接：

```python
.strip()
```

去掉首尾空格，得到：

```text
标题
```

所以：

```python
stripped.lstrip("#").strip()
```

就是把 Markdown 标题前面的 `#` 去掉，拿到纯标题文本。

### `split_by_length` 方法的逻辑

`split_by_length` 的目标是：把一整篇文本按段落合并成多个 chunk，并尽量让每个 chunk 不超过 `MAX_CHUNK_LENGTH = 800`。

核心变量：

```text
chunks：已经切好的 chunk 列表
current：正在组装的 chunk
paragraph：当前正在处理的段落
candidate：尝试把 paragraph 合并进 current 后得到的新内容
```

执行流程：

```text
1. 先用 text.split("\n\n") 按空行切成段落。
2. 遍历每个 paragraph。
3. 如果单个 paragraph 本身超过 800，就先保存已有 current，再用 split_long_text 硬切长段落。
4. 如果 paragraph 不长，就尝试和 current 合并成 candidate。
5. 如果 candidate 不超过 800，就继续放进 current。
6. 如果 candidate 超过 800，并且 current 已经至少 80 字符，就把 current 存入 chunks，然后用 paragraph 开启新的 current。
7. 如果 current 太短，不希望切出过短 chunk，就先合并成 candidate。
8. 循环结束后，把最后的 current 放进 chunks。
```

一句话总结：

```text
split_by_length 会尽量按段落合并文本，让每个 chunk 接近但不超过 800 字符，同时避免切出太短的 chunk。
```

### 为什么当前没有使用 `split_markdown_sections`？

`split_markdown_sections` 原本用于按 Markdown 标题切分文档。

但当前知识库资料来自 XMind 结构化导出，标题层级非常碎，很多有效内容都在标题里。

如果直接按标题切分，会出现几个问题：

```text
chunk 数量暴增
每个 chunk 过短
embedding 调用成本增加
检索噪音变大
上下文语义不完整
```

实际测试中，按标题切分会产生 2000 多个 chunk；改成按整篇文档长度合并切分后，18 个 Markdown 文件约产生 97 个 chunk，更适合阶段 6 MVP。

所以当前主流程是：

```text
chunk_markdown_file
-> 读取整篇 Markdown
-> split_by_length 按长度和段落切分
```

`split_markdown_sections` 先保留，后续如果优化文档来源结构，例如把资料整理成更标准的 Markdown 二级标题和正文结构，可以再考虑改造成标题感知切分。

## `embeddings.py`

### 为什么 embedding 向量要用 `float`？

Embedding 向量本质上是一组浮点数。

例如阿里百炼返回的向量类似：

```python
[
    -0.06613187491893768,
    0.027436112985014915,
    -0.0042335097678005695,
]
```

这些值是小数，不是整数，所以类型应该是 `float`。

后续计算相似度时需要做数学运算：

```python
dot_product = sum(a * b for a, b in zip(left, right))
```

如果向量值是字符串，例如 `"0.0274"`，就不能可靠地参与数学计算。

所以代码里写：

```python
return [float(value) for value in embedding]
```

目的：

```text
1. 确保每个向量值都是浮点数。
2. 让后续 cosine similarity 可以正常计算。
```

可以简单理解为：

```text
embedding = 文本的数学坐标
float = 坐标里的小数值
```

## `ingestion.py`

### `ingestion.py` 的作用

`ingestion.py` 是知识库离线入库脚本。

它不是用户每次提交复盘时都运行，而是在准备好知识库资料后手动执行：

```bash
cd backend
source .venv/bin/activate
python -m app.rag.ingestion
```

它负责把本地 Markdown 知识库转换成 SQLite 中的可检索向量数据。

整体流程：

```text
backend/knowledge_base/*.md
-> chunk_markdown_file 切分文本
-> generate_embedding 调用 embedding API 生成向量
-> KnowledgeChunk 保存 chunk 原文和向量
-> 写入 SQLite
```

一句话总结：

```text
ingestion.py 是 RAG 的“资料准备阶段”，把原始资料处理成后续在线检索能使用的数据。
```

### `Path(__file__).resolve().parents[2] / "knowledge_base"` 是什么？

`__file__` 表示当前 Python 文件路径：

```text
backend/app/rag/ingestion.py
```

`Path(__file__)` 把字符串路径变成 `Path` 对象。

`.resolve()` 会转成绝对路径。

`.parents[0]` 是当前文件父目录：

```text
backend/app/rag
```

`.parents[1]` 是：

```text
backend/app
```

`.parents[2]` 是：

```text
backend
```

所以：

```python
Path(__file__).resolve().parents[2] / "knowledge_base"
```

最终得到：

```text
backend/knowledge_base
```

`/` 在 `Path` 里不是除法，而是拼接路径。

### 为什么要 `json.dumps(embedding)`？

`embedding` 是 Python 数组：

```python
[0.1, 0.2, 0.3]
```

SQLite 没有原生的 `list[float]` 字段类型。

所以保存前先转成 JSON 字符串：

```python
json.dumps(embedding)
```

后续检索时再用：

```python
json.loads(chunk.embedding)
```

转回 Python 数组。

流程：

```text
存数据库：list[float] -> JSON 字符串
读出来检索：JSON 字符串 -> list[float]
```

### `sorted(KNOWLEDGE_BASE_DIR.glob("*.md"))` 是什么？

`KNOWLEDGE_BASE_DIR.glob("*.md")` 会找出知识库目录下所有 `.md` 文件。

`sorted(...)` 会把这些文件路径排序，保证每次入库顺序稳定。

如果不排序，文件系统返回顺序可能不固定；排序后执行结果更可预测。

### `ReflectionReference` 是什么，为什么重新入库时要删除？

`ReflectionReference` 表示某条复盘记录引用了哪些知识库 chunk。

它保存：

```text
某条复盘记录
引用了哪个知识 chunk
来源文件
标题
相关度
展示摘要
```

重新入库时会删除旧的 `KnowledgeChunk`，再生成新的 chunk。

旧的 `ReflectionReference` 里保存的是旧 chunk 的 id。重新入库后，这些 id 可能已经不存在，或者指向不同资料。

所以当前第一版策略是：

```text
重新入库知识库
-> 清空旧引用
-> 清空旧 chunk
-> 重新生成 chunk 和 embedding
```

这是简单、安全的 MVP 做法。

### 为什么 ingestion 里的 `session` 不需要 `refresh`？

`refresh` 常用于插入一条记录后，马上需要拿数据库生成的字段，例如 `id` 或默认时间。

创建复盘记录时需要：

```python
session.commit()
session.refresh(record)
```

因为后面要用 `record.id`。

但 ingestion 里只是批量写入 `KnowledgeChunk`，后面没有马上使用这些对象的数据库生成字段。

所以最后：

```python
session.commit()
```

即可，不需要 `refresh`。

### `asyncio.run` 是做什么的？

`ingest_knowledge_base` 是异步函数：

```python
async def ingest_knowledge_base()
```

普通同步代码不能直接 `await`。

所以命令行入口使用：

```python
asyncio.run(ingest_knowledge_base())
```

意思是：

```text
启动一个事件循环
运行这个异步函数
等待它执行完成
返回结果
```

这里主要是为了能在脚本里调用：

```python
await generate_embedding(...)
```

### coroutine 是什么？

`coroutine` 中文一般叫“协程”。

在 Python 里，调用一个 `async def` 函数时，它不会立刻执行函数体，而是先返回一个 coroutine 对象。

例如：

```python
async def hello():
    print("hello")
```

如果直接调用：

```python
hello()
```

它不会打印 `hello`，而是返回一个 coroutine。

要真正执行它，需要：

```python
await hello()
```

或者在同步入口里使用：

```python
asyncio.run(hello())
```

可以简单理解为：

```text
coroutine = 一个待执行的异步任务
```

异步函数里经常有等待操作，例如网络请求：

```python
await generate_embedding(...)
```

等待网络返回时，Python 可以把执行权让出去，不阻塞整个事件循环。

### `if __name__ == "__main__"` 是什么？

这段代码表示：当前模块被当作程序入口运行时，才执行 `main()`。

```python
if __name__ == "__main__":
    main()
```

当执行：

```bash
python -m app.rag.ingestion
```

这个模块会作为入口运行，`__name__` 会变成 `"__main__"`，于是执行 `main()`。

如果别的文件只是导入它：

```python
from app.rag.ingestion import ingest_knowledge_base
```

此时不会自动执行 `main()`。

作用：

```text
直接运行这个文件/模块时，执行 main
被别人 import 时，不自动执行 main
```

## `models.py`

### 怎么看出主键是自增的？

代码：

```python
id: int | None = Field(default=None, primary_key=True)
```

含义：

```text
id 是主键
创建对象时默认不给 id
数据库插入时由数据库生成 id
```

在 SQLite 里，`INTEGER PRIMARY KEY` 通常会自动使用自增 rowid 机制。

所以插入数据库时，`id=None` 会由数据库生成类似：

```text
1, 2, 3, 4...
```

更准确地说，代码里没有显式写 `autoincrement=True`，但 SQLModel + SQLite 对这种整型主键会默认让数据库生成 ID。

### `foreign_key` 是什么意思？

`foreign_key` 是外键。

它表示当前表的某个字段，引用另一张表的主键。

例如：

```python
reflection_id: int = Field(index=True, foreign_key="reflection_records.id")
```

意思是：

```text
reflection_references.reflection_id
引用
reflection_records.id
```

也就是这条引用记录属于哪一条复盘记录。

另一个：

```python
knowledge_chunk_id: int = Field(index=True, foreign_key="knowledge_chunks.id")
```

意思是这条引用记录指向哪个知识片段。

外键的作用是建立表之间的关系。

### `top-k` 是什么意思？

`top-k` 是检索里常见说法，意思是：

```text
按相关度排序后，取前 k 个结果
```

比如：

```text
top-k = 3
```

就是取最相关的 3 条知识片段。

流程：

```text
用户输入
-> 和所有知识 chunk 计算相似度
-> 按 score 从高到低排序
-> 取前 3 个
```

这些 chunk 会被注入 Prompt，让模型参考它们生成回答。

## `retrieval.py`

### `retrieval.py` 的一句话总结

`retrieval.py` 负责从知识库里找出和当前用户复盘最相关的几个 chunk，并把它们整理成 LLM 可以参考的上下文。

### `scored_chunks.sort(key=lambda item: item.score, reverse=True)` 是什么？

这句是给列表排序。

```python
scored_chunks.sort(...)
```

表示原地排序 `scored_chunks`。

```python
key=lambda item: item.score
```

表示排序时按每个元素的 `score` 字段排序。

`lambda item: item.score` 可以理解成一个临时小函数：

```python
def get_score(item):
    return item.score
```

```python
reverse=True
```

表示从大到小排序。

整体意思：

```text
把 scored_chunks 按 score 从高到低排序
```

### 为什么要判断 `len(left) != len(right)`？

余弦相似度要求两个向量维度相同。

例如：

```python
left = [0.1, 0.2, 0.3]
right = [0.4, 0.5]
```

一个是 3 维，一个是 2 维，不能一一对应计算。

正常情况下 embedding 都是同一维度，但为了防止脏数据、配置变化、旧数据残留，需要做保护。

### `cosine_similarity` 现阶段需要深究数学公式吗？

暂时不需要。

现阶段只需要理解：

```text
它用来衡量两个向量方向有多接近
结果越大，文本语义越相似
当前项目用它给 chunk 排序
```

公式细节后续有需要再学。

### `zip` 是做什么的？

`zip(left, right)` 会把两个列表按位置配对。

例如：

```python
left = [1, 2, 3]
right = [4, 5, 6]
```

会得到：

```python
(1, 4), (2, 5), (3, 6)
```

所以：

```python
sum(a * b for a, b in zip(left, right))
```

就是：

```text
1*4 + 2*5 + 3*6
```

这是向量点积。

### `sqrt` 是开方吗？

是。

```python
math.sqrt(9)
```

结果是：

```python
3
```

这里用于计算向量长度。

### `enumerate` 是什么？

`enumerate` 会在遍历列表时，同时给出索引和值。

例如：

```python
items = ["a", "b", "c"]
for index, item in enumerate(items, start=1):
    print(index, item)
```

输出：

```text
1 a
2 b
3 c
```

当前项目用它生成：

```text
[资料 1]
[资料 2]
[资料 3]
```

### `:.4f` 是什么？

代码：

```python
f"相关度：{item.score:.4f}"
```

`.4f` 表示：

```text
用浮点数格式展示
保留 4 位小数
```

例如：

```python
score = 0.593912345
f"{score:.4f}"
```

结果：

```text
0.5939
```

这样相关度显示更整齐，不会输出一长串小数。

## `prompts.py` / `llm_client.py`

### 为什么写 `build_reflection_user_prompt(payload, retrieved_context=retrieved_context)`？

也可以直接按位置传第二个参数：

```python
build_reflection_user_prompt(payload, retrieved_context)
```

但当前代码选择关键字传参：

```python
build_reflection_user_prompt(payload, retrieved_context=retrieved_context)
```

原因：

```text
别人一眼能看出这个值传给 retrieved_context
以后函数参数顺序变化时不容易传错
和其他带关键字参数的调用风格一致
```

这不是语法必须，而是为了可读性和稳定性。

### `type(exc).__name__` 是什么意思？

`type(exc).__name__` 用于拿到异常对象的类型名称。

例如：

```python
try:
    ...
except httpx.HTTPError as exc:
    print(type(exc).__name__)
```

如果异常是超时，可能得到：

```text
ReadTimeout
```

如果是连接失败，可能得到：

```text
ConnectError
```

所以代码：

```python
detail=f"LLM API streaming request failed: {type(exc).__name__}."
```

可以让前端错误更具体，方便判断是超时、连接失败，还是上游断流。

它不会输出 API Key，只会输出异常类型名。

## `schemas.py` / Frontend Types / `ReflectionDetail.tsx`

### `default_factory=list` 是指新建一个数组吗？

是。

代码：

```python
references: list[KnowledgeReference] = Field(default_factory=list)
```

意思是：如果没有传 `references`，就自动创建一个新的空列表：

```python
[]
```

为什么不用：

```python
references: list[KnowledgeReference] = []
```

因为列表是可变对象。`default_factory=list` 可以保证每个对象都有自己的新列表，避免多个对象共享同一个默认数组。

### 前端的 `number` 可以表示浮点数吗？

可以。

TypeScript / JavaScript 里没有单独的 `int` 和 `float` 类型，统一都是：

```ts
number
```

所以：

```ts
score: number
```

可以表示：

```ts
1
0.5939
-2.5
```

Python 里的 `float` 传到前端后就是 TypeScript 里的 `number`。

### `toFixed(4)` 是保留四位小数吗？

是。

```ts
reference.score.toFixed(4)
```

会把数字格式化成保留 4 位小数的字符串。

例如：

```ts
const score = 0.5939123;
score.toFixed(4);
```

结果是：

```text
"0.5939"
```

注意：`toFixed` 返回值是字符串，不是 number。

## 阶段 6 总流程复盘

阶段 6 的总流程分成两条线：离线入库和在线生成。

### 离线入库流程

这一步不是用户每次提交时做，而是准备好知识库资料后手动执行：

```bash
python -m app.rag.ingestion
```

流程：

```text
backend/knowledge_base/*.md
-> chunking.py 切成 chunk
-> embeddings.py 调阿里百炼生成 embedding
-> ingestion.py 写入 knowledge_chunks 表
```

对应文件：

```text
backend/knowledge_base/
存本地 Markdown 资料，资料正文不提交 Git

chunking.py
把 Markdown 切成适合向量化的小文本片段

embeddings.py
把每个 chunk 文本发给阿里百炼，生成 list[float] 向量

ingestion.py
把 source / title / content / embedding 保存到 SQLite

models.py
KnowledgeChunk 表定义了知识库 chunk 怎么存
```

离线入库完成后，数据库里有：

```text
knowledge_chunks
```

这张表就是后续 RAG 检索的资料库。

### 在线生成流程

这是用户在页面提交复盘时发生的。

流程：

```text
用户提交复盘表单
-> page.tsx 调 streamCreateReflection
-> api.ts 请求 POST /api/reflections/stream
-> reflections.py 收到 payload
-> retrieval.py 构造 retrieval query
-> embeddings.py 生成 query embedding
-> retrieval.py 读取 knowledge_chunks
-> retrieval.py 计算 cosine similarity
-> retrieval.py 排序取 top-k
-> retrieval.py format_chunks_for_prompt
-> prompts.py 把参考资料拼进 Prompt
-> llm_client.py 调 LLM 流式生成
-> reflections.py 一边 yield delta 给前端
-> reflections.py 一边收集完整 ai_report
-> 生成完成后保存 ReflectionRecord
-> 保存 ReflectionReference
-> 返回 done + record_id
-> page.tsx 根据 record_id 拉取详情
-> build_reflection_detail 查询 references
-> ReflectionDetail.tsx 展示 AI 报告和参考资料
```

### 三张核心表

```text
reflection_records
存用户复盘和 AI 报告

knowledge_chunks
存知识库 chunk 和 embedding

reflection_references
存某次复盘引用了哪些知识 chunk
```

关系：

```text
一次复盘 ReflectionRecord
-> 引用多个 ReflectionReference
-> 每个引用指向一个 KnowledgeChunk
```

### RAG 和之前阶段的区别

阶段 5 是：

```text
用户输入 -> Prompt -> LLM -> 报告
```

阶段 6 是：

```text
用户输入
-> 检索知识库
-> 把相关资料放进 Prompt
-> LLM 基于用户输入 + 资料生成报告
```

RAG 的关键不是“模型更聪明了”，而是：

```text
模型回答前，后端先帮它找资料
```

### 当前阶段 6 MVP 边界

已经做了：

```text
内置 Markdown 知识库
chunking
阿里百炼 embedding
SQLite 存向量
余弦相似度检索
top-k
Prompt 注入资料
引用来源保存
前端展示参考资料
```

暂时没做：

```text
文件上传
PDF/Word 解析
Reranker
向量数据库
自动评测
复杂安全防护
多知识库管理
```

一句话总结：

```text
阶段 6 让项目从“普通 LLM 复盘助手”升级成“能先检索知识库、再基于资料生成复盘报告的 RAG 应用”。
```
