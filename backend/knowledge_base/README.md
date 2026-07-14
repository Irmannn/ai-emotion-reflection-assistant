# Local Knowledge Base

Place local Markdown knowledge-base files in this directory before running the RAG ingestion command.

Markdown source files in this directory are ignored by Git because they may contain private or licensed content.

Example:

```text
backend/knowledge_base/example.md
```

Then run:

```bash
cd backend
source .venv/bin/activate
python -m app.rag.ingestion
```
