import React from 'react';
import { Sparkles, Activity, Layers, ShieldCheck } from 'lucide-react';
import hackerHouseLogo from '../assets/hacker-house.png';
import goaHindiLogo from '../assets/goa_hindi.svg';

export default function Header({ activeTab, setActiveTab }) {
  const navItems = [
    { id: 'rag', label: 'RAG Playground', icon: Sparkles },
    { id: 'eval', label: 'Evaluation Metrics', icon: Activity },
    { id: 'system', label: 'Architecture & Index', icon: Layers },
  ];

  return (
    <header
      className="sticky top-0 z-50 w-full bg-slate-950/90 backdrop-blur-md border-b border-slate-800"
      style={{
        width: '100%',
        backgroundColor: '#020617',
        borderBottom: '1px solid #1e293b',
        padding: '10px 24px',
        position: 'sticky',
        top: 0,
        zIndex: 50,
        boxSizing: 'border-box',
      }}
    >
      <div
        className="max-w-7xl mx-auto"
        style={{
          maxWidth: '1280px',
          margin: '0 auto',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          position: 'relative',
          minHeight: '52px',
        }}
      >
        {/* LEFT — Brand */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
            flexShrink: 0,
          }}
        >
          <div
            style={{
              width: '38px',
              height: '38px',
              padding: '7px',
              backgroundColor: 'rgba(99, 102, 241, 0.1)',
              border: '1px solid rgba(99, 102, 241, 0.25)',
              borderRadius: '10px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              boxSizing: 'border-box',
            }}
          >
            <ShieldCheck size={22} color="#818cf8" />
          </div>

          <div>
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
              }}
            >
              <span
                style={{
                  fontSize: '16px',
                  fontWeight: '800',
                  color: '#ffffff',
                  letterSpacing: '-0.02em',
                  whiteSpace: 'nowrap',
                }}
              >
                VoiceRAG Engine
              </span>

              <span
                style={{
                  fontSize: '10px',
                  fontWeight: '700',
                  backgroundColor: '#1e293b',
                  color: '#818cf8',
                  padding: '2px 6px',
                  borderRadius: '4px',
                  border: '1px solid #334155',
                }}
              >
                MSMARCO-XI
              </span>
            </div>

            <p
              style={{
                fontSize: '11px',
                color: '#64748b',
                margin: '2px 0 0 0',
                fontWeight: '500',
                whiteSpace: 'nowrap',
              }}
            >
              Sub-200ms Indic Retrieval & Verification
            </p>
          </div>
        </div>

        {/* CENTER — Goa Hindi + Hacker House */}
        {/* CENTER — Hacker House with Goa Hindi overlay */}
<div
  style={{
    position: 'absolute',
    left: '50%',
    top: '50%',
    transform: 'translate(-50%, -50%)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    pointerEvents: 'none',
    width: '150px',
    height: '48px',
  }}
>
  {/* Hacker House — Main Logo */}
  <img
    src={hackerHouseLogo}
    alt="Hacker House"
    style={{
      width: '145px',
      height: 'auto',
      maxHeight: '48px',
      objectFit: 'contain',
      display: 'block',
    }}
  />

  {/* Goa Hindi — Overlay in the middle */}
  <img
    src={goaHindiLogo}
    alt="Goa Hindi"
    style={{
      position: 'absolute',
      width: '52px',
      height: 'auto',
      maxHeight: '18px',
      objectFit: 'contain',
      display: 'block',
      top: '50%',
      left: '50%',
      transform: 'translate(-50%, -50%)',
    }}
  />
</div>
        {/* RIGHT — Navigation */}
        <nav
          style={{
            marginLeft: 'auto',
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            backgroundColor: '#0f172a',
            padding: '6px',
            borderRadius: '12px',
            border: '1px solid #1e293b',
          }}
        >
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;

            return (
              <button
                key={item.id}
                onClick={() =>
                  setActiveTab && setActiveTab(item.id)
                }
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px',
                  padding: '8px 14px',
                  borderRadius: '8px',
                  fontSize: '12px',
                  fontWeight: '600',
                  border: 'none',
                  cursor: 'pointer',
                  backgroundColor: isActive
                    ? '#4f46e5'
                    : 'transparent',
                  color: isActive
                    ? '#ffffff'
                    : '#94a3b8',
                  transition: 'all 0.2s',
                  whiteSpace: 'nowrap',
                }}
              >
                <Icon size={14} />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>
      </div>
    </header>
  );
}