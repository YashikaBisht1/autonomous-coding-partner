import React from 'react';

function CodeViewer({ code }) {
  return (
    <pre>
      <code>{code}</code>
    </pre>
  );
}

export default CodeViewer;
