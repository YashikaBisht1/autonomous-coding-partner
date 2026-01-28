import React, { useState, useEffect } from 'react';
import ProjectForm from './components/ProjectForm';
import AgentConsole from './components/AgentConsole';
import CodeViewer from './components/CodeViewer';
import { createProject, getProjectStatus, listProjects, getConfig } from './services/api';

function App() {
  const [projectId, setProjectId] = useState(null);
  const [projectState, setProjectState] = useState(null);
  const [logs, setLogs] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [currentView, setCurrentView] = useState('DASHBOARD');
  const [projects, setProjects] = useState([]);
  const [config, setConfig] = useState(null);
  const [isFetching, setIsFetching] = useState(false);

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

  useEffect(() => {
    if (currentView === 'PROJECTS') {
      const fetchProjects = async () => {
        setIsFetching(true);
        try {
          const data = await listProjects();
          setProjects(data);
        } catch (error) {
          console.error('Error fetching projects:', error);
        } finally {
          setIsFetching(false);
        }
      };
      fetchProjects();
    }
    if (currentView === 'SETTINGS') {
      const fetchConfig = async () => {
        setIsFetching(true);
        try {
          const data = await getConfig();
          setConfig(data);
        } catch (error) {
          console.error('Error fetching config:', error);
        } finally {
          setIsFetching(false);
        }
      };
      fetchConfig();
    }
  }, [currentView]);

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

  const renderDashboard = () => (
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
  );

  const renderProjects = () => (
    <div className="ide-panel animate-fade-in" style={{ padding: '2rem', width: '100%', maxWidth: '900px', margin: '0 auto' }}>
      <div style={{ marginBottom: '2rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h2 className="pink-glow" style={{ fontSize: '1.2rem' }}>PROJECT_ARCHIVE</h2>
        <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>{projects.length} PROJECTS_FOUND</span>
      </div>

      {isFetching ? (
        <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-muted)' }}>ACCESSING_ARCHIVE...</div>
      ) : projects.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-muted)' }}>NO_PROJECTS_INITIALIZED</div>
      ) : (
        <div style={{ display: 'grid', gap: '1rem' }}>
          {projects.map((p) => (
            <div key={p.project_id} style={{
              padding: '1rem',
              background: 'var(--bg-input)',
              border: '1px solid var(--border-dim)',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              cursor: 'pointer'
            }}
              onClick={() => {
                setProjectId(p.project_id);
                setCurrentView('DASHBOARD');
              }}
            >
              <div>
                <div style={{ fontWeight: 'bold', color: 'var(--primary)' }}>{p.project_name}</div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>ID: {p.project_id} // CREATED: {new Date(p.created_at).toLocaleString()}</div>
              </div>
              <button style={{ fontSize: '0.7rem', padding: '0.4rem 0.8rem' }}>OPEN_SESSION</button>
            </div>
          ))}
        </div>
      )}
    </div>
  );

  const renderSettings = () => (
    <div className="ide-panel animate-fade-in" style={{ padding: '2rem', width: '100%', maxWidth: '700px', margin: '0 auto' }}>
      <h2 className="pink-glow" style={{ fontSize: '1.2rem', marginBottom: '2rem' }}>SYSTEM_CONFIG</h2>

      {isFetching || !config ? (
        <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-muted)' }}>RETRIEVING_PARAMETERS...</div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          {Object.entries(config).map(([key, value]) => (
            <div key={key} style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid #222', paddingBottom: '0.5rem' }}>
              <span style={{ color: 'var(--text-pink)', fontSize: '0.8rem', fontWeight: 'bold' }}>{key.toUpperCase()}</span>
              <span style={{ fontSize: '0.8rem', color: 'var(--text-main)', fontFamily: 'monospace' }}>
                {Array.isArray(value) ? value.join(', ') : value}
              </span>
            </div>
          ))}
          <div style={{ marginTop: '2rem', padding: '1rem', border: '1px dashed var(--primary)', borderRadius: '4px', background: 'rgba(255, 0, 127, 0.05)' }}>
            <div style={{ fontSize: '0.7rem', color: 'var(--primary)', fontWeight: 'bold', marginBottom: '0.5rem' }}>SECURITY_NOTICE</div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
              Agent parameters are locked for this session. Direct modification requires LEVEL_5 clearance.
            </div>
          </div>
        </div>
      )}
    </div>
  );

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
          <span
            className={currentView === 'DASHBOARD' ? "pink-glow" : ""}
            style={{ cursor: 'pointer', color: currentView === 'DASHBOARD' ? 'var(--primary)' : 'var(--text-muted)' }}
            onClick={() => setCurrentView('DASHBOARD')}
          >
            DASHBOARD
          </span>
          <span
            className={currentView === 'PROJECTS' ? "pink-glow" : ""}
            style={{ cursor: 'pointer', color: currentView === 'PROJECTS' ? 'var(--primary)' : 'var(--text-muted)' }}
            onClick={() => setCurrentView('PROJECTS')}
          >
            PROJECTS
          </span>
          <span
            className={currentView === 'SETTINGS' ? "pink-glow" : ""}
            style={{ cursor: 'pointer', color: currentView === 'SETTINGS' ? 'var(--primary)' : 'var(--text-muted)' }}
            onClick={() => setCurrentView('SETTINGS')}
          >
            SETTINGS
          </span>
        </div>
      </nav>

      {currentView === 'DASHBOARD' && renderDashboard()}
      {currentView === 'PROJECTS' && renderProjects()}
      {currentView === 'SETTINGS' && renderSettings()}

      <footer style={{
        marginTop: 'auto',
        padding: '2rem 0',
        borderTop: '1px solid var(--border-dim)',
        display: 'flex',
        justifyContent: 'space-between',
        fontSize: '0.75rem',
        color: 'var(--text-muted)'
      }}>
        <span>CORE_ENGINE: LLAMA_3.3_70B</span>
        <span>SYSTEM_STATUS: <span style={{ color: 'var(--status-success)' }}>ONLINE</span></span>
      </footer>
    </div>
  );
}

export default App;
