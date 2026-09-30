# Local LLMs and Offline AI

A local LLM runs directly on the user device or a local server. For workshops, this is often desirable because it improves privacy, reduces dependency on cloud APIs, and simplifies demos.

Common local deployment patterns include:

- Ollama for running local models such as Llama 3 or Mistral.
- Sentence-transformers for local embeddings.
- FAISS for fast vector storage and similarity search.

The retrieval stage and generation stage can operate completely on local infrastructure. However, the model size, RAM capacity, and CPU or GPU speed affect the quality and latency of responses.

In a workshop setting, it is usually best to keep the system transparent: show the retrieved sources, explain chunking, and state that the answer is grounded in retrieved context rather than raw memory alone.
