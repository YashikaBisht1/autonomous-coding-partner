import React, { useEffect, useRef } from 'react';
import mermaid from 'mermaid';

mermaid.initialize({
    startOnLoad: true,
    theme: 'dark',
    securityLevel: 'loose',
    themeVariables: {
        primaryColor: '#ff007f',
        primaryTextColor: '#fff',
        primaryBorderColor: '#fff',
        lineColor: '#00d9ff',
        secondaryColor: '#bc13fe',
        tertiaryColor: '#39ff14'
    }
});

const AnalysisView = ({ analysis, onBack }) => {
    const mermaidRef = useRef(null);

    useEffect(() => {
        if (analysis?.mermaid_graph && mermaidRef.current) {
            // Clear previous content
            mermaidRef.current.innerHTML = analysis.mermaid_graph;
            mermaidRef.current.removeAttribute('data-processed');
            try {
                mermaid.contentLoaded();
            } catch (e) {
                console.error("Mermaid render error:", e);
            }
        }
    }, [analysis]);

    if (!analysis) return <div className="ide-panel">NO_ANALYSIS_DATA</div>;

    return (
        <div className="ide-panel animate-fade-in" style={{ padding: '2rem', width: '100%', maxWidth: '1000px', margin: '0 auto' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
                <h2 className="pink-glow" style={{ fontSize: '1.5rem' }}>CODEBASE_INTELLIGENCE</h2>
                <button onClick={onBack} style={{ fontSize: '0.8rem' }}>CLOSE_ANALYSIS</button>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem' }}>
                <section style={{ gridColumn: '1 / span 2' }}>
                    <div className="pink-glow" style={{ fontSize: '0.8rem', fontWeight: 'bold', marginBottom: '1rem' }}>DEPENDENCY_GRAPH</div>
                    <div style={{
                        padding: '2rem',
                        background: 'rgba(0,0,0,0.3)',
                        border: '1px solid var(--border-dim)',
                        borderRadius: '4px',
                        overflowX: 'auto',
                        display: 'flex',
                        justifyContent: 'center'
                    }}>
                        <div className="mermaid" ref={mermaidRef}>
                            {analysis.mermaid_graph}
                        </div>
                    </div>
                </section>

                <section>
                    <div className="pink-glow" style={{ fontSize: '0.8rem', fontWeight: 'bold', marginBottom: '1rem' }}>ARCHITECTURE_SUMMARY</div>
                    <div style={{ padding: '1rem', background: 'rgba(0,0,0,0.3)', border: '1px solid var(--border-dim)', borderRadius: '4px', fontSize: '0.9rem', lineHeight: '1.6' }}>
                        {analysis.architecture_summary || "NO_SUMMARY_AVAILABLE"}
                    </div>
                </section>

                <section>
                    <div className="pink-glow" style={{ fontSize: '0.8rem', fontWeight: 'bold', marginBottom: '1rem' }}>TECHNICAL_DEBT // SEVERITY</div>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                        {analysis.technical_debt?.length > 0 ? analysis.technical_debt.map((debt, i) => (
                            <div key={i} style={{
                                padding: '1rem',
                                background: 'rgba(255, 0, 127, 0.05)',
                                border: '1px solid var(--primary)',
                                borderRadius: '4px'
                            }}>
                                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                                    <span style={{ fontWeight: 'bold', color: 'var(--primary)', fontSize: '0.8rem' }}>{debt.severity?.toUpperCase() || 'MEDIUM'}</span>
                                    <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>{debt.location}</span>
                                </div>
                                <div style={{ fontSize: '0.85rem' }}>{debt.issue}</div>
                            </div>
                        )) : <div style={{ opacity: 0.5, fontSize: '0.8rem' }}>NO_DEBT_FOUND</div>}
                    </div>
                </section>

                <section style={{ gridColumn: '1 / span 2' }}>
                    <div className="pink-glow" style={{ fontSize: '0.8rem', fontWeight: 'bold', marginBottom: '1rem' }}>COMPONENTS_MAP</div>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '1rem' }}>
                        {analysis.components?.map((comp, i) => (
                            <div key={i} style={{ padding: '1rem', border: '1px solid var(--border-dim)', background: 'rgba(255,255,255,0.02)' }}>
                                <div style={{ fontWeight: 'bold', color: 'var(--text-pink)', marginBottom: '0.5rem' }}>{comp.name}</div>
                                <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '0.5rem' }}>{comp.purpose}</div>
                                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.3rem' }}>
                                    {comp.files?.map((f, j) => (
                                        <span key={j} style={{ fontSize: '0.65rem', background: '#222', padding: '0.2rem 0.4rem', borderRadius: '2px' }}>{f}</span>
                                    ))}
                                </div>
                            </div>
                        ))}
                    </div>
                </section>

                <section style={{ gridColumn: '1 / span 2' }}>
                    <div className="pink-glow" style={{ fontSize: '0.8rem', fontWeight: 'bold', marginBottom: '1rem' }}>MODERNIZATION_REFTS</div>
                    <div style={{ display: 'grid', gap: '1rem' }}>
                        {analysis.refactoring_suggestions?.map((sug, i) => (
                            <div key={i} style={{ display: 'flex', gap: '1rem', borderLeft: '3px solid var(--status-info)', padding: '1rem', background: 'rgba(0, 217, 255, 0.05)' }}>
                                <div style={{ flex: 1 }}>
                                    <div style={{ fontWeight: 'bold', fontSize: '0.85rem' }}>{sug.target}</div>
                                    <div style={{ fontSize: '0.85rem', marginTop: '0.3rem' }}>{sug.suggestion}</div>
                                </div>
                                <div style={{ width: '30%', fontSize: '0.75rem', opacity: 0.8 }}>
                                    <span style={{ color: 'var(--status-info)' }}>BENEFIT:</span> {sug.benefit}
                                </div>
                            </div>
                        ))}
                    </div>
                </section>
            </div>
        </div>
    );
};

export default AnalysisView;
