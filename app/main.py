from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app.config import BASE_DIR, STATIC_DIR, UPLOAD_DIR, WORKSHOP_DOCS_DIR
from app.rag_service import RagService


class QueryRequest(BaseModel):
    question: str
    top_k: int = 4


@asynccontextmanager
async def lifespan(_: FastAPI):
    app.state.rag = RagService()
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    if WORKSHOP_DOCS_DIR.exists():
        indexed = app.state.rag.ingest_directory(WORKSHOP_DOCS_DIR)
        app.state.rag.indexed_count = indexed
    else:
        app.state.rag.indexed_count = 0

    yield


app = FastAPI(
    title="Local Workshop RAG Assistant",
    description="A beginner-friendly local retrieval-augmented generation application for workshop use.",
    version="1.0.0",
    lifespan=lifespan,
)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/")
def read_root() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/health")
def health() -> dict[str, object]:
    return {"status": "ok", "service": "local-rag-workshop"}


@app.get("/api/status")
def status() -> dict[str, object]:
    rag = app.state.rag
    return {
        "indexed_documents": getattr(rag, "indexed_count", 0),
        "knowledge_base": str(WORKSHOP_DOCS_DIR),
    }


@app.post("/api/query")
def query_documents(payload: QueryRequest) -> dict[str, object]:
    question = payload.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question must not be empty.")

    response = app.state.rag.ask(question, top_k=payload.top_k)
    return response


@app.post("/api/upload")
async def upload_document(file: UploadFile = File(...)) -> dict[str, object]:
    allowed_types = {"text/plain", "application/pdf", "text/markdown"}
    if file.content_type not in allowed_types and not file.filename.lower().endswith((".txt", ".md", ".pdf")):
        raise HTTPException(status_code=400, detail="Only .txt, .md, and .pdf files are supported.")

    file_path = UPLOAD_DIR / file.filename
    with file_path.open("wb") as buffer:
        while True:
            chunk = await file.read(1024 * 1024)
            if not chunk:
                break
            buffer.write(chunk)

    indexed = app.state.rag.ingest_file(file_path)
    return {
        "message": f"File uploaded and indexed successfully.",
        "filename": file.filename,
        "chunks_added": indexed,
    }


@app.post("/api/index")
def index_workshop_docs() -> dict[str, object]:
    if not WORKSHOP_DOCS_DIR.exists():
        raise HTTPException(status_code=404, detail="Workshop directory does not exist.")

    indexed = app.state.rag.ingest_directory(WORKSHOP_DOCS_DIR)
    app.state.rag.indexed_count = indexed
    return {"message": "Workshop materials indexed successfully.", "chunks_added": indexed}
