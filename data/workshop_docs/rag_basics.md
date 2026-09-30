# RAG Fundamentals

Retrieval-Augmented Generation (RAG) combines search and generation. The system first retrieves relevant passages from a knowledge base, then uses a language model to answer a user question using that evidence.

A typical RAG pipeline includes these stages:

1. Document ingestion: text is loaded from files or web sources.
2. Chunking: the content is split into smaller sections so the retrieval step stays precise.
3. Embedding: each chunk is converted into a numeric vector using a sentence embedding model.
4. Retrieval: the user query is embedded and matched against stored vectors.
5. Generation: the language model produces a final answer grounded in the retrieved context.

For local workshop use, keep the document store small and relevant. This makes retrieval faster and easier to explain.
