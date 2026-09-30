# Local Workshop RAG App

This project is a beginner-friendly, technically correct local Retrieval-Augmented Generation (RAG) application designed for a college technical workshop.

## Features

- Local document ingestion from `.txt`, `.md`, and `.pdf` files
- Chunk-based indexing with sentence embeddings
- Fast vector retrieval using FAISS
- Optional local LLM generation through Ollama
- Simple FastAPI backend and browser-based frontend
- Clear workshop-ready UI for demos and learning

## Project structure

- `app/` - Python backend logic
- `static/` - browser interface
- `data/workshop_docs/` - sample workshop documents
- `requirements.txt` - Python dependencies

## Quick start

1. Create a virtual environment with Python 3.12.
2. Install dependencies.
3. Start the FastAPI app.
4. Open the browser at `http://localhost:8000`.

## Setup commands

```bash
py -3.12 -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Optional local LLM integration

The app can call Ollama if it is running locally. By default it expects:

- `http://localhost:11434`
- model: `llama3.2:latest`

If Ollama is unavailable, the application still returns a grounded fallback answer based on the retrieved local passages.

## Workshop demo flow

1. Open the app in the browser.
2. Upload a document or use the default workshop notes.
3. Ask a question that requires context from the indexed materials.
4. Review the retrieved source snippets and the generated answer.

This demonstrates the core RAG workflow clearly and practically.
