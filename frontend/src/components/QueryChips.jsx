import React from 'react';
import { Sparkles } from 'lucide-react';

export default function QueryChips({ onSelectQuery }) {
  const sampleQueries = [
    {
      label: 'कॉर्पोरेशन क्या है?',
      desc: 'In-domain MSMARCO',
      tag: 'Hindi',
      type: 'grounded'
    },
    {
      label: 'कंप्यूटर नेटवर्क के प्रकार क्या हैं?',
      desc: 'In-domain MSMARCO',
      tag: 'Hindi',
      type: 'grounded'
    },
    {
      label: 'What is a corporation?',
      desc: 'English MSMARCO',
      tag: 'English',
      type: 'grounded'
    },
    {
      label: 'क्वांटम कंप्यूटर में कितने क्यूबिट होते हैं?',
      desc: 'Out-of-domain (Test Abstention)',
      tag: 'Abstention Test',
      type: 'abstain'
    }
  ];

  return (
    <div className="w-full max-w-2xl mx-auto my-3">
      <div className="flex items-center gap-2 mb-2 text-xs font-semibold text-slate-400">
        <Sparkles className="w-3.5 h-3.5 text-cyan-400 shrink-0" />
        <span>Sample Dataset Queries (Click to test):</span>
      </div>
      <div className="flex flex-wrap gap-2">
        {sampleQueries.map((item, idx) => (
          <button
            key={idx}
            type="button"
            onClick={() => onSelectQuery(item.label)}
            className={`flex items-center gap-2 px-3 py-1.5 rounded-xl text-xs font-medium border transition-all active:scale-95 ${
              item.type === 'abstain'
                ? 'bg-rose-500/10 text-rose-300 border-rose-500/20 hover:bg-rose-500/20 hover:border-rose-500/30'
                : 'bg-slate-900/80 text-slate-300 border-white/10 hover:bg-slate-800 hover:text-cyan-300 hover:border-cyan-500/30'
            }`}
          >
            <span>{item.label}</span>
            <span
              className={`text-[10px] px-1.5 py-0.5 rounded-md font-mono ${
                item.type === 'abstain'
                  ? 'bg-rose-500/20 text-rose-300'
                  : 'bg-white/5 text-slate-400'
              }`}
            >
              {item.tag}
            </span>
          </button>
        ))}
      </div>
    </div>
  );
}