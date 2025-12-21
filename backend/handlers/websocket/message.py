"""
WebSocket Message Handler
WebSocket 메시지 처리 Lambda 핸들러
"""
import json
import boto3
import logging
from datetime import datetime

from services.websocket_service import WebSocketService
from utils.logger import setup_logger

logger = setup_logger(__name__)


def handler(event, context):
    """
    WebSocket 메시지 핸들러
    """
    logger.info(f"Message event: {json.dumps(event)}")
    
    # WebSocket 연결 정보
    connection_id = event['requestContext']['connectionId']
    domain_name = event['requestContext']['domainName']
    stage = event['requestContext']['stage']
    
    # API Gateway Management API 클라이언트
    apigateway_client = boto3.client(
        'apigatewaymanagementapi',
        endpoint_url=f'https://{domain_name}/{stage}',
        region_name='us-east-1'
    )
    
    try:
        # 요청 파싱
        if not event.get('body'):
            raise ValueError("No message body provided")
        
        body = json.loads(event['body'])
        action = body.get('action', 'sendMessage')
        
        # 메시지 전송 액션
        if action == 'sendMessage':
            user_message = body.get('message', '')
            engine_type = body.get('engineType', '11')
            conversation_id = body.get('conversationId')
            user_id = body.get('userId', connection_id)
            
            logger.info(f"Processing message for {engine_type}, user: {user_id}")
            
            # 응답 시뮬레이션 (실제로는 AI 모델 호출)
            response_text = f"Echo: {user_message} (Engine: {engine_type})"
            
            # 응답 전송
            send_message_to_client(connection_id, {
                'type': 'ai_chunk',
                'chunk': response_text,
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }, apigateway_client)
            
            # 완료 알림
            send_message_to_client(connection_id, {
                'type': 'chat_end',
                'engine': engine_type,
                'conversationId': conversation_id,
                'message': '응답 생성이 완료되었습니다.',
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }, apigateway_client)
            
            return {
                'statusCode': 200,
                'body': json.dumps({'message': 'Message processed successfully'})
            }
        
        else:
            send_message_to_client(connection_id, {
                'type': 'error',
                'message': f'Unknown action: {action}'
            }, apigateway_client)
            
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Unknown action'})
            }
            
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}", exc_info=True)
        
        try:
            send_message_to_client(connection_id, {
                'type': 'error',
                'message': f'처리 중 오류가 발생했습니다: {str(e)}'
            }, apigateway_client)
        except:
            pass
        
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }


def send_message_to_client(connection_id, message, apigateway_client):
    """클라이언트에게 메시지 전송"""
    try:
        apigateway_client.post_to_connection(
            ConnectionId=connection_id,
            Data=json.dumps(message, ensure_ascii=False, default=str)
        )
        logger.debug(f"Message sent to {connection_id}: {message.get('type', 'unknown')}")
        
    except apigateway_client.exceptions.GoneException:
        logger.warning(f"Connection {connection_id} is gone")
            
    except Exception as e:
        logger.error(f"Error sending message to {connection_id}: {str(e)}")
        raise