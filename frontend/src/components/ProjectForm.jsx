import React, { useState } from 'react';

function ProjectForm({ onSubmit, isLoading }) {
  const [projectName, setProjectName] = useState('');
  const [goal, setGoal] = useState('');
  const [techStack, setTechStack] = useState('Python');
  const [styleGuide, setStyleGuide] = useState('');
  const [specConstraints, setSpecConstraints] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!projectName || !goal) return;

    onSubmit({
      project_name: projectName,
      goal: goal,
      tech_stack: techStack.split(',').map(s => s.trim()),
      style_guide: styleGuide,
      spec_constraints: specConstraints
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

        <details style={{ marginTop: '0.5rem' }}>
          <summary style={{ fontSize: '0.75rem', color: 'var(--text-pink)', cursor: 'pointer', fontWeight: 'bold' }}>
            ADVANCED_CONSTRAINTS // [PHASE_3]
          </summary>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', marginTop: '1rem', padding: '1rem', border: '1px solid #222' }}>
            <div>
              <label style={{ fontSize: '0.65rem' }}>STYLE_GUIDE_PREFS</label>
              <textarea
                placeholder="e.g. Use CamelCase for all functions, No comments allowed..."
                value={styleGuide}
                onChange={(e) => setStyleGuide(e.target.value)}
                rows={2}
                style={{ fontSize: '0.8rem' }}
              />
            </div>
            <div>
              <label style={{ fontSize: '0.65rem' }}>ARCHITECTURAL_CONSTRAINTS</label>
              <textarea
                placeholder="e.g. Use Repository Pattern, Minimal dependencies..."
                value={specConstraints}
                onChange={(e) => setSpecConstraints(e.target.value)}
                rows={2}
                style={{ fontSize: '0.8rem' }}
              />
            </div>
          </div>
        </details>

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
