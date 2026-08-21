import React, { useEffect, useRef } from 'react';

export default function Waveform({ isListening }) {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    let animationFrameId;
    let phase = 0;

    const render = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      const width = canvas.width;
      const height = canvas.height;
      const centerY = height / 2;

      const bars = 32;
      const barWidth = 3;
      const gap = (width - bars * barWidth) / (bars - 1);

      for (let i = 0; i < bars; i++) {
        const x = i * (barWidth + gap);
        let amplitude = 4;

        if (isListening) {
          // Dynamic oscillation
          const freq = Math.sin(phase + i * 0.25) * Math.cos(phase * 0.5 + i * 0.15);
          amplitude = Math.max(4, Math.abs(freq) * (height * 0.42));
        }

        // Gradient color for bars
        const grad = ctx.createLinearGradient(0, centerY - amplitude, 0, centerY + amplitude);
        grad.addColorStop(0, '#38bdf8');
        grad.addColorStop(0.5, '#6366f1');
        grad.addColorStop(1, '#a855f7');

        ctx.fillStyle = grad;
        ctx.beginPath();
        ctx.roundRect(x, centerY - amplitude, barWidth, amplitude * 2, 2);
        ctx.fill();
      }

      phase += isListening ? 0.12 : 0.02;
      animationFrameId = requestAnimationFrame(render);
    };

    render();

    return () => {
      cancelAnimationFrame(animationFrameId);
    };
  }, [isListening]);

  return (
    <div className="w-full max-w-xs h-12 flex items-center justify-center my-2">
      <canvas
        ref={canvasRef}
        width={240}
        height={48}
        className="w-full h-full opacity-90"
      />
    </div>
  );
}
