from __future__ import annotations

from pathlib import Path
from typing import Iterable, List

from pypdf import PdfReader

from app.config import CHUNK_OVERLAP, CHUNK_SIZE


def clean_text(text: str) -> str:
    return "\n".join(line.strip() for line in text.splitlines()).strip()


def read_text_file(path: Path) -> str:
    if path.suffix.lower() == ".pdf":
        reader = PdfReader(str(path))
        pages = []
        for page in reader.pages:
            text = page.extract_text() or ""
            pages.append(text)
        return "\n".join(pages)

    return path.read_text(encoding="utf-8", errors="ignore")


def split_text_into_chunks(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
    if not text or not text.strip():
        return []

    words = text.split()
    if len(words) <= chunk_size:
        return [clean_text(text)]

    chunks: List[str] = []
    step = chunk_size - overlap

    for start in range(0, len(words), step):
        end = min(start + chunk_size, len(words))
        chunk = " ".join(words[start:end])
        if chunk.strip():
            chunks.append(clean_text(chunk))

        if end >= len(words):
            break

    return chunks


def load_documents_from_directory(directory: Path) -> List[dict]:
    documents: List[dict] = []
    if not directory.exists():
        return documents

    for file_path in sorted(directory.iterdir()):
        if file_path.is_dir():
            continue
        if file_path.suffix.lower() not in {".txt", ".md", ".pdf"}:
            continue

        text = read_text_file(file_path)
        chunks = split_text_into_chunks(text)
        for index, chunk in enumerate(chunks):
            documents.append(
                {
                    "id": f"{file_path.stem}-{index}",
                    "source": file_path.name,
                    "text": chunk,
                }
            )

    return documents
