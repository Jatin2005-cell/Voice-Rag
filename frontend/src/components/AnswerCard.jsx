import React, { useState, useEffect } from 'react';
import {
  AlertTriangle,
  ShieldCheck,
  Zap,
  Volume2,
  VolumeX,
  Copy,
  Check,
  Sparkles
} from 'lucide-react';

export default function AnswerCard({ response }) {
  const [copied, setCopied] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);

  useEffect(() => {
    return () => {
      if ('speechSynthesis' in window) {
        window.speechSynthesis.cancel();
      }
    };
  }, []);

  if (!response) return null;

  const { answer, grounded, confidence, sources, latency, transcript, guardrail } = response;
  const isAbstaining = !grounded || answer?.includes("couldn't find enough") || guardrail?.abstain;

  const copyToClipboard = () => {
    if (!answer) return;
    navigator.clipboard.writeText(answer);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const toggleSpeech = () => {
    if ('speechSynthesis' in window) {
      if (isSpeaking) {
        window.speechSynthesis.cancel();
        setIsSpeaking(false);
      } else {
        const utterance = new SpeechSynthesisUtterance(answer);
        if (/[\u0900-\u097F]/.test(answer)) {
          utterance.lang = 'hi-IN';
        } else {
          utterance.lang = 'en-US';
        }
        utterance.onend = () => setIsSpeaking(false);
        utterance.onerror = () => setIsSpeaking(false);
        setIsSpeaking(true);
        window.speechSynthesis.speak(utterance);
      }
    }
  };

  const confidencePct = Math.round((confidence || 0) * 100);

  return (
    <div
      className={`w-full max-w-4xl mx-auto rounded-2xl p-6 transition-all duration-300 border ${
        isAbstaining
          ? 'bg-amber-950/20 border-amber-500/30 shadow-lg shadow-amber-500/5'
          : 'bg-slate-900/90 border-cyan-500/30 shadow-xl shadow-cyan-500/10'
      }`}
    >
      {/* Top Header Badges */}
      <div className="flex flex-wrap items-center justify-between gap-3 pb-4 mb-4 border-b border-white/10">
        <div className="flex flex-wrap items-center gap-2">
          {isAbstaining ? (
            <div className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-amber-500/15 border border-amber-500/30 text-amber-400 text-xs font-bold tracking-wide">
              <AlertTriangle className="w-3.5 h-3.5" />
              <span>Guardrail Abstention</span>
            </div>
          ) : (
            <div className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-500/15 border border-emerald-500/30 text-emerald-400 text-xs font-bold tracking-wide">
              <ShieldCheck className="w-4 h-4" />
              <span>Grounded Answer ✓</span>
            </div>
          )}

          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-slate-800 border border-white/10 text-xs text-slate-300 font-medium">
            <span className="text-slate-400">Confidence:</span>
            <span
              className={`font-bold font-mono ${
                confidencePct > 70 ? 'text-emerald-400' : 'text-amber-400'
              }`}
            >
              {confidencePct}%
            </span>
          </div>

          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-slate-800 border border-white/10 text-xs text-slate-300 font-medium">
            <span className="text-slate-400">Evidence:</span>
            <span className="font-bold text-cyan-300">{sources?.length || 0} Passages</span>
          </div>
        </div>

        {/* Latency Tag */}
        <div className="flex items-center gap-2">
          <div className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-cyan-500/10 border border-cyan-500/20 text-cyan-300 text-xs font-mono font-semibold">
            <Zap className="w-3.5 h-3.5 text-cyan-400" />
            <span>RAG: {latency?.total_rag_ms || 0} ms</span>
          </div>

          {latency?.stt_ms && (
            <div className="flex items-center gap-1 px-2.5 py-1 rounded-full bg-purple-500/10 border border-purple-500/20 text-purple-300 text-xs font-mono">
              <span>STT: {latency.stt_ms} ms</span>
            </div>
          )}
        </div>
      </div>

      {/* Answer Body */}
      <div className="my-2">
        <div className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1 flex items-center gap-1.5">
          <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
          <span>Synthesized Answer</span>
        </div>
        <p className="text-base sm:text-lg font-medium text-slate-100 leading-relaxed font-sans select-text">
          {answer}
        </p>
      </div>

      {/* Action Footer */}
      <div className="flex flex-wrap items-center justify-between gap-3 pt-4 mt-4 border-t border-white/5 text-xs text-slate-400">
        <div className="flex items-center gap-2 truncate max-w-full">
          <span className="font-mono text-[11px] text-slate-500 truncate">
            Query: "{transcript || response.query}"
          </span>
        </div>

        <div className="flex items-center gap-2 shrink-0">
          <button
            type="button"
            onClick={toggleSpeech}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 transition-all"
            title="Read aloud"
          >
            {isSpeaking ? (
              <VolumeX className="w-3.5 h-3.5 text-rose-400" />
            ) : (
              <Volume2 className="w-3.5 h-3.5 text-cyan-400" />
            )}
            <span>{isSpeaking ? 'Stop' : 'Listen'}</span>
          </button>

          <button
            type="button"
            onClick={copyToClipboard}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 transition-all"
            title="Copy answer"
          >
            {copied ? (
              <Check className="w-3.5 h-3.5 text-emerald-400" />
            ) : (
              <Copy className="w-3.5 h-3.5" />
            )}
            <span>{copied ? 'Copied' : 'Copy'}</span>
          </button>
        </div>
      </div>
    </div>
  );
}