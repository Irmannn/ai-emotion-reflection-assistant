import asyncio
import json
from pathlib import Path

from sqlmodel import Session, delete

from app.database import create_db_and_tables, engine
from app.models import KnowledgeChunk, ReflectionReference
from app.rag.chunking import chunk_markdown_file
from app.rag.embeddings import generate_embedding


KNOWLEDGE_BASE_DIR = Path(__file__).resolve().parents[2] / "knowledge_base"


async def ingest_knowledge_base() -> int:
    create_db_and_tables()
    markdown_files = sorted(KNOWLEDGE_BASE_DIR.glob("*.md"))
    markdown_files = [path for path in markdown_files if path.name != "README.md"]

    with Session(engine) as session:
        session.exec(delete(ReflectionReference))
        session.exec(delete(KnowledgeChunk))
        session.commit()

        count = 0
        for path in markdown_files:
            chunks = chunk_markdown_file(path)
            for chunk in chunks:
                embedding = await generate_embedding(chunk.content)
                session.add(
                    KnowledgeChunk(
                        source=chunk.source,
                        title=chunk.title,
                        content=chunk.content,
                        embedding=json.dumps(embedding),
                    )
                )
                count += 1
                print(f"ingested chunk {count}: {chunk.source} / {chunk.title}")
        session.commit()

    return count


def main() -> None:
    count = asyncio.run(ingest_knowledge_base())
    print(f"Knowledge ingestion completed. chunks={count}")


if __name__ == "__main__":
    main()
