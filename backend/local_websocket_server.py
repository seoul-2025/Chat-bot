"""
로컬 WebSocket 서버 - 기존 핸들러 로직 사용
"""
import asyncio
import json
import websockets
import os
import sys
import logging
from datetime import datetime

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 경로 설정
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 간단한 WebSocket 서비스 (의존성 최소화)
class SimpleWebSocketService:
    def __init__(self):
        pass
    
    def stream_response(self, user_message, engine_type, user_role='user'):
        """간단한 응답 생성 (실제로는 Bedrock 연동)"""
        # 여기서 실제 Bedrock 호출
        import boto3
        from config.aws import AWS_REGION, BEDROCK_CONFIG
        
        try:
            bedrock_client = boto3.client('bedrock-runtime', region_name=AWS_REGION)
            
            body = {
                "anthropic_version": BEDROCK_CONFIG['anthropic_version'],
                "max_tokens": BEDROCK_CONFIG['max_tokens'],
                "temperature": BEDROCK_CONFIG['temperature'],
                "messages": [{"role": "user", "content": user_message}],
                "top_k": BEDROCK_CONFIG['top_k'],
                "top_p": BEDROCK_CONFIG['top_p']
            }
            
            response = bedrock_client.invoke_model_with_response_stream(
                modelId=BEDROCK_CONFIG['model_id'],
                body=json.dumps(body)
            )
            
            stream = response.get('body')
            if stream:
                for event in stream:
                    chunk = event.get('chunk')
                    if chunk:
                        chunk_obj = json.loads(chunk.get('bytes').decode())
                        
                        if chunk_obj.get('type') == 'content_block_delta':
                            delta = chunk_obj.get('delta', {})
                            if delta.get('type') == 'text_delta':
                                text = delta.get('text', '')
                                if text:
                                    yield text
                        
                        elif chunk_obj.get('type') == 'message_stop':
                            break
                            
        except Exception as e:
            yield f"오류: {str(e)}"

class MockAPIGatewayClient:
    """API Gateway 클라이언트 모킹"""
    def __init__(self, websocket):
        self.websocket = websocket
    
    async def post_to_connection(self, ConnectionId, Data):
        """WebSocket으로 메시지 전송"""
        await self.websocket.send(Data)

async def handle_websocket(websocket, path):
    """WebSocket 연결 처리 - 기존 핸들러 로직 사용"""
    logger.info("New WebSocket connection")
    
    # WebSocket 서비스 초기화
    websocket_service = SimpleWebSocketService()
    
    # Mock API Gateway 클라이언트
    apigateway_client = MockAPIGatewayClient(websocket)
    
    try:
        async for message in websocket:
            try:
                logger.info(f"Received message: {message[:100]}...")
                
                # 요청 파싱
                if not message:
                    raise ValueError("No message body provided")
                
                body = json.loads(message)
                action = body.get('action', 'sendMessage')
                
                # 메시지 전송 액션
                if action == 'sendMessage':
                    # 필수 파라미터 추출 및 검증
                    user_message = body.get('message', '')
                    engine_type = body.get('engineType', '11')
                    conversation_id = body.get('conversationId')
                    user_id = body.get('userId', body.get('email', 'local_user'))
                    conversation_history = body.get('conversationHistory', [])
                    user_role = determine_user_role(user_id, body)
                    
                    logger.info(f"Processing message for {engine_type}, user: {user_id}, role: {user_role}")
                    
                    # AI 시작 알림
                    await send_message_to_client('local', {
                        'type': 'ai_start',
                        'timestamp': datetime.utcnow().isoformat() + 'Z'
                    }, apigateway_client)
                    
                    # 스트리밍 응답 전송
                    chunk_index = 0
                    total_response = ""
                    
                    try:
                        for chunk in websocket_service.stream_response(
                            user_message=user_message,
                            engine_type=engine_type,
                            user_role=user_role
                        ):
                            total_response += chunk
                            
                            # 청크 전송
                            logger.info(f"Sending chunk {chunk_index}, chunk length: {len(chunk)}")
                            await send_message_to_client('local', {
                                'type': 'ai_chunk',
                                'chunk': chunk,
                                'chunk_index': chunk_index,
                                'timestamp': datetime.utcnow().isoformat() + 'Z'
                            }, apigateway_client)
                            
                            chunk_index += 1
                    except Exception as stream_error:
                        logger.error(f"Streaming error: {stream_error}")
                        await send_message_to_client('local', {
                            'type': 'error',
                            'message': f'스트리밍 오류: {str(stream_error)}'
                        }, apigateway_client)
                        continue
                    
                    # 완료 알림
                    await send_message_to_client('local', {
                        'type': 'chat_end',
                        'engine': engine_type,
                        'conversationId': conversation_id,
                        'total_chunks': chunk_index,
                        'response_length': len(total_response),
                        'message': '응답 생성이 완료되었습니다.',
                        'timestamp': datetime.utcnow().isoformat() + 'Z'
                    }, apigateway_client)
                    
                    logger.info(f"Chat completed: {chunk_index} chunks, {len(total_response)} chars")
                
                else:
                    # 알 수 없는 액션
                    await send_message_to_client('local', {
                        'type': 'error',
                        'message': f'Unknown action: {action}'
                    }, apigateway_client)
                    
            except json.JSONDecodeError:
                await send_message_to_client('local', {
                    'type': 'error',
                    'message': 'Invalid JSON format'
                }, apigateway_client)
            except Exception as e:
                logger.error(f"Error processing message: {str(e)}", exc_info=True)
                
                # 에러 전송
                try:
                    await send_message_to_client('local', {
                        'type': 'error',
                        'message': f'처리 중 오류가 발생했습니다: {str(e)}'
                    }, apigateway_client)
                except:
                    pass
                
    except websockets.exceptions.ConnectionClosed:
        logger.info("WebSocket connection closed")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")


def determine_user_role(user_id, body):
    """사용자 역할 판단"""
    # body에서 직접 userRole 확인
    if body.get('userRole'):
        return body.get('userRole', 'user')
    
    # 이메일로 판단
    if user_id and '@sedaily.com' in str(user_id):
        return 'admin'
    
    return 'user'


async def send_message_to_client(connection_id, message, apigateway_client):
    """클라이언트에게 메시지 전송"""
    try:
        await apigateway_client.post_to_connection(
            ConnectionId=connection_id,
            Data=json.dumps(message, ensure_ascii=False, default=str)
        )
        logger.debug(f"Message sent to {connection_id}: {message.get('type', 'unknown')}")
        
    except Exception as e:
        logger.error(f"Error sending message to {connection_id}: {str(e)}")
        raise


def start_server():
    """서버 시작"""
    host = 'localhost'
    port = 8767
    
    logger.info(f"Starting WebSocket server on {host}:{port}")
    
    # Windows에서 asyncio 문제 해결
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    start_server_coro = websockets.serve(handle_websocket, host, port)
    server = loop.run_until_complete(start_server_coro)
    
    logger.info("WebSocket server started successfully")
    
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    finally:
        server.close()
        loop.run_until_complete(server.wait_closed())
        loop.close()

if __name__ == "__main__":
    start_server()