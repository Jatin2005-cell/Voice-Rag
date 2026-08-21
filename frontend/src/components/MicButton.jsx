import React from 'react';
import { Mic, MicOff, RefreshCw } from 'lucide-react';

export default function MicButton({ state, isListening, onClick, onToggle, disabled }) {
  const activeListening = isListening || state === 'listening';
  const isProcessing = state === 'transcribing' || state === 'retrieving' || state === 'generating';
  const handleClick = onClick || onToggle;

  return (
    <button
      type="button"
      onClick={handleClick}
      disabled={disabled || isProcessing}
      className={`p-4 rounded-full transition-all duration-300 flex items-center justify-center border shadow-lg ${
        activeListening
          ? 'bg-rose-500/20 text-rose-400 border-rose-500/50 animate-pulse scale-110 shadow-rose-500/20'
          : isProcessing
          ? 'bg-cyan-500/20 text-cyan-400 border-cyan-500/40 animate-spin'
          : 'bg-slate-800 text-slate-200 hover:text-white hover:bg-slate-700 border-white/10 hover:border-cyan-500/50'
      } disabled:opacity-50 disabled:cursor-not-allowed`}
      title={activeListening ? 'Stop Recording' : 'Start Voice Input'}
    >
      {isProcessing ? (
        <RefreshCw className="w-6 h-6 animate-spin" />
      ) : activeListening ? (
        <MicOff className="w-6 h-6 text-rose-400" />
      ) : (
        <Mic className="w-6 h-6 text-cyan-400" />
      )}
    </button>
  );
}