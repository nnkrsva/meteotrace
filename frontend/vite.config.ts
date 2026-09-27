/// <reference types="vitest/config" />
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api/v1/forecast': 'http://localhost:8002',
      '/api/v1/history': 'http://localhost:8003',
      '/api/v1/auth': 'http://localhost:8001',
    },
  },
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: ['./src/setupTests.ts'],
    coverage: { reporter: ['text'], thresholds: { lines: 75 }, include: ['src/**/*.{ts,tsx}'], exclude: ['src/main.tsx', 'src/setupTests.ts'] },
  },
});
