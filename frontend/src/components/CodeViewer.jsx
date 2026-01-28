import React from 'react';

function CodeViewer({ files }) {
  if (!files || files.length === 0) return null;

  return (
    <div className="ide-panel animate-fade-in" style={{ overflow: 'hidden' }}>
      <div style={{ padding: '0.75rem 1rem', borderBottom: '1px solid var(--border-dim)', background: '#111' }}>
        <h3 style={{ fontSize: '0.85rem', color: 'var(--text-pink)' }}>EXPLORER // ARTIFACTS</h3>
      </div>
      <div style={{ padding: '1rem', maxHeight: '400px', overflowY: 'auto' }}>
        <div style={{ display: 'grid', gap: '0.5rem' }}>
          {files.map((file, index) => (
            <div key={index} style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.75rem',
              padding: '0.75rem',
              background: 'var(--bg-input)',
              borderRadius: '2px',
              border: '1px solid var(--border-dim)',
              transition: 'border-color 0.2s',
              cursor: 'pointer'
            }}
              onMouseEnter={(e) => e.currentTarget.style.borderColor = 'var(--primary)'}
              onMouseLeave={(e) => e.currentTarget.style.borderColor = 'var(--border-dim)'}
            >
              <span style={{ color: 'var(--primary)' }}>{file.endsWith('.py') ? '🐍' : '📄'}</span>
              <div style={{ flex: 1 }}>
                <div style={{ fontWeight: '600', fontSize: '0.85rem' }}>{file}</div>
                <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>PROJECT_ASSET</div>
              </div>
              <div style={{ fontSize: '0.6rem', padding: '2px 6px', border: '1px solid #444', color: '#888' }}>
                READONLY
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default CodeViewer;
