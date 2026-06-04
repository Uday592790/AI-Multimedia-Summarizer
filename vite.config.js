import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/upload': 'http://localhost:8000',
      '/summarize': 'http://localhost:8000',
      '/evaluate': 'http://localhost:8000',
      '/search': 'http://localhost:8000',
      '/translate': 'http://localhost:8000',
      '/tts': 'http://localhost:8000',
      '/audio': 'http://localhost:8000',
      '/health': 'http://localhost:8000',
      '/lda_compare': 'http://localhost:8000',
    },
  },
});
