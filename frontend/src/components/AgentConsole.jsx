import React, { useState, useEffect, useRef } from 'react';

function AgentConsole({ logs }) {
  const scrollRef = useRef(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [logs]);

  return (
    <div className="ide-panel scanline-effect" style={{
      display: 'flex',
      flexDirection: 'column',
      height: '450px',
      marginTop: '1.5rem',
      backgroundColor: '#000'
    }}>
      <div style={{
        padding: '0.75rem 1rem',
        borderBottom: '1px solid var(--border-dim)',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        backgroundColor: '#111'
      }}>
        <h3 style={{ fontSize: '0.85rem', color: 'var(--text-pink)', letterSpacing: '1px' }}>
          TERMINAL // DEVELOPER_AGENTS
        </h3>
        <div style={{ display: 'flex', gap: '6px' }}>
          <div style={{ width: '12px', height: '12px', borderRadius: '50%', background: '#ff5f56' }}></div>
          <div style={{ width: '12px', height: '12px', borderRadius: '50%', background: '#ffbd2e' }}></div>
          <div style={{ width: '12px', height: '12px', borderRadius: '50%', background: '#27c93f' }}></div>
        </div>
      </div>

      <div
        ref={scrollRef}
        style={{
          padding: '1.5rem',
          overflowY: 'auto',
          flex: 1,
          display: 'flex',
          flexDirection: 'column',
          gap: '0.5rem',
          fontSize: '0.9rem',
          lineHeight: '1.4'
        }}
      >
        {logs.length === 0 ? (
          <div style={{ color: '#444', fontStyle: 'italic' }}>
            {"> "} INITIALIZING SYSTEM...<br />
            {"> "} WAITING FOR INPUT...
          </div>
        ) : (
          logs.map((log, index) => (
            <div key={index} style={{
              display: 'flex',
              gap: '1rem',
              color: log.type === 'error' ? 'var(--status-error)' :
                log.type === 'progress' ? 'var(--secondary)' : 'var(--text-main)'
            }}>
              <span style={{ color: '#555', minWidth: '85px' }}>{new Date(log.timestamp || Date.now()).toLocaleTimeString()}</span>
              <span>
                <span style={{ color: 'var(--text-pink)' }}>root@cyber-agent:~$</span> {log.message}
              </span>
            </div>
          ))
        )}
        <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center', marginTop: '0.5rem' }}>
          <span style={{ color: 'var(--text-pink)' }}>root@cyber-agent:~$</span>
          <span style={{
            width: '8px',
            height: '16px',
            background: 'var(--primary)',
            animation: 'blink 1s step-end infinite'
          }}></span>
        </div>
      </div>

      <style jsx>{`
        @keyframes blink {
          50% { opacity: 0; }
        }
      `}</style>
    </div>
  );
}

export default AgentConsole;
