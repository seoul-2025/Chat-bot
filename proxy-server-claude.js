import express from 'express';
import cors from 'cors';
import fetch from 'node-fetch';
import dotenv from 'dotenv';

dotenv.config({ path: '.env.local' });

const app = express();
const PORT = 5000;

const CLAUDE_API_KEY = process.env.VITE_CLAUDE_API_KEY;

console.log('🔑 API 키 확인:', CLAUDE_API_KEY ? `${CLAUDE_API_KEY.substring(0, 20)}...` : '없음');

if (!CLAUDE_API_KEY) {
  console.error('❌ CLAUDE API 키가 설정되지 않았습니다. .env.local 파일을 확인해주세요.');
  process.exit(1);
}

app.use(cors());
app.use(express.json());

app.get('/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

app.post('/api/claude/chat', async (req, res) => {
  try {
    const { message, model } = req.body;
    const selectedModel = model || 'claude-opus-4-5-20251101';
    
    console.log(`🤖 Claude API 호출 - 모델: ${selectedModel}, 메시지 길이: ${message?.length || 0}`);
    
    const response = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': CLAUDE_API_KEY,
        'anthropic-version': '2023-06-01'
      },
      body: JSON.stringify({
        model: selectedModel,
        max_tokens: 4000,
        stream: true,
        messages: [{ role: 'user', content: message }]
      })
    });

    if (!response.ok) {
      const error = await response.text();
      return res.status(response.status).send(error);
    }

    res.setHeader('Content-Type', 'text/plain');
    res.setHeader('Transfer-Encoding', 'chunked');

    response.body.pipe(res);
  } catch (error) {
    console.error('프록시 오류:', error);
    res.status(500).json({ error: error.message });
  }
});

app.listen(PORT, '127.0.0.1', () => {
  console.log(`Claude 프록시 서버가 http://127.0.0.1:${PORT}에서 실행 중입니다.`);
});