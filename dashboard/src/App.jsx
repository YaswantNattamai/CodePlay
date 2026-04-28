import React, { useState, useRef, useEffect } from 'react';
import './index.css';

const NOTE_MAP = {
    'C': 0, 'C#': 1, 'D': 2, 'D#': 3, 'E': 4,
    'F': 5, 'F#': 6, 'G': 7, 'G#': 8, 'A': 9, 'A#': 10, 'B': 11
};

const INSTRUMENT_COLORS = {
  EP: 'var(--c-ep)',
  BASS: 'var(--c-bass)',
  DRUMS: 'var(--c-drums)',
  LEAD: 'var(--c-lead)',
  PAD: 'var(--c-pad)',
  STRINGS: 'var(--c-strings)',
};

const INITIAL_CODE = `PATTERN groove {
    DRUMS: KICK every 0.5, HAT every 0.25
    BASS: C2 [0.0-0.5] @90
}

LOOP 4 {
    SECOND 1 {
        USE groove
        LEAD: C5 [0.0-0.5] @80 REVERB DELAY
        PAD: E4 [0.0-1.0] @70
    }
}
`;

function noteToFreq(noteStr) {
    if (!noteStr) return 440;
    if (['KICK', 'SNARE', 'HAT', 'CRASH'].includes(noteStr)) return 150;
    
    let pitch = noteStr.length === 2 ? noteStr[0] : noteStr.slice(0, 2);
    let octave = parseInt(noteStr.length === 2 ? noteStr[1] : noteStr[2], 10) || 4;
    
    let midi = (octave + 1) * 12 + (NOTE_MAP[pitch] || 0);
    return 440.0 * Math.pow(2.0, (midi - 69) / 12.0);
}

function playNote(noteStr) {
    const AudioContext = window.AudioContext || window.webkitAudioContext;
    if (!AudioContext) return;
    const audioCtx = new AudioContext();
    const oscillator = audioCtx.createOscillator();
    const gainNode = audioCtx.createGain();
    
    oscillator.type = 'sawtooth';
    oscillator.frequency.value = noteToFreq(noteStr);
    
    oscillator.connect(gainNode);
    gainNode.connect(audioCtx.destination);
    
    const now = audioCtx.currentTime;
    gainNode.gain.setValueAtTime(0, now);
    gainNode.gain.linearRampToValueAtTime(0.3, now + 0.05);
    gainNode.gain.exponentialRampToValueAtTime(0.001, now + 0.5);
    
    oscillator.start(now);
    oscillator.stop(now + 0.5);
}

function App() {
  const [code, setCode] = useState(INITIAL_CODE);
  const [data, setData] = useState(null);
  const [isCompiling, setIsCompiling] = useState(false);
  const [error, setError] = useState(null);
  
  const audioRef = useRef(null);

  const handleCompile = async () => {
    setIsCompiling(true);
    setError(null);
    try {
      const res = await fetch('http://127.0.0.1:8000/compile', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code })
      });
      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || 'Compilation failed');
      }
      const result = await res.json();
      setData(result.ir);
      
      // Force audio reload to fetch new wav
      if (audioRef.current) {
        audioRef.current.src = `http://127.0.0.1:8000/audio?t=${Date.now()}`;
        audioRef.current.load();
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setIsCompiling(false);
    }
  };

  const instruments = ['EP', 'BASS', 'DRUMS', 'LEAD', 'PAD', 'STRINGS'];
  const totalSeconds = data ? (data.duration || 4) : 4;
  const pixelsPerSecond = 200;

  const keyboardNotes = ['C4', 'C#4', 'D4', 'D#4', 'E4', 'F4', 'F#4', 'G4', 'G#4', 'A4', 'A#4', 'B4'];

  return (
    <div>
      <nav className="navbar">
        <h1>CodePlay</h1>
        <div className="keyboard">
          {keyboardNotes.map(n => (
            <button 
              key={n} 
              onClick={() => playNote(n)}
              className="key-btn"
            >
              {n.replace('4', '')}
            </button>
          ))}
        </div>
      </nav>

      <main className="app-container">
        {/* Left Pane: Code Editor */}
        <div className="left-pane">
          <div className="editor-header">
            <h2>Source Code</h2>
            <button 
              className="compile-btn" 
              onClick={handleCompile}
              disabled={isCompiling}
            >
              {isCompiling ? 'Compiling...' : 'Compile & Render'}
            </button>
          </div>
          <textarea 
            className="code-editor"
            value={code}
            onChange={(e) => setCode(e.target.value)}
            spellCheck="false"
          />
        </div>

        {/* Right Pane: Timeline & Player */}
        <div className="right-pane">
          {error && (
            <div className="error-msg">
              <strong>Compiler Error:</strong><br/>{error}
            </div>
          )}

          <div className="player-card">
            <h3 style={{ margin: 0, color: '#94a3b8', width: '80px' }}>Player</h3>
            <audio ref={audioRef} controls />
          </div>

          <div className="timeline-container">
            {!data ? (
              <div style={{ color: '#94a3b8', textAlign: 'center', marginTop: '4rem' }}>
                Click "Compile & Render" to view the timeline visualization.
              </div>
            ) : (
              <>
                <div className="time-markers" style={{ width: `${totalSeconds * pixelsPerSecond + 150}px` }}>
                  {Array.from({length: totalSeconds + 1}).map((_, i) => (
                    <div key={i} className="marker" style={{ width: `${pixelsPerSecond}px` }}>
                      <span>{i}s</span>
                      <div className="grid-line"></div>
                    </div>
                  ))}
                </div>

                <div className="tracks">
                  {instruments.map(instr => {
                    const allNotes = [];
                    (data.timeline || []).forEach(block => {
                      const secondOffset = block.second - 1;
                      const trackNotes = block.tracks[instr] || [];
                      trackNotes.forEach(n => {
                        allNotes.push({
                          ...n,
                          absoluteStart: secondOffset + n.start,
                          absoluteEnd: secondOffset + n.end
                        });
                      });
                    });

                    if (allNotes.length === 0) return null;

                    return (
                      <div key={instr} className="track-row">
                        <div className="track-label" style={{ color: INSTRUMENT_COLORS[instr] }}>
                          {instr}
                        </div>
                        <div className="track-content" style={{ width: `${totalSeconds * pixelsPerSecond}px` }}>
                          {allNotes.map((n, i) => {
                            const left = n.absoluteStart * pixelsPerSecond;
                            const width = (n.absoluteEnd - n.absoluteStart) * pixelsPerSecond;
                            const opacity = n.velocity ? Math.max(0.3, n.velocity / 127) : 0.8;
                            
                            return (
                              <div 
                                key={i}
                                className="note-block"
                                style={{ 
                                  left: `${left}px`, 
                                  width: `${Math.max(width, 5)}px`, 
                                  backgroundColor: INSTRUMENT_COLORS[instr],
                                  opacity: opacity
                                }}
                                title={`Note: ${n.note} | Vel: ${n.velocity}`}
                              >
                                {width > 20 ? n.note : ''}
                              </div>
                            )
                          })}
                        </div>
                      </div>
                    );
                  })}
                </div>
              </>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;
