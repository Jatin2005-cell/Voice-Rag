import React, { useState, useRef, useEffect } from 'react';
import { Send, Sparkles, Globe2, RefreshCw, AlertCircle, Search, HelpCircle } from 'lucide-react';
import MicButton from '../components/MicButton';
import Waveform from '../components/Waveform';
import QueryChips from '../components/QueryChips';
import AnswerCard from '../components/AnswerCard';
import SourceCard from '../components/SourceCard';
import WhyThisAnswer from '../components/WhyThisAnswer';
import LatencyMeter from '../components/LatencyMeter';
import { sendTextQuery } from '../services/api';

export default function RagPage() {
  const [query, setQuery] = useState('');
  const [language, setLanguage] = useState('hi');
  const [micState, setMicState] = useState('idle');
  const [isListening, setIsListening] = useState(false);
  const [response, setResponse] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const recognitionRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);

  useEffect(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
      const recognition = new SpeechRecognition();
      recognition.continuous = false;
      recognition.interimResults = true;
      recognition.lang = language === 'hi' ? 'hi-IN' : language === 'en' ? 'en-US' : `${language}-IN`;

      recognition.onstart = () => {
        setIsListening(true);
        setMicState('listening');
        setError(null);
      };

      recognition.onresult = (event) => {
        const transcript = Array.from(event.results)
          .map((res) => res[0].transcript)
          .join('');
        setQuery(transcript);
      };

      recognition.onerror = (err) => {
        console.warn('Speech recognition error:', err);
        setIsListening(false);
        setMicState('idle');
      };

      recognition.onend = () => {
        setIsListening(false);
      };

      recognitionRef.current = recognition;
    }
  }, [language]);

  const handleMicToggle = async () => {
    if (isListening) {
      if (recognitionRef.current) recognitionRef.current.stop();
      if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
        mediaRecorderRef.current.stop();
      }
      setIsListening(false);
      setMicState('transcribing');
      
      setTimeout(() => {
        if (query && query.trim()) {
          handleSubmitQuery(query.trim());
        } else {
          setMicState('idle');
        }
      }, 500);
    } else {
      setQuery('');
      setError(null);
      setResponse(null);
      
      if (recognitionRef.current) {
        try { recognitionRef.current.start(); } catch (e) {}
      }

      if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        try {
          const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
          const mediaRecorder = new MediaRecorder(stream);
          audioChunksRef.current = [];
          mediaRecorder.ondataavailable = (e) => {
            if (e.data.size > 0) audioChunksRef.current.push(e.data);
          };
          mediaRecorder.onstop = async () => {
            stream.getTracks().forEach(track => track.stop());
          };
          mediaRecorder.start();
          mediaRecorderRef.current = mediaRecorder;
        } catch (e) {}
      }

      setIsListening(true);
      setMicState('listening');
    }
  };

  const handleSubmitQuery = async (queryText) => {
    const q = (queryText || query).trim();
    if (!q) return;

    setLoading(true);
    setError(null);
    setMicState('retrieving');

    try {
      setTimeout(() => {
        setMicState((prev) => (prev === 'retrieving' ? 'generating' : prev));
      }, 70);

      const res = await sendTextQuery(q, { language, topK: 5 });
      setResponse(res);
      setMicState('ready');
    } catch (err) {
      setError(err.message || 'Error communicating with backend');
      setMicState('idle');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      width: '100%',
      minHeight: '100vh',
      backgroundColor: '#020617',
      color: '#f8fafc',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      padding: '40px 16px',
      fontFamily: 'system-ui, -apple-system, sans-serif'
    }}>
      <div style={{ width: '100%', maxWidth: '800px', display: 'flex', flexDirection: 'column', gap: '32px' }}>

        {/* Header */}
        <div style={{ textAlign: 'center', display: 'flex', flexDirection: 'column', gap: '12px', alignItems: 'center' }}>
          <div style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '8px',
            padding: '6px 16px',
            borderRadius: '9999px',
            backgroundColor: 'rgba(99, 102, 241, 0.1)',
            border: '1px solid rgba(99, 102, 241, 0.2)',
            color: '#a5b4fc',
            fontSize: '12px',
            fontWeight: 600
          }}>
            <Sparkles size={14} color="#818cf8" />
            <span>Multilingual Voice Grounded RAG</span>
          </div>

          <h1 style={{ fontSize: '36px', fontWeight: 800, margin: 0, letterSpacing: '-0.025em' }}>
            Ask. Retrieve. Verify.
          </h1>

          <p style={{ fontSize: '14px', color: '#94a3b8', margin: 0, maxWidth: '500px', lineHeight: '1.5' }}>
            Query grounded facts across Indic languages using dense vector retrieval against MSMARCO-XI.
          </p>
        </div>

        {/* Language selector */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          gap: '12px',
          backgroundColor: '#0f172a',
          border: '1px solid #1e293b',
          padding: '10px 20px',
          borderRadius: '12px',
          alignSelf: 'center'
        }}>
          <Globe2 size={16} color="#818cf8" />
          <span style={{ fontSize: '13px', color: '#cbd5e1' }}>Language:</span>
          <select
            value={language}
            onChange={(e) => setLanguage(e.target.value)}
            style={{
              backgroundColor: '#1e293b',
              color: '#f8fafc',
              border: '1px solid #334155',
              padding: '6px 12px',
              borderRadius: '8px',
              fontSize: '13px',
              cursor: 'pointer'
            }}
          >
            <option value="hi">Hindi (हिन्दी)</option>
            <option value="bn">Bengali (বাংলা)</option>
            <option value="ta">Tamil (தமிழ்)</option>
            <option value="te">Telugu (తెలుగు)</option>
            <option value="mr">Marathi (मराठी)</option>
            <option value="gu">Gujarati (ગુજરાતી)</option>
            <option value="en">English (MS MARCO)</option>
          </select>
        </div>

        {/* Mic Container */}
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '16px' }}>
          <div style={{
            padding: '20px',
            backgroundColor: '#0f172a',
            borderRadius: '9999px',
            border: '1px solid #1e293b',
            boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.5)'
          }}>
            <MicButton state={micState} isListening={isListening} onClick={handleMicToggle} disabled={loading} />
          </div>
          <Waveform isListening={isListening} />
        </div>

        {/* Custom Query Input */}
        <div style={{
          backgroundColor: '#0f172a',
          border: '1px solid #1e293b',
          borderRadius: '16px',
          padding: '24px',
          display: 'flex',
          flexDirection: 'column',
          gap: '16px'
        }}>
          <label htmlFor="custom-query-input" style={{ fontSize: '12px', fontWeight: 700, color: '#818cf8', display: 'flex', alignItems: 'center', gap: '8px', letterSpacing: '0.05em' }}>
            <Search size={16} />
            <span>TYPE YOUR CUSTOM QUERY</span>
          </label>

          <form onSubmit={(e) => { e.preventDefault(); handleSubmitQuery(query); }} style={{ position: 'relative', width: '100%' }}>
            <input
              id="custom-query-input"
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Type or edit query (e.g. कॉर्पोरेशन क्या है?)..."
              style={{
                width: '100%',
                padding: '16px 56px 16px 16px',
                borderRadius: '12px',
                backgroundColor: '#020617',
                border: '1px solid #334155',
                color: '#f8fafc',
                fontSize: '15px',
                outline: 'none',
                boxSizing: 'border-box'
              }}
              disabled={loading}
            />

            <button
              type="submit"
              disabled={loading || !query.trim()}
              style={{
                position: 'absolute',
                right: '8px',
                top: '50%',
                transform: 'translateY(-50%)',
                padding: '10px 14px',
                borderRadius: '8px',
                backgroundColor: '#4f46e5',
                color: '#ffffff',
                border: 'none',
                cursor: loading || !query.trim() ? 'not-allowed' : 'pointer',
                opacity: loading || !query.trim() ? 0.4 : 1,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}
            >
              {loading ? <RefreshCw size={18} className="animate-spin" /> : <Send size={18} />}
            </button>
          </form>
        </div>

        {/* Sample Queries */}
        <div style={{
          backgroundColor: 'rgba(15, 23, 42, 0.5)',
          border: '1px solid #1e293b',
          borderRadius: '16px',
          padding: '20px',
          display: 'flex',
          flexDirection: 'column',
          gap: '12px'
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid #1e293b', paddingBottom: '10px' }}>
            <span style={{ fontSize: '12px', fontWeight: 700, color: '#94a3b8', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <HelpCircle size={15} color="#818cf8" />
              <span>SAMPLE DATASET QUERIES</span>
            </span>
            <span style={{ fontSize: '11px', color: '#64748b' }}>Click to test</span>
          </div>

          <QueryChips onSelectQuery={(sampleText) => { setQuery(sampleText); handleSubmitQuery(sampleText); }} />
        </div>

        {/* Error Notification */}
        {error && (
          <div style={{ padding: '14px 18px', borderRadius: '10px', backgroundColor: 'rgba(244, 63, 94, 0.1)', border: '1px solid rgba(244, 63, 94, 0.2)', color: '#fda4af', fontSize: '13px', display: 'flex', alignItems: 'center', gap: '10px' }}>
            <AlertCircle size={16} color="#f43f5e" />
            <span>{error}</span>
          </div>
        )}

        {/* Results Panel */}
        {response && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '20px', paddingTop: '20px', borderTop: '1px solid #1e293b' }}>
            <AnswerCard response={response} />
            <LatencyMeter latency={response.latency} />
            <WhyThisAnswer response={response} />
            <SourceCard sources={response.sources} />
          </div>
        )}

      </div>
    </div>
  );
}