import React from 'react';

function AgentConsole({ logs }) {
  return (
    <div className="agent-console">
      <h2>Agent Console:</h2>
      {logs.map((log, index) => (
        <p key={index}>{log}</p>
      ))}
    </div>
  );
}

export default AgentConsole;
