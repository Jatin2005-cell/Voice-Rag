import React, { useState, useEffect } from 'react';
import { Cpu, Database, ArrowRight, ShieldCheck, Zap, Layers, Sparkles, Mic, FileText, CheckCircle2 } from 'lucide-react';
import { fetchSystemInfo } from '../services/api';

export default function SystemPage() {
  const [sysInfo, setSysInfo] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchSystemInfo()
      .then(data => setSysInfo(data))
      .catch(err => console.warn('System info load error:', err))
      .finally(() => setLoading(false));
  }, []);

  const pipelineSteps = [
    { step: '1', title: 'Voice Input', desc: 'Audio Stream / Mic Capture', icon: Mic, color: 'text-rose-400 bg-rose-500/10 border-rose-500/20' },
    { step: '2', title: 'STT Provider', desc: 'Sarvam AI / ElevenLabs', icon: Sparkles, color: 'text-amber-400 bg-amber-500/10 border-amber-500/20' },
    { step: '3', title: 'Guardrails', desc: 'Empty & Injection Safety Check', icon: ShieldCheck, color: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20' },
    { step: '4', title: 'Dense Embedding', desc: 'Multilingual MiniLM (384-d)', icon: Cpu, color: 'text-cyan-400 bg-cyan-500/10 border-cyan-500/20' },
    { step: '5', title: 'Vector Search', desc: 'Normalized Cosine Dot Product', icon: Database, color: 'text-blue-400 bg-blue-500/10 border-blue-500/20' },
    { step: '6', title: 'Relevance Filter', desc: 'Score >= 0.35 Cutoff', icon: Layers, color: 'text-indigo-400 bg-indigo-500/10 border-indigo-500/20' },
    { step: '7', title: 'Context Harness', desc: 'Strict Grounding System Prompt', icon: FileText, color: 'text-purple-400 bg-purple-500/10 border-purple-500/20' },
    { step: '8', title: 'LLM Generation', desc: 'Groq Llama-3.1-8b-instant', icon: Sparkles, color: 'text-violet-400 bg-violet-500/10 border-violet-500/20' },
    { step: '9', title: 'Grounding Verify', desc: 'Faithfulness & Hallucination Check', icon: ShieldCheck, color: 'text-teal-400 bg-teal-500/10 border-teal-500/20' },
    { step: '10', title: 'Verified Answer', desc: 'Structured JSON & Latency Profile', icon: CheckCircle2, color: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20' }
  ];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      
      {/* Header */}
      <div className="mb-8 pb-6 border-b border-white/10">
        <div className="flex items-center gap-2 text-cyan-400 text-xs font-bold uppercase tracking-wider mb-1">
          <Cpu className="w-4 h-4" />
          <span>System Architecture &amp; Specification</span>
        </div>
        <h1 className="text-2xl sm:text-4xl font-extrabold text-white tracking-tight">
          VoiceRAG Pipeline &amp; Harness Architecture
        </h1>
        <p className="text-xs sm:text-sm text-slate-400 mt-1">
          Complete end-to-end architecture engineered for sub-200ms latency, high Indic retrieval fidelity, and strict grounding.
        </p>
      </div>

      {/* Visual Pipeline Diagram */}
      <div className="p-6 rounded-2xl bg-slate-900/80 border border-white/10 mb-8">
        <h3 className="text-sm font-bold text-slate-200 uppercase tracking-wider mb-4 flex items-center gap-2">
          <Zap className="w-4 h-4 text-cyan-400" />
          End-to-End Orchestrated Pipeline Flow
        </h3>

        <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
          {pipelineSteps.map((item, idx) => {
            const Icon = item.icon;
            return (
              <div
                key={idx}
                className="p-3.5 rounded-xl bg-slate-950/70 border border-white/5 flex flex-col justify-between relative group hover:border-cyan-500/30 transition-all"
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="text-[10px] font-mono font-bold text-slate-500">Step {item.step}</span>
                  <div className={`p-1.5 rounded-lg border ${item.color}`}>
                    <Icon className="w-3.5 h-3.5" />
                  </div>
                </div>
                <div>
                  <h4 className="text-xs font-bold text-slate-100">{item.title}</h4>
                  <p className="text-[11px] text-slate-400 mt-0.5 leading-snug">{item.desc}</p>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Active System Configuration */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        
        {/* Dataset & Retrieval Config */}
        <div className="p-6 rounded-2xl bg-slate-900/80 border border-white/10 space-y-3 text-xs">
          <h3 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2 mb-3">
            <Database className="w-4 h-4 text-blue-400" />
            Dataset &amp; Retrieval Engine
          </h3>
          
          <div className="flex justify-between py-1.5 border-b border-white/5 font-mono">
            <span className="text-slate-400">Official Dataset:</span>
            <span className="text-cyan-300 font-bold">{sysInfo?.dataset_name || 'ai4bharat/MSMARCO-XI'}</span>
          </div>

          <div className="flex justify-between py-1.5 border-b border-white/5 font-mono">
            <span className="text-slate-400">Active Language:</span>
            <span className="text-slate-200 font-bold">{sysInfo?.dataset_language || 'hi'} (Hindi)</span>
          </div>

          <div className="flex justify-between py-1.5 border-b border-white/5 font-mono">
            <span className="text-slate-400">Chunking Strategy:</span>
            <span className="text-emerald-400 font-bold">{sysInfo?.chunking_strategy || 'passage_aware'}</span>
          </div>

          <div className="flex justify-between py-1.5 border-b border-white/5 font-mono">
            <span className="text-slate-400">Vector Store:</span>
            <span className="text-slate-200 font-bold">{sysInfo?.vector_store || 'FastDenseVectorStore (In-Memory Cosine)'}</span>
          </div>

          <div className="flex justify-between py-1.5 border-b border-white/5 font-mono">
            <span className="text-slate-400">Top-K Retrieval Candidates:</span>
            <span className="text-cyan-300 font-bold">{sysInfo?.top_k || 5}</span>
          </div>

          <div className="flex justify-between py-1.5 font-mono">
            <span className="text-slate-400">Similarity Cutoff (Threshold):</span>
            <span className="text-amber-300 font-bold">{sysInfo?.similarity_threshold || 0.35}</span>
          </div>
        </div>

        {/* Models & Performance SLA */}
        <div className="p-6 rounded-2xl bg-slate-900/80 border border-white/10 space-y-3 text-xs">
          <h3 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2 mb-3">
            <Cpu className="w-4 h-4 text-purple-400" />
            Models &amp; Latency SLA
          </h3>

          <div className="flex justify-between py-1.5 border-b border-white/5 font-mono">
            <span className="text-slate-400">Embedding Model:</span>
            <span className="text-cyan-300 font-bold">paraphrase-multilingual-MiniLM-L12-v2</span>
          </div>

          <div className="flex justify-between py-1.5 border-b border-white/5 font-mono">
            <span className="text-slate-400">LLM Generation Provider:</span>
            <span className="text-purple-300 font-bold">Groq (llama-3.1-8b-instant) / Gemini Flash</span>
          </div>

          <div className="flex justify-between py-1.5 border-b border-white/5 font-mono">
            <span className="text-slate-400">Speech-to-Text Provider:</span>
            <span className="text-rose-300 font-bold">{sysInfo?.stt_provider || 'Sarvam AI (Saaras Indic)'}</span>
          </div>

          <div className="flex justify-between py-1.5 border-b border-white/5 font-mono">
            <span className="text-slate-400">RAG Latency Target SLA:</span>
            <span className="text-emerald-400 font-bold">&lt; 200.0 ms</span>
          </div>

          <div className="flex justify-between py-1.5 border-b border-white/5 font-mono">
            <span className="text-slate-400">Guardrails Engine:</span>
            <span className="text-slate-200 font-bold">Active (Abstention on low confidence)</span>
          </div>

          <div className="flex justify-between py-1.5 font-mono">
            <span className="text-slate-400">Grounding Verifier:</span>
            <span className="text-teal-300 font-bold">Active (Token overlap &amp; claim check)</span>
          </div>
        </div>

      </div>

    </div>
  );
}
