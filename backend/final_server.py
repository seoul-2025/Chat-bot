"""
통합 WebSocket 서버 - Claude 서비스 포함
"""
import asyncio
import sys
import json
import websockets
import os
import sys
import logging
from datetime import datetime
import boto3

# Windows asyncio 문제 해결
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# AWS 설정
AWS_REGION = os.environ.get('AWS_REGION', 'us-east-1')
BEDROCK_CONFIG = {
    'region_name': AWS_REGION,
    'model_id': 'us.anthropic.claude-opus-4-5-20251101-v1:0',
    'max_tokens': int(os.environ.get('BEDROCK_MAX_TOKENS', '4000')),
    'temperature': float(os.environ.get('BEDROCK_TEMPERATURE', '0.7')),
    'top_p': float(os.environ.get('BEDROCK_TOP_P', '0.9')),
    'top_k': int(os.environ.get('BEDROCK_TOP_K', '50')),
    'anthropic_version': os.environ.get('ANTHROPIC_VERSION', 'bedrock-2023-05-31')
}

# Bedrock Runtime 클라이언트 초기화
bedrock_runtime = boto3.client('bedrock-runtime', region_name=AWS_REGION)

async def generate_claude_response(websocket, message, engine):
    """AWS Bedrock Claude 3.5 Sonnet을 사용한 AI 응답 생성 및 스트리밍"""
    
    print(f"=== AWS Bedrock Claude 서비스 시작 ===")
    print(f"Message: {message[:100]}...")
    print(f"Engine: {engine}")
    print(f"Model ID: {BEDROCK_CONFIG['model_id']}")
    
    try:
        # Bedrock 요청 본문 구성
        body = {
            "anthropic_version": BEDROCK_CONFIG['anthropic_version'],
            "max_tokens": BEDROCK_CONFIG['max_tokens'],
            "temperature": BEDROCK_CONFIG['temperature'],
            "messages": [{
                "role": "user",
                "content": message
            }],
            "top_k": BEDROCK_CONFIG['top_k'],
            "top_p": BEDROCK_CONFIG['top_p']
        }
        
        print(f"AWS Bedrock 요청 전송 중...")
        
        # Bedrock 스트리밍 호출
        response = bedrock_runtime.invoke_model_with_response_stream(
            modelId=BEDROCK_CONFIG['model_id'],
            body=json.dumps(body)
        )
        
        print(f"AWS Bedrock 응답 수신 시작")
        
        chunk_index = 0
        stream = response.get('body')
        
        if stream:
            for event in stream:
                chunk = event.get('chunk')
                if chunk:
                    chunk_obj = json.loads(chunk.get('bytes').decode())
                    print(f"Chunk type: {chunk_obj.get('type')}")
                    
                    if chunk_obj.get('type') == 'content_block_delta':
                        delta = chunk_obj.get('delta', {})
                        if delta.get('type') == 'text_delta':
                            text = delta.get('text', '')
                            if text:
                                print(f"Sending chunk {chunk_index}: {text[:50]}...")
                                await websocket.send(json.dumps({
                                    "type": "ai_chunk",
                                    "chunk": text,
                                    "chunk_index": chunk_index
                                }))
                                chunk_index += 1
                    
                    elif chunk_obj.get('type') == 'message_stop':
                        print("Message stop received")
                        break
        
        print(f"Total chunks sent: {chunk_index}")
        
        # 스트리밍 완료
        await websocket.send(json.dumps({
            "type": "chat_end",
            "total_chunks": chunk_index,
            "engine": engine
        }))
        
        print("=== AWS Bedrock Claude 서비스 완료 ===")
        
    except Exception as e:
        print(f"AWS Bedrock API 오류: {e}")
        print(f"Error type: {type(e)}")
        import traceback
        traceback.print_exc()
        
        await websocket.send(json.dumps({
            "type": "error",
            "message": f"AWS Bedrock AI 응답 생성 중 오류: {str(e)}"
        }))

async def handle_websocket(websocket, path):
    logger.info("New WebSocket connection")
    
    try:
        async for message in websocket:
            try:
                data = json.loads(message)
                action = data.get('action', 'sendMessage')
                
                if action == 'sendMessage':
                    user_message = data.get('message', '')
                    engine_type = data.get('engineType', 'claude')
                    
                    # AI 시작 알림
                    await websocket.send(json.dumps({
                        "type": "ai_start",
                        "timestamp": datetime.utcnow().isoformat() + 'Z'
                    }))
                    
                    # Claude 응답 생성
                    await generate_claude_response(websocket, user_message, engine_type)
                    
                else:
                    await websocket.send(json.dumps({
                        "type": "error",
                        "message": f"Unknown action: {action}"
                    }))
                    
            except Exception as e:
                logger.error(f"Error: {e}")
                await websocket.send(json.dumps({
                    "type": "error",
                    "message": f"오류: {str(e)}"
                }))
                
    except websockets.exceptions.ConnectionClosed:
        logger.info("Connection closed")

def start_server():
    """서버 시작"""
    host = 'localhost'
    port = 8769
    
    logger.info(f"Starting WebSocket server on {host}:{port}")
    
    # 간단한 서버 시작
    start_server = websockets.serve(handle_websocket, host, port)
    
    try:
        asyncio.get_event_loop().run_until_complete(start_server)
        logger.info("WebSocket server started successfully")
        asyncio.get_event_loop().run_forever()
    except KeyboardInterrupt:
        logger.info("Server stopped by user")

if __name__ == "__main__":
    start_server()