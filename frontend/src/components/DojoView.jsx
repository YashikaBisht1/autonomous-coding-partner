import React, { useState, useEffect } from 'react';

const DojoView = ({ projectId, challenge, onBack, onVerify }) => {
    const [timeLeft, setTimeLeft] = useState(300); // 5 minute starting point
    const [status, setStatus] = useState('ACTIVE');
    const [result, setResult] = useState(null);

    useEffect(() => {
        const timer = setInterval(() => {
            setTimeLeft((prev) => (prev > 0 ? prev - 1 : 0));
        }, 1000);
        return () => clearInterval(timer);
    }, []);

    const formatTime = (seconds) => {
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    };

    const handleVerify = async () => {
        setStatus('VERIFYING');
        const res = await onVerify();
        if (res.success) {
            setStatus('COMPLETED');
            setResult(res);
        } else {
            setStatus('FAILED');
            setResult(res);
            setTimeout(() => setStatus('ACTIVE'), 3000);
        }
    };

    return (
        <div className="ide-panel animate-fade-in" style={{ padding: '2rem', width: '100%', maxWidth: '800px', margin: '0 auto', border: '2px solid var(--primary)', boxShadow: '0 0 20px rgba(255, 0, 127, 0.2)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
                <div>
                    <h2 className="pink-glow" style={{ fontSize: '1.5rem', margin: 0 }}>MISSION: THE_DOJO</h2>
                    <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>PROJECT_ID: {projectId} // CHALLENGE_ID: {challenge.challenge_id}</span>
                </div>
                <div style={{ textAlign: 'right' }}>
                    <div style={{ fontSize: '2rem', fontWeight: 'bold', fontFamily: 'monospace', color: timeLeft < 60 ? 'var(--status-error)' : 'var(--primary)' }}>
                        {formatTime(timeLeft)}
                    </div>
                    <span style={{ fontSize: '0.6rem', color: 'var(--text-muted)' }}>TIME_REMAINING</span>
                </div>
            </div>

            <div style={{ background: 'rgba(0,0,0,0.5)', padding: '1.5rem', borderRadius: '4px', marginBottom: '2rem', border: '1px solid #333' }}>
                <div style={{ color: 'var(--primary)', fontWeight: 'bold', fontSize: '0.8rem', marginBottom: '0.5rem' }}>MISSION_INTELLIGENCE</div>
                <div style={{ fontSize: '0.95rem', lineHeight: '1.6', color: '#eee' }}>
                    {challenge.message}
                    <br /><br />
                    <span style={{ color: 'var(--status-info)' }}>[SYSTEM_LOG]:</span> A subtle logic error has been detected in <span style={{ color: 'var(--primary)' }}>{challenge.file}</span>.
                    {challenge.intel && (
                        <div style={{ marginTop: '1rem', padding: '0.5rem', borderLeft: '2px solid var(--secondary)', background: 'rgba(188, 19, 254, 0.1)', fontSize: '0.8rem' }}>
                            <span style={{ color: 'var(--secondary)', fontWeight: 'bold' }}>DECRYPTED_INTEL:</span> {challenge.intel}
                        </div>
                    )}
                </div>
            </div>

            {status === 'COMPLETED' ? (
                <div style={{ textAlign: 'center', padding: '2rem', background: 'rgba(57, 255, 20, 0.1)', border: '1px solid var(--status-success)', borderRadius: '4px' }}>
                    <h1 style={{ color: 'var(--status-success)', marginBottom: '1rem' }}>QUEST_COMPLETE</h1>
                    <div style={{ fontSize: '1.2rem', marginBottom: '1rem' }}>{result.message}</div>
                    <button onClick={onBack}>RETURN_TO_BASE</button>
                </div>
            ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', alignItems: 'center' }}>
                    <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', textAlign: 'center' }}>
                        USE THE TERMINAL TO FIX THE CODE, THEN CLICK VERIFY
                        <br />
                        <code>python dojo_verify.py {projectId}</code>
                    </div>

                    <div style={{ display: 'flex', gap: '1rem' }}>
                        <button
                            className="pink-glow"
                            style={{ padding: '1rem 3rem', fontSize: '1rem' }}
                            onClick={handleVerify}
                            disabled={status === 'VERIFYING'}
                        >
                            {status === 'VERIFYING' ? 'VERIFYING...' : 'SUBMIT_FIX'}
                        </button>
                        <button
                            style={{ background: 'transparent', border: '1px solid #444' }}
                            onClick={onBack}
                        >
                            ABORT_MISSION
                        </button>
                    </div>

                    {status === 'FAILED' && (
                        <div style={{ color: 'var(--status-error)', fontSize: '0.85rem', marginTop: '1rem' }}>
                            SCAN_FAILED: {result?.error || 'Logic bug still present.'}
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};

export default DojoView;
