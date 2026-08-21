import React, { useState } from 'react';
import { Database, ChevronDown, ChevronUp, CheckCircle, Languages } from 'lucide-react';

export default function SourceCard({ sources }) {
  const [expandedIndex, setExpandedIndex] = useState(0);

  if (!sources || sources.length === 0) {
    return (
      <div className="w-full max-w-4xl mx-auto my-4 p-5 rounded-2xl bg-slate-900/60 border border-white/5 text-center text-sm text-slate-400">
        No candidate evidence passages retrieved for this query.
      </div>
    );
  }

  return (
    <div className="w-full max-w-4xl mx-auto my-4">
      <div className="flex items-center justify-between mb-3 px-1">
        <div className="flex items-center gap-2">
          <Database className="w-4 h-4 text-cyan-400 shrink-0" />
          <h3 className="text-sm font-bold text-slate-200 uppercase tracking-wider">
            Retrieved Evidence Sources ({sources.length})
          </h3>
        </div>
        <span className="text-xs text-slate-400 font-mono">Dataset: MSMARCO-XI</span>
      </div>

      <div className="flex flex-col gap-2.5">
        {sources.map((src, idx) => {
          const isExpanded = expandedIndex === idx;
          const isGold = src.is_selected === 1;
          const similarityScore = Math.round((src.score || 0) * 100);

          return (
            <div
              key={src.chunk_id || idx}
              className={`rounded-xl border transition-all duration-200 ${
                isExpanded
                  ? 'bg-slate-900/95 border-cyan-500/40 shadow-lg'
                  : 'bg-slate-900/50 border-white/5 hover:border-white/15'
              }`}
            >
              {/* Header Row */}
              <button
                type="button"
                onClick={() => setExpandedIndex(isExpanded ? null : idx)}
                className="w-full px-4 py-3 flex items-center justify-between text-left gap-3"
              >
                <div className="flex items-center gap-3 flex-wrap">
                  <span className="flex items-center justify-center w-6 h-6 rounded-md bg-cyan-500/10 text-cyan-400 font-mono text-xs font-bold border border-cyan-500/20">
                    #{idx + 1}
                  </span>

                  <span className="text-xs font-bold text-slate-200">
                    {src.chunk_id || `Passage ${(src.passage_idx ?? idx) + 1}`}
                  </span>

                  {isGold && (
                    <span className="flex items-center gap-1 text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-md bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                      <CheckCircle className="w-3 h-3" />
                      Gold Relevant
                    </span>
                  )}

                  <span className="text-xs px-2 py-0.5 rounded-md bg-slate-800 text-slate-300 border border-white/5 font-mono">
                    Similarity: <strong className="text-cyan-300">{similarityScore}%</strong>
                  </span>
                </div>

                <div className="flex items-center gap-2 shrink-0">
                  <span className="text-[11px] text-slate-400 uppercase font-mono hidden sm:inline">
                    {src.language || 'hi'}
                  </span>
                  {isExpanded ? (
                    <ChevronUp className="w-4 h-4 text-slate-400" />
                  ) : (
                    <ChevronDown className="w-4 h-4 text-slate-400" />
                  )}
                </div>
              </button>

              {/* Expanded Content */}
              {isExpanded && (
                <div className="px-4 pb-4 pt-1 border-t border-white/5 space-y-3 text-xs">
                  {/* Retrieved Indic Passage */}
                  <div>
                    <div className="flex items-center gap-1 text-[11px] font-semibold uppercase text-cyan-400 mb-1">
                      <Languages className="w-3 h-3 shrink-0" />
                      <span>Retrieved Indic Passage Text ({src.language || 'Hindi'}):</span>
                    </div>
                    <p className="text-slate-200 text-sm leading-relaxed bg-slate-950/60 p-3 rounded-lg border border-white/5 font-sans">
                      {src.text}
                    </p>
                  </div>

                  {/* English Original Passage */}
                  {src.english_text && (
                    <div>
                      <div className="text-[11px] font-semibold uppercase text-slate-400 mb-1">
                        <span>Original English Passage:</span>
                      </div>
                      <p className="text-slate-300 text-xs leading-relaxed bg-slate-950/40 p-2.5 rounded-lg border border-white/5 font-sans">
                        {src.english_text}
                      </p>
                    </div>
                  )}

                  {/* Metadata Chips */}
                  <div className="flex flex-wrap gap-2 pt-1 font-mono text-[10px] text-slate-400">
                    {src.query_id && (
                      <span className="px-2 py-1 bg-slate-800/80 rounded border border-white/5">
                        Query ID: {src.query_id}
                      </span>
                    )}
                    <span className="px-2 py-1 bg-slate-800/80 rounded border border-white/5">
                      Strategy: {src.strategy || 'passage_aware'}
                    </span>
                    {src.passage_idx !== undefined && (
                      <span className="px-2 py-1 bg-slate-800/80 rounded border border-white/5">
                        Passage Index: {src.passage_idx}
                      </span>
                    )}
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}