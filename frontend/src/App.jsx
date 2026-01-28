import React, { useState, useEffect } from 'react';
import ProjectForm from './components/ProjectForm';
import AgentConsole from './components/AgentConsole';
import CodeViewer from './components/CodeViewer';
import { createProject, getProjectStatus } from './services/api';

function App() {
  const [projectId, setProjectId] = useState(null);
  const [projectState, setProjectState] = useState(null);
  const [logs, setLogs] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    let interval;
    if (projectId && (!projectState || projectState.status !== 'completed' && projectState.status !== 'failed')) {
      interval = setInterval(async () => {
        try {
          const data = await getProjectStatus(projectId);
          setProjectState(data);
          if (data.logs) setLogs(data.logs);
        } catch (error) {
          console.error('Error polling status:', error);
        }
      }, 2000);
    }
    return () => clearInterval(interval);
  }, [projectId, projectState]);

  const handleCreateProject = async (projectData) => {
    setIsLoading(true);
    setLogs([{ type: 'info', message: 'CONNECTING_TO_AGENTS...', timestamp: new Date().toISOString() }]);
    try {
      const data = await createProject(projectData);
      setProjectId(data.project_id);
      setIsLoading(false);
    } catch (error) {
      console.error('Failed to create project:', error);
      setLogs(prev => [...prev, { type: 'error', message: 'CRITICAL_SYSTEM_LINK_FAILURE', timestamp: new Date().toISOString() }]);
      setIsLoading(false);
    }
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <nav style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        padding: '1rem 0',
        borderBottom: '1px solid var(--border-dim)',
        marginBottom: '2rem'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <div style={{
            width: '32px',
            height: '32px',
            background: 'var(--primary)',
            borderRadius: '4px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontWeight: 'bold',
            color: 'black'
          }}>A</div>
          <h2 style={{ fontSize: '1rem', margin: 0 }}>
            AUTONOMOUS_PARTNER <span style={{ color: 'var(--text-muted)', fontWeight: '400' }}>v2.0.4</span>
          </h2>
        </div>
        <div style={{ display: 'flex', gap: '2rem', fontSize: '0.8rem', fontWeight: 'bold' }}>
          <span className="pink-glow" style={{ cursor: 'pointer' }}>DASHBOARD</span>
          <span style={{ color: 'var(--text-muted)', cursor: 'pointer' }}>PROJECTS</span>
          <span style={{ color: 'var(--text-muted)', cursor: 'pointer' }}>SETTINGS</span>
        </div>
      </nav>

      <main style={{
        flex: 1,
        display: 'grid',
        gridTemplateColumns: projectId ? '450px 1fr' : '1fr',
        gap: '3rem',
        alignItems: 'start'
      }}>
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: projectId ? 'flex-start' : 'center' }}>
          {!projectId ? (
            <ProjectForm onSubmit={handleCreateProject} isLoading={isLoading} />
          ) : (
            <div className="ide-panel" style={{ width: '100%', padding: '2rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1.5rem' }}>
                <span style={{ color: 'var(--text-pink)', fontSize: '0.75rem', fontWeight: 'bold' }}>PROJECT_STATUS</span>
                <span style={{
                  color: projectState?.status === 'completed' ? 'var(--status-success)' : 'var(--status-info)',
                  fontSize: '0.75rem',
                  fontWeight: 'bold'
                }}>
                  [{projectState?.status?.toUpperCase() || 'BUSY'}]
                </span>
              </div>
              <h2 style={{ fontSize: '1.5rem', marginBottom: '1rem' }}>{projectState?.project_name}</h2>
              <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', height: '100px', overflowY: 'auto' }}>
                {projectState?.goal}
              </div>

              <div style={{ marginTop: '2rem', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.7rem' }}>
                  <span>PLANNING</span>
                  <span>100%</span>
                </div>
                <div style={{ height: '4px', background: '#222' }}>
                  <div style={{ height: '100%', width: '100%', background: 'var(--primary)' }}></div>
                </div>
              </div>

              <button
                onClick={() => setProjectId(null)}
                style={{ marginTop: '2rem', width: '100%', fontSize: '0.8rem', padding: '0.6rem' }}
              >
                CREATE_NEW_SESSION
              </button>
            </div>
          )}
        </div>

        {projectId && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
            <AgentConsole logs={logs} />
            <CodeViewer files={projectState?.files || []} />
          </div>
        )}
      </main>

      <footer style={{
        marginTop: 'auto',
        padding: '2rem 0',
        borderTop: '1px solid var(--border-dim)',
        display: 'flex',
        justifyContent: 'space-between',
        fontSize: '0.75rem',
        color: var(--text-muted)
      }}>
      <span>CORE_ENGINE: LLAMA_3.3_70B</span>
      <span>SYSTEM_STATUS: <span style={{ color: 'var(--status-success)' }}>ONLINE</span></span>
    </footer>
    </div >
  );
}

export default App;
