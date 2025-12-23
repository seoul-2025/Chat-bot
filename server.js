// 로컬 프록시 서버 (Claude API CORS 우회용)
import express from 'express';
import cors from 'cors';
import fetch from 'node-fetch';

const app = express();
const PORT = 3001;

// CORS 설정
app.use(cors({
  origin: 'http://localhost:3002',
  credentials: true
}));

app.use(express.json({ limit: '50mb' }));

// Claude API 프록시 엔드포인트
app.post('/api/claude/chat', async (req, res) => {
  try {
    const { message, apiKey } = req.body;

    if (!apiKey) {
      return res.status(400).json({ error: 'API 키가 필요합니다.' });
    }

    console.log('🤖 Claude API 프록시 요청:', { messageLength: message.length });

    const response = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': apiKey,
        'anthropic-version': '2023-06-01'
      },
      body: JSON.stringify({
        model: 'claude-opus-4-5-20251101', // 지정된 모델 사용
        max_tokens: 4000,
        messages: [
          {
            role: 'user',
            content: message
          }
        ],
        stream: true
      })
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error('Claude API 오류:', response.status, errorText);
      return res.status(response.status).json({ 
        error: `Claude API 오류: ${response.status}`,
        details: errorText
      });
    }

    // 스트리밍 응답을 클라이언트로 전달
    res.writeHead(200, {
      'Content-Type': 'text/plain; charset=utf-8',
      'Transfer-Encoding': 'chunked',
      'Cache-Control': 'no-cache',
      'Connection': 'keep-alive'
    });

    const reader = response.body;
    reader.on('data', (chunk) => {
      res.write(chunk);
    });

    reader.on('end', () => {
      res.end();
    });

    reader.on('error', (error) => {
      console.error('스트리밍 오류:', error);
      res.end();
    });

  } catch (error) {
    console.error('프록시 서버 오류:', error);
    res.status(500).json({ 
      error: '서버 오류가 발생했습니다.',
      details: error.message
    });
  }
});

// 서버 시작
app.listen(PORT, () => {
  console.log(`🚀 Claude API 프록시 서버가 http://localhost:${PORT} 에서 실행 중입니다.`);
});