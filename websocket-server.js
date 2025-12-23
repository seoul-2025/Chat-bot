import { WebSocketServer } from 'ws';
import { BedrockRuntimeClient, InvokeModelWithResponseStreamCommand } from '@aws-sdk/client-bedrock-runtime';
import dotenv from 'dotenv';

// .env 파일 로드
dotenv.config();

// AWS Bedrock 클라이언트 초기화
const bedrock = new BedrockRuntimeClient({
  region: 'us-east-1'
});

// WebSocket 서버 생성 - Windows 호환성을 위한 설정
const wss = new WebSocketServer({ 
  port: 3001,
  host: 'localhost'
});

console.log('🚀 WebSocket 서버가 ws://localhost:3001 에서 실행 중입니다.');

wss.on('connection', (ws) => {
  console.log('📱 클라이언트 연결됨');

  ws.on('message', async (data) => {
    try {
      const message = JSON.parse(data);
      console.log('📨 메시지 받음:', {
        action: message.action,
        engineType: message.engineType,
        messageLength: message.message?.length || 0
      });

      if (message.action === 'sendMessage') {
        await handleChatMessage(ws, message);
      }
    } catch (error) {
      console.error('메시지 처리 오류:', error);
      ws.send(JSON.stringify({
        type: 'error',
        message: '메시지 처리 중 오류가 발생했습니다.'
      }));
    }
  });

  ws.on('close', () => {
    console.log('📱 클라이언트 연결 종료');
  });
});

async function handleChatMessage(ws, message) {
  try {
    // AI 시작 신호
    ws.send(JSON.stringify({
      type: 'ai_start',
      timestamp: new Date().toISOString()
    }));

    // 엔진별 시스템 프롬프트
    const systemPrompts = {
      "11": "당신은 기업 보도자료 전문 분석가입니다. 기업의 보도자료를 분석하여 핵심 내용을 파악하고, 언론사에서 사용할 수 있는 기사 형태로 재작성해주세요.",
      "22": "당신은 정부/공공기관 보도자료 전문 분석가입니다. 정부 및 공공기관의 보도자료를 분석하여 핵심 내용을 파악하고, 언론사에서 사용할 수 있는 기사 형태로 재작성해주세요."
    };

    const systemPrompt = systemPrompts[message.engineType] || systemPrompts["11"];
    const fullMessage = `${systemPrompt}\n\n분석할 내용:\n${message.message}`;

    // Bedrock 스트리밍 호출
    const command = new InvokeModelWithResponseStreamCommand({
      modelId: 'us.anthropic.claude-opus-4-5-20251101-v1:0',
      body: JSON.stringify({
        anthropic_version: "bedrock-2023-05-31",
        max_tokens: 4000,
        messages: [
          {
            role: 'user',
            content: fullMessage
          }
        ]
      })
    });

    const response = await bedrock.send(command);
    let chunkIndex = 0;

    // 스트림 처리
    for await (const chunk of response.body) {
      if (chunk.chunk?.bytes) {
        const chunkData = JSON.parse(new TextDecoder().decode(chunk.chunk.bytes));
        
        if (chunkData.type === 'content_block_delta' && chunkData.delta?.text) {
          // 청크 전송
          ws.send(JSON.stringify({
            type: 'ai_chunk',
            chunk: chunkData.delta.text,
            chunk_index: chunkIndex
          }));
          chunkIndex++;
        }
      }
    }

    // 완료 신호
    ws.send(JSON.stringify({
      type: 'chat_end',
      total_chunks: chunkIndex,
      engine: message.engineType
    }));

  } catch (error) {
    console.error('Bedrock API 오류:', error);
    ws.send(JSON.stringify({
      type: 'error',
      message: `Bedrock API 오류: ${error.message}`
    }));
  }
}