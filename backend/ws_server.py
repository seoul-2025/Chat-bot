#!/usr/bin/env python3
import asyncio
import sys
import platform

# Windows 환경에서 WinError 10014 해결
if platform.system() == 'Windows':
    # Windows에서 소켓 문제 해결을 위한 설정
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    # 추가 Windows 호환성 설정
    import socket
    socket.socket = socket.socket

import json
import websockets
import boto3
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# AWS Bedrock 클라이언트
bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')

async def handle_client(websocket, path):
    logger.info("Client connected")
    try:
        async for message in websocket:
            data = json.loads(message)
            user_message = data.get('message', '')
            
            logger.info(f"Processing: {user_message[:50]}...")
            
            # AI 시작 신호
            await websocket.send(json.dumps({"type": "ai_start"}))
            
            # Bedrock 호출
            try:
                response = bedrock.invoke_model_with_response_stream(
                    modelId='us.anthropic.claude-opus-4-5-20251101-v1:0',
                    body=json.dumps({
                        "anthropic_version": "bedrock-2023-05-31",
                        "max_tokens": 4000,
                        "messages": [{"role": "user", "content": user_message}]
                    })
                )
                
                chunk_index = 0
                for event in response['body']:
                    chunk = event.get('chunk')
                    if chunk:
                        chunk_data = json.loads(chunk['bytes'].decode())
                        if chunk_data.get('type') == 'content_block_delta':
                            delta = chunk_data.get('delta', {})
                            if delta.get('type') == 'text_delta':
                                text = delta.get('text', '')
                                if text:
                                    await websocket.send(json.dumps({
                                        "type": "ai_chunk",
                                        "chunk": text,
                                        "chunk_index": chunk_index
                                    }))
                                    chunk_index += 1
                
                await websocket.send(json.dumps({
                    "type": "chat_end",
                    "total_chunks": chunk_index
                }))
                
            except Exception as e:
                logger.error(f"Bedrock error: {e}")
                await websocket.send(json.dumps({
                    "type": "error",
                    "message": str(e)
                }))
                
    except websockets.exceptions.ConnectionClosed:
        logger.info("Client disconnected")

async def main():
    logger.info("Starting server on 127.0.0.1:8769")
    # Windows 호환성을 위해 명시적 IP 주소 사용
    async with websockets.serve(
        handle_client, 
        "127.0.0.1", 
        8769,
        # Windows 소켓 문제 해결을 위한 추가 옵션
        reuse_port=False
    ):
        logger.info("WebSocket Server running on ws://localhost:8769")
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    # Windows에서 이벤트 루프 문제 해결을 위한 대안적 접근
    if platform.system() == 'Windows':
        try:
            # 새로운 이벤트 루프 생성 및 설정
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(main())
        except Exception as e:
            logger.error(f"Windows event loop error: {e}")
            # ProactorEventLoop로 폴백
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
            asyncio.run(main())
    else:
        asyncio.run(main())