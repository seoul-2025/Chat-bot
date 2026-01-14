import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "path";

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
      "@features": path.resolve(__dirname, "./src/features"),
      "@shared": path.resolve(__dirname, "./src/shared"),
      "@core": path.resolve(__dirname, "./src/core"),
    },
  },

  build: {
    outDir: "dist",
    sourcemap: true,
    // 번들 최적화
    rollupOptions: {
      output: {
        // 코드 스플리팅 개선
        manualChunks: {
          'react-vendor': ['react', 'react-dom', 'react-router-dom'],
          'ui-vendor': ['framer-motion', 'clsx', 'react-hot-toast'],
          'chart-vendor': ['recharts'],
          'markdown-vendor': ['react-markdown', 'remark-gfm'],
        },
      },
    },
    // 청크 크기 경고 제한 증가
    chunkSizeWarningLimit: 1000,
  },
  // 개발 및 프리뷰 서버에서 라우팅 지원
  server: {
    port: 3005,
    strictPort: true,
    host: '0.0.0.0',
    historyApiFallback: true,
    proxy: {
      '/api/anthropic': {
        target: 'https://api.anthropic.com',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/anthropic/, ''),
        configure: (proxy, options) => {
          proxy.on('proxyReq', (proxyReq, req, res) => {
            proxyReq.setHeader('x-api-key', process.env.VITE_CLAUDE_API_KEY || '');
            proxyReq.setHeader('anthropic-version', '2023-06-01');
          });
        }
      }
    }
  },
  preview: {
    port: 3000,
    historyApiFallback: true,
  },
});
