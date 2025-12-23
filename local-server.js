import express from 'express';
import cors from 'cors';
import { WebSocketServer } from 'ws';
import http from 'http';

const app = express();
const server = http.createServer(app);
const wss = new WebSocketServer({ server });

app.use(cors());
app.use(express.json());

// 채팅 엔드포인트
app.post('/chat', async (req, res) => {
  try {
    const { message, engineType, conversationId } = req.body;
    
    // 프론트엔드가 기대하는 형식으로 응답
    res.json({
      success: true,
      message: `Echo: ${message} (Engine: ${engineType})`
    });
  } catch (error) {
    res.status(500).json({ 
      type: 'error',
      message: error.message 
    });
  }
});

// 대화 관련 API
app.get('/conversations', (req, res) => {
  res.json([]);
});

// 사용량 업데이트 엔드포인트
app.post('/usage/update', (req, res) => {
  const { userId, engineType, inputTokens, outputTokens } = req.body;
  console.log(`사용량 업데이트: ${userId}, ${engineType}, 입력:${inputTokens}, 출력:${outputTokens}`);
  res.json({ 
    success: true,
    percentage: Math.floor(Math.random() * 100),
    message: 'Usage updated successfully'
  });
});

// 엔진 상태 확인 엔드포인트
app.get('/:engineId', (req, res) => {
  const { engineId } = req.params;
  console.log(`엔진 상태 확인: ${engineId}`);
  res.json({ 
    status: 'active',
    engine: engineId,
    message: `Engine ${engineId} is ready`
  });
});

app.post('/conversations', (req, res) => {
  const { title } = req.body;
  res.json({ 
    id: Date.now().toString(), 
    title: title || 'New Chat',
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString()
  });
});

app.patch('/conversations/:id', (req, res) => {
  const { id } = req.params;
  const { title } = req.body;
  res.json({ 
    id: id, 
    title: title,
    updated_at: new Date().toISOString()
  });
});

app.delete('/conversations/:id', (req, res) => {
  const { id } = req.params;
  res.json({ success: true, id: id });
});

// WebSocket 연결
wss.on('connection', (ws, req) => {
  console.log('WebSocket 연결됨');
  
  // JWT 인증 시뮬레이션
  const token = req.headers.authorization || req.url.split('token=')[1];
  if (!token) {
    ws.close(1008, 'Authentication required');
    return;
  }
  
  ws.on('message', async (message) => {
    try {
      const data = JSON.parse(message.toString());
      console.log('받은 메시지:', data);
      
      if (data.type === 'chat_message') {
        // AI 시작 신호
        ws.send(JSON.stringify({
          type: 'ai_start',
          timestamp: new Date().toISOString()
        }));
        
        // Bedrock Claude 모델 시뮬레이션
        const response = await simulateClaudeResponse(data.message, data.engineType);
        
        // 스트리밍 응답
        for (let i = 0; i < response.chunks.length; i++) {
          setTimeout(() => {
            ws.send(JSON.stringify({
              type: 'ai_chunk',
              chunk: response.chunks[i],
              chunk_index: i
            }));
          }, i * 50);
        }
        
        // 완료 신호
        setTimeout(() => {
          ws.send(JSON.stringify({
            type: 'chat_end',
            total_chunks: response.chunks.length,
            engine: data.engineType,
            conversationId: data.conversationId
          }));
        }, response.chunks.length * 50 + 100);
      }
    } catch (error) {
      console.error('WebSocket 메시지 처리 오류:', error);
      ws.send(JSON.stringify({
        type: 'error',
        message: error.message
      }));
    }
  });
  
  ws.on('close', () => {
    console.log('WebSocket 연결 종료');
  });
});

// Claude 모델 시뮬레이션
async function simulateClaudeResponse(message, engineType) {
  const responses = {
    '11': `[Claude Opus 4.1] 기업 보도자료 전문 분석\n\n입력된 내용: "${message}"\n\n하이라이트:\n• 핵심 비즈니스 인사이트 추출\n• 시장 영향도 분석\n• 투자자 관점 정리\n\n기사 작성 방향 제안을 위해 추가 정보가 필요하시면 말씀해 주세요.`,
    '12': `[Claude Opus 4.1] 정부/공공기관 보도자료 전문 분석\n\n입력된 내용: "${message}"\n\n주요 분석 포인트:\n• 정책 변화 영향도\n• 국민 생활 연관성\n• 예산 및 시행 일정\n\n전문적인 기사 작성을 위한 추가 질문이 있으시면 언제든 말씀해 주세요.`
  };
  
  const responseText = responses[engineType] || `[Claude Opus 4.1] AI 전문 분석: ${message}`;
  const chunks = responseText.split(' ').map(word => word + ' ');
  
  return { chunks };
}

const PORT = 8080;
server.listen(PORT, (err) => {
  if (err) {
    console.error('서버 시작 실패:', err);
    return;
  }
  console.log(`로컬 서버가 http://localhost:${PORT}에서 실행 중입니다`);
});