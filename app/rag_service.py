from __future__ import annotations

from pathlib import Path
from typing import Any

import httpx

from app.config import DEFAULT_TOP_K, OLLAMA_BASE_URL, OLLAMA_MODEL
from app.data_loader import load_documents_from_directory, read_text_file, split_text_into_chunks
from app.vector_store import VectorStore


class RagService:
    def __init__(self) -> None:
        self.vector_store = VectorStore()

    def ingest_directory(self, directory: str | Path) -> int:
        documents = load_documents_from_directory(Path(directory))
        if not documents:
            return 0
        return self.vector_store.add_documents(documents)

    def ingest_file(self, file_path: str | Path) -> int:
        file_path = Path(file_path)
        text = read_text_file(file_path)
        chunks = split_text_into_chunks(text)
        documents = [
            {"id": f"{file_path.stem}-{index}", "source": file_path.name, "text": chunk}
            for index, chunk in enumerate(chunks)
        ]
        return self.vector_store.add_documents(documents)

    def ask(self, question: str, top_k: int = DEFAULT_TOP_K) -> dict[str, Any]:
        matches = self.vector_store.search(question, top_k=top_k)
        if not matches:
            return {
                "answer": "I could not find any relevant workshop material in the local index yet. Please upload a document or add more notes.",
                "sources": [],
                "retrieved_chunks": 0,
            }

        context = "\n\n".join(
            f"[Source: {match['source']}]\n{match['text']}" for match in matches
        )

        answer = self._generate_answer(question, context, matches)
        return {
            "answer": answer,
            "sources": [
                {"source": match["source"], "score": round(match["score"], 4)} for match in matches
            ],
            "retrieved_chunks": len(matches),
        }

    def _generate_answer(self, question: str, context: str, matches: list[dict[str, Any]]) -> str:
        prompt = (
            "You are a helpful workshop instructor. Answer using only the context below. "
            "If the context does not contain the answer, say so clearly. "
            "Cite the source names in the response when relevant.\n\n"
            f"Question: {question}\n\nContext:\n{context}"
        )

        try:
            response = httpx.post(
                f"{OLLAMA_BASE_URL}/api/generate",
                json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False},
                timeout=120,
            )
            if response.status_code == 200:
                generated = response.json().get("response", "").strip()
                if generated:
                    return generated
        except Exception:
            pass

        context_summary = "\n".join(
            f"• {match['source']}: {match['text'][:180].strip()}..." for match in matches
        )

        return (
            "Based on the workshop materials, the most relevant information is:\n\n"
            f"{context_summary}\n\n"
            "In summary: the indexed content suggests that the answer should be derived from the retrieved passages above. "
            "For a fully polished response, run Ollama locally with the model configured in the application settings."
        )
