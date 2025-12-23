"""
Windows 호환 WebSocket 서버
"""
import asyncio
import json
import websockets
import os
import sys
import logging
from datetime import datetime
import threading
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.services.claude_service import generate_claude_response

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

def run_server():
    """별도 스레드에서 서버 실행"""
    # 새로운 이벤트 루프 생성
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    # Windows 정책 설정
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    try:
        # 서버 시작
        start_server = websockets.serve(handle_websocket, 'localhost', 8767)
        loop.run_until_complete(start_server)
        logger.info("WebSocket server started on localhost:8767")
        
        # 서버 실행
        loop.run_forever()
    except Exception as e:
        logger.error(f"Server error: {e}")
    finally:
        loop.close()

if __name__ == "__main__":
    try:
        # 메인 스레드에서 서버 실행
        if os.name == 'nt':
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        
        # 직접 실행
        asyncio.run(websockets.serve(handle_websocket, 'localhost', 8767))
        
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        # 대안: 스레드 사용
        logger.info("Trying alternative method...")
        server_thread = threading.Thread(target=run_server)
        server_thread.daemon = True
        server_thread.start()
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Server stopped")