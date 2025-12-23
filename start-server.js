import { createServer } from 'vite';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

async function startServer() {
  try {
    const server = await createServer({
      configFile: path.resolve(__dirname, 'vite.config.js'),
      server: {
        port: 3002,
        host: '127.0.0.1'
      }
    });
    
    await server.listen();
    console.log('Server running at http://127.0.0.1:3002');
  } catch (error) {
    console.error('Failed to start server:', error);
    
    // 대체 포트로 시도
    try {
      const server = await createServer({
        configFile: path.resolve(__dirname, 'vite.config.js'),
        server: {
          port: 3000,
          host: '127.0.0.1'
        }
      });
      
      await server.listen();
      console.log('Server running at http://127.0.0.1:3000');
    } catch (err) {
      console.error('Failed to start on alternative port:', err);
    }
  }
}

startServer();