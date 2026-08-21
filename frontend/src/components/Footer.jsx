import React from 'react';
import { Database, Shield, Zap } from 'lucide-react';

export default function Footer() {
  return (
    <footer
      style={{
        width: '100%',
        backgroundColor: '#020617',
        borderTop: '1px solid #1e293b',
        padding: '24px 32px',
        color: '#94a3b8',
        fontSize: '12px',
        boxSizing: 'border-box'
      }}
    >
      <div
        style={{
          maxWidth: '1280px',
          margin: '0 auto',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          gap: '16px'
        }}
      >
        {/* Dataset Credential */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Database size={16} color="#818cf8" />
          <span>
            Powered by <strong style={{ color: '#e2e8f0', fontWeight: 600 }}>ai4bharat/MSMARCO-XI</strong> Indic Multilingual Corpus
          </span>
        </div>

        {/* Feature Tags */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '20px', fontSize: '11px', fontFamily: 'monospace' }}>
          <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <Zap size={14} color="#fbbf24" />
            Sub-200ms SLA Target
          </span>
          <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <Shield size={14} color="#34d399" />
            Strict Abstention Guardrails
          </span>
        </div>

        {/* Copyright */}
        <div style={{ fontSize: '11px', color: '#64748b' }}>
          &copy; {new Date().getFullYear()} VoiceRAG Engine. Enterprise Search & Verification.
        </div>
      </div>
    </footer>
  );
}