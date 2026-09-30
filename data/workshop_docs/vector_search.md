# Vector Search and Embeddings

Vector search is a method of retrieving semantically similar content by comparing embeddings instead of exact keywords. A sentence encoder transforms text into a high-dimensional vector space where related ideas are near each other.

This is useful when a query uses different terms from the source document. For example, the words "retrieval" and "search" may not be identical, but their embeddings can still be close in meaning.

The most common similarity metric is cosine similarity, which measures the angle between vectors. A higher score suggests stronger semantic similarity.

When building a local RAG workflow, it is helpful to store metadata such as file names, chunk identifiers, and page numbers alongside each vector. This makes the answer easier to trace back to source documents.
