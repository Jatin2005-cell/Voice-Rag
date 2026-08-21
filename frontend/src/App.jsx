import React, { useState } from 'react';
import Header from './components/Header';
import Footer from './components/Footer';
import RagPage from './pages/RagPage';
import EvaluationPage from './pages/EvaluationPage';
import SystemPage from './pages/SystemPage';

export default function App() {
  const [activeTab, setActiveTab] = useState('rag');

  return (
    <div className="min-h-screen bg-slate-950 bg-[radial-gradient(ellipse_80%_80%_at_50%_-20%,rgba(120,119,198,0.12),rgba(255,255,255,0))] text-slate-100 flex flex-col justify-between font-sans selection:bg-indigo-500 selection:text-white">
      <Header activeTab={activeTab} setActiveTab={setActiveTab} />
      
      <main className="flex-1 flex flex-col">
        {activeTab === 'rag' && <RagPage />}
        {activeTab === 'eval' && <EvaluationPage />}
        {activeTab === 'system' && <SystemPage />}
      </main>

      <Footer />
    </div>
  );
}