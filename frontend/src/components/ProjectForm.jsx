import React, { useState } from 'react';

function ProjectForm({ onSubmit }) {
  const [projectName, setProjectName] = useState('');
  const [projectDescription, setProjectDescription] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit({ name: projectName, description: projectDescription });
    setProjectName('');
    setProjectDescription('');
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="text"
        placeholder="Project Name"
        value={projectName}
        onChange={(e) => setProjectName(e.target.value)}
      />
      <textarea
        placeholder="Project Description"
        value={projectDescription}
        onChange={(e) => setProjectDescription(e.target.value)}
      ></textarea>
      <button type="submit">Create Project</button>
    </form>
  );
}

export default ProjectForm;
