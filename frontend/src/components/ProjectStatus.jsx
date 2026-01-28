import React from 'react';

function ProjectStatus({ status }) {
  return (
    <div>
      <h2>Project Status:</h2>
      <p>{status}</p>
    </div>
  );
}

export default ProjectStatus;
