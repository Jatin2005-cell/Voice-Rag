import React from 'react';
import { ShieldCheck, Sparkles, Activity, Layers } from 'lucide-react';

export default function Navbar({ activeTab, setActiveTab }) {
  return (
    <header style={{
      width: '100%',
      backgroundColor: '#0f172a',
      borderBottom: '1px solid #1e293b',
      padding: '14px 28px',
      position: 'relative', // Sticky ki jagah relative se bhi test kar sakte ho
      zIndex: 50,
      boxSizing: 'border-box'
    }}>
      <div style={{
        maxWidth: '1280px',
        margin: '0 auto',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        gap: '20px'
      }}>
        
        {/* LEFT: Logo & Subtitle */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{
            padding: '8px',
            backgroundColor: 'rgba(99, 102, 241, 0.1)',
            border: '1px solid rgba(99, 102, 241, 0.25)',
            borderRadius: '10px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}>
            <ShieldCheck size={22} color="#818cf8" />
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{ fontSize: '16px', fontWeight: '800', color: '#ffffff', letterSpacing: '-0.02em', whiteSpace: 'nowrap' }}>
                VoiceRAG Engine
              </span>
              <span style={{
                fontSize: '10px',
                fontWeight: '700',
                backgroundColor: '#1e293b',
                color: '#818cf8',
                padding: '2px 6px',
                borderRadius: '4px',
                border: '1px solid #334155'
              }}>
                MSMARCO-XI
              </span>
            </div>
            <p style={{ fontSize: '11px', color: '#64748b', margin: '2px 0 0 0', fontWeight: '500', whiteSpace: 'nowrap' }}>
              Sub-200ms Indic Retrieval & Verification
            </p>
          </div>
        </div>

        {/* RIGHT: Navigation Tabs + Badge */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px', marginLeft: 'auto' }}>
          <nav style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <button
              onClick={() => setActiveTab && setActiveTab('playground')}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                padding: '8px 14px',
                borderRadius: '8px',
                fontSize: '13px',
                fontWeight: '600',
                border: 'none',
                cursor: 'pointer',
                backgroundColor: activeTab === 'playground' ? '#4f46e5' : 'transparent',
                color: activeTab === 'playground' ? '#ffffff' : '#94a3b8',
                whiteSpace: 'nowrap'
              }}
            >
              <Sparkles size={15} />
              <span>RAG Playground</span>
            </button>

            <button
              onClick={() => setActiveTab && setActiveTab('metrics')}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                padding: '8px 14px',
                borderRadius: '8px',
                fontSize: '13px',
                fontWeight: '600',
                border: 'none',
                cursor: 'pointer',
                backgroundColor: activeTab === 'metrics' ? '#4f46e5' : 'transparent',
                color: activeTab === 'metrics' ? '#ffffff' : '#94a3b8',
                whiteSpace: 'nowrap'
              }}
            >
              <Activity size={15} />
              <span>Evaluation Metrics</span>
            </button>

            <button
              onClick={() => setActiveTab && setActiveTab('architecture')}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                padding: '8px 14px',
                borderRadius: '8px',
                fontSize: '13px',
                fontWeight: '600',
                border: 'none',
                cursor: 'pointer',
                backgroundColor: activeTab === 'architecture' ? '#4f46e5' : 'transparent',
                color: activeTab === 'architecture' ? '#ffffff' : '#94a3b8',
                whiteSpace: 'nowrap'
              }}
            >
              <Layers size={15} />
              <span>Architecture & Index</span>
            </button>
          </nav>

          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            padding: '6px 12px',
            borderRadius: '9999px',
            backgroundColor: 'rgba(16, 185, 129, 0.1)',
            border: '1px solid rgba(16, 185, 129, 0.2)',
            fontSize: '12px',
            fontWeight: '600',
            color: '#34d399',
            whiteSpace: 'nowrap'
          }}>
            
          </div>
        </div>

      </div>
    </header>
  );
}