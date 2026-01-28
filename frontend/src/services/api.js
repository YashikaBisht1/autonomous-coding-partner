const API_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000/api';

export const createProject = async (projectData) => {
  const response = await fetch(`${API_URL}/projects`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(projectData),
  });
  return response.json();
};

export const getProjectStatus = async (projectId) => {
  const response = await fetch(`${API_URL}/projects/${projectId}`);
  return response.json();
};
