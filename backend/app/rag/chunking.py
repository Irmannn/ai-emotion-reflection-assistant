from dataclasses import dataclass
from pathlib import Path


MIN_CHUNK_LENGTH = 80
MAX_CHUNK_LENGTH = 800


@dataclass(frozen=True)
class TextChunk:
    source: str
    title: str
    content: str


def chunk_markdown_file(path: Path) -> list[TextChunk]:
    """Split one Markdown file into small chunks while preserving headings."""
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        return []

    return [
        TextChunk(
            source=path.name,
            title=path.stem,
            content=chunk_content,
        )
        for chunk_content in split_by_length(text)
    ]


def split_markdown_sections(text: str) -> list[tuple[str, str]]:
    sections: list[tuple[str, list[str]]] = []
    current_title = ""
    current_lines: list[str] = []

    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            if current_lines:
                sections.append((current_title, current_lines))
            current_title = stripped.lstrip("#").strip()
            current_lines = []
            continue
        current_lines.append(line)

    if current_lines:
        sections.append((current_title, current_lines))

    if not sections:
        return [("", text)]

    normalized_sections: list[tuple[str, str]] = []
    for title, lines in sections:
        body = "\n".join(lines).strip()
        content = f"{title}\n{body}".strip() if title else body
        if content:
            normalized_sections.append((title, content))

    if not normalized_sections:
        return [("", text)]

    return normalized_sections


def split_by_length(text: str) -> list[str]:
    paragraphs = [paragraph.strip() for paragraph in text.split("\n\n") if paragraph.strip()]
    chunks: list[str] = []
    current = ""

    for paragraph in paragraphs:
        if len(paragraph) > MAX_CHUNK_LENGTH:
            if current:
                chunks.append(current)
                current = ""
            chunks.extend(split_long_text(paragraph))
            continue

        candidate = f"{current}\n\n{paragraph}".strip() if current else paragraph
        if len(candidate) <= MAX_CHUNK_LENGTH:
            current = candidate
            continue

        if len(current) >= MIN_CHUNK_LENGTH:
            chunks.append(current)
            current = paragraph
        else:
            current = candidate

    if current:
        chunks.append(current)

    return chunks


def split_long_text(text: str) -> list[str]:
    chunks: list[str] = []
    for index in range(0, len(text), MAX_CHUNK_LENGTH):
        chunk = text[index : index + MAX_CHUNK_LENGTH].strip()
        if chunk:
            chunks.append(chunk)
    return chunks
