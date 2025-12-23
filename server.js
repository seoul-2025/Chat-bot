// Claude API 프록시 서버 (Anthropic API 사용)
import express from 'express';
import cors from 'cors';
import fetch from 'node-fetch';

const app = express();
const PORT = process.env.PORT || 3001;

// CORS 설정 - 프로덕션 모드
app.use(cors({
  origin: process.env.NODE_ENV === 'production' 
    ? ['https://d1234567890.cloudfront.net', 'https://your-domain.com']
    : 'http://localhost:3002',
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

    console.log('🤖 Claude 4.5 Opus API 요청:', { messageLength: message.length });

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

    // 스트리밍 응답 처리
    res.writeHead(200, {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache',
      'Connection': 'keep-alive',
      'Access-Control-Allow-Origin': '*'
    });

    let buffer = '';
    
    response.body.on('data', (chunk) => {
      buffer += chunk.toString();
      const lines = buffer.split('\n');
      buffer = lines.pop() || '';
      
      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = line.slice(6);
          if (data === '[DONE]') {
            res.write('data: [DONE]\n\n');
            res.end();
            return;
          }
          try {
            const parsed = JSON.parse(data);
            if (parsed.delta?.text) {
              res.write(`data: ${JSON.stringify({ content: parsed.delta.text })}\n\n`);
            }
          } catch (e) {
            // 파싱 오류 무시
          }
        }
      }
    });

    response.body.on('end', () => {
      res.write('data: [DONE]\n\n');
      res.end();
    });

    response.body.on('error', (error) => {
      console.error('스트리밍 오류:', error);
      res.write(`data: ${JSON.stringify({ error: error.message })}\n\n`);
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

// 사용량 조회 엔드포인트
app.get('/usage/:userId/:engineType', (req, res) => {
  try {
    const { userId, engineType } = req.params;
    console.log('📊 사용량 조회 요청:', { userId, engineType });
    
    // 테스트용 더미 데이터
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
    
    console.log('📊 사용량 응답:', usageData);
    res.json(usageData);
  } catch (error) {
    console.error('사용량 조회 오류:', error);
    res.status(500).json({ 
      success: false,
      error: '사용량 조회 중 오류 발생' 
    });
  }
});

// 사용량 업데이트 엔드포인트
app.post('/usage/update', (req, res) => {
  try {
    const { userId, engineType, inputText, outputText } = req.body;
    
    // 테스트용 응답
    const result = {
      success: true,
      tokensUsed: (inputText?.length || 0) + (outputText?.length || 0),
      percentage: Math.floor(Math.random() * 30) + 10, // 10-40% 랜덤
      remaining: 7500
    };
    
    res.json(result);
  } catch (error) {
    res.status(500).json({ 
      success: false,
      error: '사용량 업데이트 중 오류 발생' 
    });
  }
});

// 프롬프트 조회 엔드포인트
app.get('/prompts/:engineType', (req, res) => {
  try {
    const { engineType } = req.params;
    console.log('📝 프롬프트 조회 요청:', { engineType });
    
    // 테스트용 더미 데이터
    const promptData = {
      engineType,
      description: `${engineType} 엔진 전용 AI 어시스턴트`,
      instructions: `${engineType} 엔진에 맞는 전문적인 답변을 제공해주세요.`,
      files: []
    };
    
    console.log('📝 프롬프트 응답:', promptData);
    res.json(promptData);
  } catch (error) {
    console.error('프롬프트 조회 오류:', error);
    res.status(500).json({ 
      error: '프롬프트 조회 중 오류 발생' 
    });
  }
});

// 프롬프트 파일 목록 조회 엔드포인트
app.get('/prompts/:engineType/files', (req, res) => {
  try {
    const { engineType } = req.params;
    console.log('📁 프롬프트 파일 목록 요청:', { engineType });
    
    // 테스트용 빈 배열
    const filesData = {
      files: []
    };
    
    console.log('📁 파일 목록 응답:', filesData);
    res.json(filesData);
  } catch (error) {
    console.error('파일 목록 조회 오류:', error);
    res.status(500).json({ 
      error: '파일 목록 조회 중 오류 발생' 
    });
  }
});

// 서버 시작
app.listen(PORT, () => {
  console.log(`🚀 Claude API 프록시 서버가 http://localhost:${PORT} 에서 실행 중입니다.`);
});