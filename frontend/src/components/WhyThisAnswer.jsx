import React, { useState } from 'react';
import { HelpCircle, ChevronDown, ChevronUp, CheckCircle2, XCircle } from 'lucide-react';

export default function WhyThisAnswer({ response }) {
  const [isOpen, setIsOpen] = useState(false);

  if (!response || !response.why_this_answer) return null;

  const why = response.why_this_answer;
  const grounding = response.grounding_details;
  const sourcesCount = response.sources?.length || 0;

  return (
    <div className="w-full max-w-4xl mx-auto my-3">
      <div className="rounded-xl border border-white/10 bg-slate-900/60 overflow-hidden">
        <button
          type="button"
          onClick={() => setIsOpen(!isOpen)}
          className="w-full px-4 py-2.5 flex items-center justify-between text-left hover:bg-slate-800/50 transition-colors"
        >
          <div className="flex items-center gap-2 text-xs font-bold text-slate-300">
            <HelpCircle className="w-4 h-4 text-indigo-400 shrink-0" />
            <span>Why this answer? (Verification & Transparency Trail)</span>
          </div>

          <div className="flex items-center gap-1 text-xs text-slate-400">
            <span>{isOpen ? 'Collapse' : 'Explain Logic'}</span>
            {isOpen ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
          </div>
        </button>

        {isOpen && (
          <div className="px-4 py-3 border-t border-white/5 bg-slate-950/40 space-y-2.5 text-xs text-slate-300">
            {/* Step 1: Input Validation */}
            <div className="flex items-start gap-2.5">
              {why.input_valid ? (
                <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
              ) : (
                <XCircle className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
              )}
              <div>
                <p className="font-semibold text-slate-200">1. Query Preprocessing & Safety Guardrail</p>
                <p className="text-slate-400 text-[11px]">
                  Input query verified against safety filters and minimum length requirements.
                </p>
              </div>
            </div>

            {/* Step 2: Vector Retrieval */}
            <div className="flex items-start gap-2.5">
              {sourcesCount > 0 ? (
                <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
              ) : (
                <XCircle className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
              )}
              <div>
                <p className="font-semibold text-slate-200">2. Dense Vector Retrieval (MSMARCO-XI)</p>
                <p className="text-slate-400 text-[11px]">
                  Scanned precomputed multilingual embeddings. Retrieved {sourcesCount} candidate passages.
                  {why.top_similarity_score !== undefined
                    ? ` Top similarity score: ${(why.top_similarity_score * 100).toFixed(1)}%.`
                    : ''}
                </p>
              </div>
            </div>

            {/* Step 3: Evidence Cutoff */}
            <div className="flex items-start gap-2.5">
              {why.evidence_threshold_met ? (
                <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
              ) : (
                <XCircle className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
              )}
              <div>
                <p className="font-semibold text-slate-200">3. Relevance & Abstention Guardrail</p>
                <p className="text-slate-400 text-[11px]">
                  {why.evidence_threshold_met
                    ? 'Retrieved passages passed similarity cutoff. Context synthesized for LLM.'
                    : 'Evidence similarity below required confidence cutoff. Abstention guardrail triggered to prevent hallucination.'}
                </p>
              </div>
            </div>

            {/* Step 4: Grounding Verification */}
            <div className="flex items-start gap-2.5">
              {why.grounding_passed ? (
                <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
              ) : (
                <XCircle className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
              )}
              <div>
                <p className="font-semibold text-slate-200">4. Grounding & Faithfulness Validation</p>
                <p className="text-slate-400 text-[11px]">
                  {grounding?.overlap_ratio !== undefined
                    ? `Claim verification completed with ${(grounding.overlap_ratio * 100).toFixed(1)}% contextual token overlap.`
                    : 'Verified synthesized claims strictly match retrieved passages.'}
                </p>
              </div>
            </div>

            {/* Summary Note */}
            {why.reason && (
              <div className="pt-2 border-t border-white/5 text-[11px] text-cyan-300/80 font-mono">
                Status: {why.reason}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}