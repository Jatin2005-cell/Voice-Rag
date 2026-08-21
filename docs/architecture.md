# VoiceRAG: System Architecture & Orchestration Harness

> **Tagline:** Ask. Retrieve. Verify.  
> **Target Latency:** &lt; 200 ms (RAG Pipeline)

---

## High-Level Architecture

VoiceRAG is an end-to-end Voice-Enabled Retrieval-Augmented Generation (RAG) system built for low-latency Indic information retrieval over the official **ai4bharat/MSMARCO-XI** dataset.

```
+-----------------------------------------------------------------------------------+
|                               USER VOICE / TEXT INPUT                             |
+-----------------------------------------------------------------------------------+
                                       |
                                       v
                     +-----------------------------------+
                     |      Speech-To-Text Provider      |
                     |  (Sarvam AI Saaras / ElevenLabs)  |
                     +-----------------------------------+
                                       |
                                       v
                     +-----------------------------------+
                     |      Query Guardrail Engine       |
                     | (Empty / Injection / Safety Check)|
                     +-----------------------------------+
                                       |
                                       v
                     +-----------------------------------+
                     |    Multilingual Embedding Model   |
                     | (paraphrase-multilingual-MiniLM)  |
                     +-----------------------------------+
                                       |
                                       v
                     +-----------------------------------+
                     |   FastDenseVectorStore (In-Mem)   |
                     |   (Normalized Cosine Dot Product) |
                     +-----------------------------------+
                                       |
                                       v
                     +-----------------------------------+
                     |    Relevance Cutoff Guardrail     |
                     |  (Threshold: 0.35 -> Abstention)  |
                     +-----------------------------------+
                                       |
                                       v
                     +-----------------------------------+
                     |      Grounded LLM Generation      |
                     |  (Groq Llama-3.1-8b-instant /     |
                     |   Fast Deterministic Fallback)    |
                     +-----------------------------------+
                                       |
                                       v
                     +-----------------------------------+
                     |  Grounding & Faithfulness Check   |
                     |  (Token overlap & claim verify)   |
                     +-----------------------------------+
                                       |
                                       v
                     +-----------------------------------+
                     |     Structured Response & UI      |
                     | (Answer + Badges + Latency Trace) |
                     +-----------------------------------+
```

---

## Orchestrator Harness (`backend/app/services/orchestrator.py`)

The pipeline runs inside a robust execution harness rather than raw unconstrained model calls:

1. **Structured Input / Output Validation**: Typed Pydantic schemas enforce format integrity.
2. **Error Recovery & Retries**: Automated fallback from cloud API to high-speed deterministic extraction if upstream LLM times out or rate limits.
3. **Microsecond Stage Timers**: Dynamic recording of `embedding_ms`, `retrieval_ms`, `context_building_ms`, `generation_ms`, `grounding_ms`, `total_rag_ms`, `stt_ms`, and `end_to_end_ms`.
4. **Decoupled STT & RAG**: Clear attribution preventing cloud STT network fluctuations from masking sub-200ms RAG performance.
