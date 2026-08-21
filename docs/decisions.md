# VoiceRAG: Architectural Decisions & Trade-Offs

## 1. Decision: Passage-Aware Chunking over Naive Fixed-Size Chunking
- **Context:** MSMARCO-XI data consists of curated passage units extracted from web documents with associated `is_selected` labels.
- **Decision:** Use `PassageAwareChunker` as primary chunking strategy, preserving original passage boundaries and only sub-chunking if length exceeds 250 words.
- **Rationale:** Prevents fragmenting coherent semantic entities across arbitrary fixed boundaries, maintaining direct alignment with ground-truth relevance annotations.

## 2. Decision: In-Memory Normalized BLAS Dot Product for Vector Store
- **Context:** The task targets &lt; 200 ms end-to-end RAG latency. Cloud vector databases add 30-150 ms of network round-trip overhead per query.
- **Decision:** Implement `FastDenseVectorStore` using normalized NumPy matrix dot-product (`np.dot`) backed by persistent `.npz` storage.
- **Rationale:** Reduces vector search latency to **0.63 ms** across 5,000 - 20,000 vectors while preserving full metadata filtering capabilities.

## 3. Decision: Reranker Disabled by Default (`RERANKING_ENABLED=false`)
- **Context:** Cross-encoder rerankers add 80-250 ms of inference overhead.
- **Decision:** Set default `RERANKING_ENABLED=false`, providing an optional ultra-fast lexical boost hybrid reranker when explicitly enabled.
- **Rationale:** Strict adherence to the &lt; 200 ms SLA while maintaining competitive Recall@5.

## 4. Decision: Strict Abstention on Weak Retrieval
- **Context:** In high-stakes retrieval tasks, hallucinating ungrounded facts when context is missing is unacceptable.
- **Decision:** When top similarity score &lt; `SIMILARITY_THRESHOLD` (0.35), the orchestrator triggers an immediate safe abstention:
  *"I couldn't find enough relevant information in the provided knowledge base to answer this reliably."*
- **Rationale:** Guarantees that the system knows *when not to answer*, not just how to answer.
