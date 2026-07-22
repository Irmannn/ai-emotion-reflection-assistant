from typing import Any

from langchain_core.callbacks.manager import AsyncCallbackManagerForRetrieverRun, CallbackManagerForRetrieverRun
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from pydantic import ConfigDict, Field
from sqlmodel import Session

from app.rag.retrieval import DEFAULT_TOP_K, RetrievedChunk, build_retrieval_query, retrieve_chunks_for_query
from app.schemas import ReflectionCreate


class KnowledgeBaseRetriever(BaseRetriever):
    """Expose the existing embedding search through LangChain's Retriever interface."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    session: Any = Field(exclude=True)
    top_k: int = DEFAULT_TOP_K
    latest_chunks: list[RetrievedChunk] = Field(default_factory=list, exclude=True)

    def _get_relevant_documents(
        self, query: str, *, run_manager: CallbackManagerForRetrieverRun
    ) -> list[Document]:
        raise NotImplementedError("KnowledgeBaseRetriever uses async embedding calls; use ainvoke().")

    async def _aget_relevant_documents(
        self, query: str, *, run_manager: AsyncCallbackManagerForRetrieverRun
    ) -> list[Document]:
        self.latest_chunks = await retrieve_chunks_for_query(query, self.session, self.top_k)
        return [_to_document(item) for item in self.latest_chunks]


async def retrieve_reflection_documents(payload: ReflectionCreate, session: Session) -> tuple[list[Document], list[RetrievedChunk]]:
    retriever = KnowledgeBaseRetriever(session=session)
    documents = await retriever.ainvoke(build_retrieval_query(payload))
    return documents, retriever.latest_chunks


def _to_document(item: RetrievedChunk) -> Document:
    return Document(
        page_content=item.chunk.content,
        metadata={
            "source": item.chunk.source,
            "title": item.chunk.title,
            "score": item.score,
            "knowledge_chunk_id": item.chunk.id,
        },
    )
