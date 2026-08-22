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
import sunRiseImg from '../assets/sun_rise.png';

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
      backgroundColor: '#0B3C2A',
      color: '#FACC15',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      padding: '40px 16px',
      fontFamily: 'system-ui, -apple-system, sans-serif',
      position: 'relative',
      overflow: 'hidden'
    }}>
      {/* Enhanced Visibility Sunrise Background Layer */}
      <div 
        style={{
          position: 'absolute',
          inset: 0,
          backgroundImage: `linear-gradient(to bottom, rgba(11, 60, 42, 0.45) 0%, rgba(11, 60, 42, 0.75) 60%, rgba(11, 60, 42, 0.95) 100%), url(${sunRiseImg})`,
          backgroundPosition: 'bottom center',
          backgroundSize: 'cover',
          backgroundRepeat: 'no-repeat',
          opacity: 0.55,
          pointerEvents: 'none',
          zIndex: 0
        }} 
      />

      <div style={{ width: '100%', maxWidth: '800px', display: 'flex', flexDirection: 'column', gap: '32px', position: 'relative', zIndex: 10 }}>

        {/* Header */}
        <div style={{ textAlign: 'center', display: 'flex', flexDirection: 'column', gap: '12px', alignItems: 'center' }}>
          <div style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '8px',
            padding: '6px 16px',
            borderRadius: '9999px',
            backgroundColor: 'rgba(7, 44, 30, 0.85)',
            border: '1px solid rgba(250, 204, 21, 0.6)',
            color: '#FACC15',
            fontSize: '12px',
            fontWeight: 700,
            textTransform: 'uppercase',
            backdropFilter: 'blur(8px)'
          }}>
            <Sparkles size={14} color="#FACC15" />
            <span>Multilingual Voice Grounded RAG</span>
          </div>

          <h1 style={{ fontSize: '38px', fontWeight: 900, margin: 0, letterSpacing: '-0.025em', color: '#FACC15', textShadow: '0 4px 12px rgba(0, 0, 0, 0.6)' }}>
            Ask. Retrieve. Verify.
          </h1>

          <p style={{ fontSize: '14px', color: '#FFFFFF', margin: 0, maxWidth: '500px', lineHeight: '1.5', fontWeight: 500, textShadow: '0 2px 8px rgba(0, 0, 0, 0.7)' }}>
            Query grounded facts across Indic languages using dense vector retrieval against MSMARCO-XI.
          </p>
        </div>

        {/* Language selector */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          gap: '12px',
          backgroundColor: 'rgba(7, 44, 30, 0.9)',
          backdropFilter: 'blur(12px)',
          border: '1px solid rgba(250, 204, 21, 0.4)',
          padding: '10px 20px',
          borderRadius: '12px',
          alignSelf: 'center',
          boxShadow: '0 10px 25px -5px rgba(0, 0, 0, 0.4)'
        }}>
          <Globe2 size={16} color="#FF2A85" />
          <span style={{ fontSize: '13px', color: '#FACC15', fontWeight: 600 }}>Language:</span>
          <select
            value={language}
            onChange={(e) => setLanguage(e.target.value)}
            style={{
              backgroundColor: '#0B3C2A',
              color: '#FACC15',
              border: '1px solid #FACC15',
              padding: '6px 12px',
              borderRadius: '8px',
              fontSize: '13px',
              fontWeight: 600,
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
            backgroundColor: 'rgba(7, 44, 30, 0.95)',
            backdropFilter: 'blur(12px)',
            borderRadius: '9999px',
            border: '2px solid #FF2A85',
            boxShadow: '0 20px 30px rgba(0, 0, 0, 0.6)'
          }}>
            <MicButton state={micState} isListening={isListening} onClick={handleMicToggle} disabled={loading} />
          </div>
          <Waveform isListening={isListening} />
        </div>

        {/* Custom Query Input */}
        <div style={{
          backgroundColor: 'rgba(7, 44, 30, 0.9)',
          backdropFilter: 'blur(16px)',
          border: '1px solid rgba(250, 204, 21, 0.4)',
          borderRadius: '16px',
          padding: '24px',
          display: 'flex',
          flexDirection: 'column',
          gap: '16px',
          boxShadow: '0 20px 30px rgba(0, 0, 0, 0.5)'
        }}>
          <label htmlFor="custom-query-input" style={{ fontSize: '12px', fontWeight: 800, color: '#FF2A85', display: 'flex', alignItems: 'center', gap: '8px', letterSpacing: '0.05em' }}>
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
                backgroundColor: 'rgba(11, 60, 42, 0.95)',
                border: '1px solid rgba(250, 204, 21, 0.5)',
                color: '#FFFFFF',
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
                backgroundColor: '#FF2A85',
                color: '#FFFFFF',
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
          backgroundColor: 'rgba(7, 44, 30, 0.9)',
          backdropFilter: 'blur(16px)',
          border: '1px solid rgba(250, 204, 21, 0.3)',
          borderRadius: '16px',
          padding: '20px',
          display: 'flex',
          flexDirection: 'column',
          gap: '12px',
          boxShadow: '0 20px 30px rgba(0, 0, 0, 0.4)'
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid rgba(250, 204, 21, 0.3)', paddingBottom: '10px' }}>
            <span style={{ fontSize: '12px', fontWeight: 800, color: '#FACC15', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <HelpCircle size={15} color="#FF2A85" />
              <span>SAMPLE DATASET QUERIES</span>
            </span>
            <span style={{ fontSize: '11px', color: '#E2E8F0' }}>Click to test</span>
          </div>

          <QueryChips onSelectQuery={(sampleText) => { setQuery(sampleText); handleSubmitQuery(sampleText); }} />
        </div>

        {/* Error Notification */}
        {error && (
          <div style={{ padding: '14px 18px', borderRadius: '10px', backgroundColor: 'rgba(255, 42, 133, 0.2)', border: '1px solid #FF2A85', color: '#FF2A85', fontSize: '13px', display: 'flex', alignItems: 'center', gap: '10px' }}>
            <AlertCircle size={16} color="#FF2A85" />
            <span>{error}</span>
          </div>
        )}

        {/* Results Panel */}
        {response && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '20px', paddingTop: '20px', borderTop: '1px solid rgba(250, 204, 21, 0.4)' }}>
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