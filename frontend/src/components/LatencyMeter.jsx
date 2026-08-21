import React from 'react';
import { Zap, Clock, Cpu, Database, Sparkles, ShieldCheck } from 'lucide-react';

export default function LatencyMeter({ latency }) {
  if (!latency) return null;

  const {
    embedding_ms = 0,
    retrieval_ms = 0,
    context_building_ms = 0,
    generation_ms = 0,
    grounding_ms = 0,
    total_rag_ms = 0,
    stt_ms,
    end_to_end_ms
  } = latency;

  const target = 200;
  const isPassing = total_rag_ms <= target;

  const stages = [
    { label: 'Embedding', ms: embedding_ms, color: 'bg-cyan-400', icon: Cpu },
    { label: 'Vector Retrieval', ms: retrieval_ms, color: 'bg-blue-500', icon: Database },
    { label: 'Context', ms: context_building_ms, color: 'bg-indigo-400', icon: Clock },
    { label: 'Generation', ms: generation_ms, color: 'bg-purple-500', icon: Sparkles },
    { label: 'Grounding', ms: grounding_ms, color: 'bg-emerald-400', icon: ShieldCheck }
  ];

  return (
    <div className="w-full max-w-4xl mx-auto my-3 p-4 rounded-xl bg-slate-900/70 border border-white/10">
      <div className="flex flex-wrap items-center justify-between gap-2 mb-3">
        <div className="flex items-center gap-2">
          <Zap className="w-4 h-4 text-cyan-400 shrink-0" />
          <h4 className="text-xs font-bold uppercase tracking-wider text-slate-200">
            Real-Time Query Latency Profile
          </h4>
        </div>

        <div className="flex items-center gap-2 text-xs">
          <span className="text-slate-400">RAG Pipeline:</span>
          <span className="font-mono font-extrabold text-cyan-300">{total_rag_ms} ms</span>
          <span
            className={`px-2 py-0.5 rounded-full font-bold text-[10px] ${
              isPassing
                ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                : 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
            }`}
          >
            {isPassing ? 'TARGET PASS (< 200ms)' : 'OPTIMIZING'}
          </span>
        </div>
      </div>

      {/* Stacked Progress Bar */}
      <div className="w-full h-2 rounded-full bg-slate-800 flex overflow-hidden mb-3">
        {stages.map((stg, i) => {
          const widthPct = total_rag_ms > 0 ? Math.max(2, (stg.ms / total_rag_ms) * 100) : 20;
          return (
            <div
              key={i}
              style={{ width: `${widthPct}%` }}
              className={`${stg.color} h-full transition-all duration-300`}
              title={`${stg.label}: ${stg.ms} ms`}
            />
          );
        })}
      </div>

      {/* Stage Breakdown Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-5 gap-2 text-[11px] font-mono">
        {stages.map((stg, i) => (
          <div
            key={i}
            className="p-2 rounded-lg bg-slate-950/60 border border-white/5 flex flex-col justify-between"
          >
            <span className="text-slate-400 truncate">{stg.label}</span>
            <span className="font-bold text-slate-200 mt-1">{stg.ms} ms</span>
          </div>
        ))}
      </div>

      {/* Voice End-To-End Summary */}
      {stt_ms !== undefined && (
        <div className="mt-3 pt-2.5 border-t border-white/5 flex flex-wrap items-center justify-between gap-2 text-xs font-mono text-slate-400">
          <span>
            STT Transcription: <strong className="text-purple-300">{stt_ms} ms</strong>
          </span>
          <span>
            End-to-End Voice: <strong className="text-white">{end_to_end_ms} ms</strong>
          </span>
        </div>
      )}
    </div>
  );
}