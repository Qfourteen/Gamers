import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { resolve } from 'path';

export default defineConfig({
  plugins: [react()],
  root: '.', // frontend 디렉토리가 root
  build: {
    outDir: '../backend/static', // 빌드 결과물이 백엔드 static 폴더로
    emptyOutDir: true,
    rollupOptions: {
      input: {
        // 필요에 따라 여러 개 입력 가능
        main: resolve(__dirname, 'index.html'),
        reactMount: resolve(__dirname, 'react/mountHome.jsx'),
      },
      output: {
        entryFileNames: 'js/[name].js',
        chunkFileNames: 'js/[name]-[hash].js',
        assetFileNames: 'assets/[name]-[hash][extname]'
      }
    }
  }
});
