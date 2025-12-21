import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  build: {
    outDir: 'dist-chat',
    rollupOptions: {
      input: './chat-only.html'
    }
  },
  server: {
    port: 3003
  }
})