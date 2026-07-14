import json
import math
from dataclasses import dataclass

from sqlmodel import Session, select

from app.models import KnowledgeChunk
from app.rag.embeddings import generate_embedding
from app.schemas import ReflectionCreate


DEFAULT_TOP_K = 3


@dataclass(frozen=True)
class RetrievedChunk:
    chunk: KnowledgeChunk
    score: float


def build_retrieval_query(payload: ReflectionCreate) -> str:
    return "\n".join(
        [
            payload.event_text,
            "情绪标签：" + "、".join(payload.emotion_tags),
            f"情绪强度：{payload.emotion_intensity}",
            f"自动想法：{payload.automatic_thoughts}",
            f"身体反应：{payload.body_reaction}",
            f"分析方向：{payload.focus_area}",
        ]
    ).strip()


async def retrieve_relevant_chunks(payload: ReflectionCreate, session: Session, top_k: int = DEFAULT_TOP_K) -> list[RetrievedChunk]:
    chunks = session.exec(select(KnowledgeChunk)).all()
    if not chunks:
        return []

    query_embedding = await generate_embedding(build_retrieval_query(payload))
    scored_chunks: list[RetrievedChunk] = []

    for chunk in chunks:
        try:
            chunk_embedding = json.loads(chunk.embedding)
        except json.JSONDecodeError:
            continue

        score = cosine_similarity(query_embedding, chunk_embedding)
        scored_chunks.append(RetrievedChunk(chunk=chunk, score=score))

    scored_chunks.sort(key=lambda item: item.score, reverse=True)
    return scored_chunks[:top_k]


def cosine_similarity(left: list[float], right: list[float]) -> float:
    if not left or not right or len(left) != len(right):
        return 0.0

    dot_product = sum(a * b for a, b in zip(left, right))
    left_norm = math.sqrt(sum(value * value for value in left))
    right_norm = math.sqrt(sum(value * value for value in right))
    if left_norm == 0 or right_norm == 0:
        return 0.0

    return dot_product / (left_norm * right_norm)


def format_chunks_for_prompt(chunks: list[RetrievedChunk]) -> str:
    if not chunks:
        return "本次没有检索到可用的知识库资料。"

    sections: list[str] = []
    for index, item in enumerate(chunks, start=1):
        sections.append(
            "\n".join(
                [
                    f"[资料 {index}]",
                    f"标题：{item.chunk.title}",
                    f"来源：{item.chunk.source}",
                    f"相关度：{item.score:.4f}",
                    "内容：",
                    item.chunk.content,
                ]
            )
        )
    return "\n\n".join(sections)
