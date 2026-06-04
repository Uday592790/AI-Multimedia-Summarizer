import axios from 'axios';
import { API_BASE_URL } from '../config';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const getErrorMessage = (error, fallback = 'Request failed. Please try again.') => {
  const detail = error?.response?.data?.detail ?? error?.response?.data?.error;
  if (typeof detail === 'string') return detail;
  if (Array.isArray(detail)) return detail.map((item) => item.msg ?? String(item)).join(', ');
  return error?.message || fallback;
};

export const uploadFile = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  const response = await api.post('/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  const data = response.data;
  return {
    transcription: data.text ?? '',
    file_path: data.file_path,
  };
};

export const generateSummary = async (transcription) => {
  const response = await api.post('/summarize', { text: transcription });
  const data = response.data;
  return { summary: data.summary ?? '' };
};

export const evaluateSummary = async (original, summary) => {
  const response = await api.post('/evaluate', {
    source_text: original,
    summary_text: summary,
  });
  const data = response.data;
  const m = data.metrics ?? {};
  const mapped = {
    bertscore:
      m.precision !== undefined && m.recall !== undefined && m.f1_score !== undefined
        ? {
            precision: m.precision,
            recall: m.recall,
            f1: m.f1_score,
          }
        : undefined,
    ...m,
  };
  return mapped;
};

export const semanticSearch = async (query, transcription) => {
  const response = await api.post('/search', {
    query,
    text: transcription,
  });
  const data = response.data;
  const results = (data.results ?? []).map((r) => ({
    sentence: r.text,
    score: r.score,
  }));
  return results;
};

export const translateText = async (text, targetLanguage) => {
  const response = await api.post('/translate', {
    text,
    target_language: targetLanguage,
  });
  return response.data;
};

export const generateAudioSummary = async (summary) => {
  const response = await api.post('/tts', { text: summary });
  const data = response.data;
  const audio_url = data.audio_url?.startsWith('/')
    ? `${API_BASE_URL}${data.audio_url}`
    : data.audio_url;
  return { ...data, audio_url };
};
