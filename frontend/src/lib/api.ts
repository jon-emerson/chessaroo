// API configuration utility
export const getApiUrl = () => {
  // In browser environment
  if (typeof window !== 'undefined') {
    // Development - use localhost:8000
    if (window.location.hostname === 'localhost') {
      return 'http://localhost:8000';
    }
    // Production - use same host as frontend (ALB routes to same container)
    return `${window.location.protocol}//${window.location.hostname}`;
  }

  // Server-side - use environment variable or fallback
  return process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
};

export const apiCall = async (endpoint: string, options?: RequestInit) => {
  const baseUrl = getApiUrl();
  const url = `${baseUrl}${endpoint}`;

  const response = await fetch(url, {
    credentials: 'include', // Include cookies for session management
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ error: response.statusText }));
    throw new Error(errorData.error || `API call failed: ${response.statusText}`);
  }

  return response.json();
};