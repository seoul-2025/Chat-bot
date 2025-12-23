// Lambda용 Express 서버 핸들러
import serverlessExpress from '@vendia/serverless-express';
import express from 'express';
import cors from 'cors';
import fetch from 'node-fetch';

const app = express();

// CORS 설정
app.use(cors({
  origin: '*',
  credentials: true
}));

app.use(express.json({ limit: '50mb' }));

// Claude API 프록시 엔드포인트
app.post('/api/claude/chat', async (req, res) => {
  try {
    const { message, apiKey } = req.body;

    const claudeApiKey = apiKey || process.env.CLAUDE_API_KEY;
    if (!claudeApiKey) {
      return res.status(400).json({ error: 'API 키가 필요합니다.' });
    }

    console.log('🤖 Claude API 요청:', { messageLength: message.length });

    const response = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': claudeApiKey,
        'anthropic-version': '2023-06-01'
      },
      body: JSON.stringify({
        model: 'claude-3-5-sonnet-20241022',
        max_tokens: 4000,
        messages: [
          {
            role: 'user',
            content: message
          }
        ],
        stream: false // Lambda에서는 스트리밍 비활성화
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

    const data = await response.json();
    res.json(data);

  } catch (error) {
    console.error('프록시 서버 오류:', error);
    res.status(500).json({ 
      error: '서버 오류가 발생했습니다.',
      details: error.message
    });
  }
});

// 사용량 조회 엔드포인트
app.get('/usage/:userId/:engineType', (req, res) => {
  const { userId, engineType } = req.params;
  
  const usageData = {
    success: true,
    data: {
      totalTokens: engineType === '11' ? 2500 : 1500,
      inputTokens: engineType === '11' ? 1200 : 800,
      outputTokens: engineType === '11' ? 1300 : 700,
      messageCount: engineType === '11' ? 25 : 15,
      lastUsedAt: new Date().toISOString()
    }
  };
  
  res.json(usageData);
});

// 사용량 업데이트 엔드포인트
app.post('/usage/update', (req, res) => {
  const { userId, engineType, inputText, outputText } = req.body;
  
  const result = {
    success: true,
    tokensUsed: (inputText?.length || 0) + (outputText?.length || 0),
    percentage: Math.floor(Math.random() * 30) + 10,
    remaining: 7500
  };
  
  res.json(result);
});

// 프롬프트 조회 엔드포인트
app.get('/prompts/:engineType', (req, res) => {
  const { engineType } = req.params;
  
  const promptData = {
    engineType,
    description: `${engineType} 엔진 전용 AI 어시스턴트`,
    instructions: `${engineType} 엔진에 맞는 전문적인 답변을 제공해주세요.`,
    files: []
  };
  
  res.json(promptData);
});

// 프롬프트 파일 목록 조회 엔드포인트
app.get('/prompts/:engineType/files', (req, res) => {
  const filesData = {
    files: []
  };
  
  res.json(filesData);
});

// Lambda 핸들러
export const handler = serverlessExpress({ app });