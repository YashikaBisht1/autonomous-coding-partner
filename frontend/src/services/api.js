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

export const listProjects = async () => {
  const response = await fetch(`${API_URL}/projects`);
  return response.json();
};

export const getConfig = async () => {
  const response = await fetch(`${API_URL}/config`);
  return response.json();
};
export const analyzeProject = async (projectId) => {
  const response = await fetch(`${API_URL}/projects/${projectId}/analyze`, {
    method: 'POST',
  });
  return response.json();
};
export const startDojoChallenge = async (projectId) => {
  const response = await fetch(`${API_URL}/projects/${projectId}/dojo/challenge`, {
    method: 'POST',
  });
  return response.json();
};

export const verifyDojoChallenge = async (projectId) => {
  const response = await fetch(`${API_URL}/projects/${projectId}/dojo/verify`, {
    method: 'POST',
  });
  return response.json();
};
