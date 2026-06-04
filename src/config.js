// In development, call the FastAPI backend directly to avoid long upload/model-load proxy resets.
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
