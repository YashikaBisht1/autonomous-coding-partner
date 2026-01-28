import React, { useState } from 'react';

function ProjectForm({ onSubmit, isLoading }) {
  const [projectName, setProjectName] = useState('');
  const [goal, setGoal] = useState('');
  const [techStack, setTechStack] = useState('Python');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!projectName || !goal) return;

    onSubmit({
      project_name: projectName,
      goal: goal,
      tech_stack: techStack.split(',').map(s => s.trim())
    });
  };

  return (
    <div className="ide-panel" style={{ width: '100%', maxWidth: '650px', padding: '2.5rem', marginTop: '1rem' }}>
      <div style={{ marginBottom: '2rem' }}>
        <h2 className="pink-glow" style={{ fontSize: '1.2rem', marginBottom: '0.5rem' }}>NEW_DEB_SESSION</h2>
        <div style={{ height: '2px', width: '60px', background: 'var(--primary)' }}></div>
      </div>

      <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1.75rem' }}>
        <div>
          <label>Project // ID</label>
          <input
            type="text"
            placeholder="SYSTEM_CALC_V1"
            value={projectName}
            onChange={(e) => setProjectName(e.target.value)}
            required
          />
        </div>

        <div>
          <label>Mission // Objective</label>
          <textarea
            placeholder="Enter mission parameters and goals..."
            value={goal}
            onChange={(e) => setGoal(e.target.value)}
            required
            rows={5}
          />
        </div>

        <div>
          <label>Protocol // Stack</label>
          <input
            type="text"
            placeholder="PYTHON, FASTAPI, OPENAI"
            value={techStack}
            onChange={(e) => setTechStack(e.target.value)}
          />
        </div>

        <div style={{ marginTop: '1rem' }}>
          <button type="submit" disabled={isLoading} style={{ width: '100%' }}>
            {isLoading ? 'EXECUTING_PROTOCOL...' : 'BOOT_AGENTS.EXE'}
          </button>
        </div>
      </form>
    </div>
  );
}

export default ProjectForm;
