from __future__ import annotations

import json
import math
import re
from collections import Counter
from typing import Any, List

import numpy as np

from app.config import INDEX_DIR


class VectorStore:
    def __init__(self):
        self.index_dir = INDEX_DIR
        self.index_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_path = self.index_dir / "metadata.json"
        self.documents: List[dict[str, Any]] = []
        self.term_index: dict[str, int] = {}
        self.idf: dict[str, float] = {}
        self.doc_vectors: List[np.ndarray] = []
        self.doc_norms: List[float] = []
        self._load_or_initialize()

    def _load_or_initialize(self) -> None:
        if self.metadata_path.exists():
            with self.metadata_path.open("r", encoding="utf-8") as file:
                self.documents = json.load(file)
            self._rebuild_index()
            return

        self.documents = []
        self.term_index = {}
        self.idf = {}
        self.doc_vectors = []
        self.doc_norms = []

    def _tokenize(self, text: str) -> List[str]:
        return re.findall(r"\b[\w'-]+\b", text.lower())

    def _save(self) -> None:
        with self.metadata_path.open("w", encoding="utf-8") as file:
            json.dump(self.documents, file, ensure_ascii=False, indent=2)

    def _rebuild_index(self) -> None:
        if not self.documents:
            self.term_index = {}
            self.idf = {}
            self.doc_vectors = []
            self.doc_norms = []
            return

        doc_tokens = [self._tokenize(item["text"]) for item in self.documents]
        doc_freq: Counter[str] = Counter()

        for tokens in doc_tokens:
            unique_tokens = set(tokens)
            for token in unique_tokens:
                doc_freq[token] += 1

        vocabulary = sorted(doc_freq.keys())
        self.term_index = {token: index for index, token in enumerate(vocabulary)}
        doc_count = len(doc_tokens)
        self.idf = {
            token: math.log((1 + doc_count) / (1 + doc_freq[token])) + 1.0
            for token in vocabulary
        }

        vectors: List[np.ndarray] = []
        norms: List[float] = []
        for tokens in doc_tokens:
            vector = np.zeros(len(vocabulary), dtype=np.float32)
            counts = Counter(tokens)
            for token, count in counts.items():
                if token in self.term_index:
                    vector[self.term_index[token]] = count * self.idf[token]
            norm = float(np.linalg.norm(vector))
            vectors.append(vector)
            norms.append(norm)

        self.doc_vectors = vectors
        self.doc_norms = norms

    def add_documents(self, documents: List[dict[str, Any]]) -> int:
        if not documents:
            return 0

        self.documents.extend(documents)
        self._rebuild_index()
        self._save()
        return len(documents)

    def search(self, query: str, top_k: int = 4) -> List[dict[str, Any]]:
        if not self.documents or not self.doc_vectors:
            return []

        query_tokens = self._tokenize(query)
        if not query_tokens:
            return []

        query_counts = Counter(query_tokens)
        query_vector = np.zeros(len(self.term_index), dtype=np.float32)
        for token, count in query_counts.items():
            if token in self.term_index:
                query_vector[self.term_index[token]] = count * self.idf[token]

        query_norm = float(np.linalg.norm(query_vector))
        if query_norm == 0:
            return []

        scores: List[tuple[float, int]] = []
        for index, document_vector in enumerate(self.doc_vectors):
            doc_norm = self.doc_norms[index]
            if doc_norm == 0:
                continue
            score = float(np.dot(query_vector, document_vector) / (query_norm * doc_norm))
            if score > 0:
                scores.append((score, index))

        scores.sort(key=lambda item: item[0], reverse=True)
        matches: List[dict[str, Any]] = []
        for score, index in scores[:top_k]:
            document = self.documents[index]
            matches.append(
                {
                    "score": score,
                    "source": document.get("source", "unknown"),
                    "text": document.get("text", ""),
                }
            )

        return matches

    def reset(self) -> None:
        self.documents = []
        self.term_index = {}
        self.idf = {}
        self.doc_vectors = []
        self.doc_norms = []
        if self.metadata_path.exists():
            self.metadata_path.unlink()
