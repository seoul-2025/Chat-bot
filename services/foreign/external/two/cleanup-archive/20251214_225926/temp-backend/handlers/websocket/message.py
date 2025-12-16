"""
WebSocket Message Handler
WebSocket 메시지 처리 Lambda 핸들러
"""
import json
import boto3
import logging
from datetime import datetime

import sys
import os


from services.websocket_service import WebSocketService
from utils.logger import setup_logger
from lib.citation_formatter import CitationFormatter

logger = setup_logger(__name__)


def handler(event, context):
    """
    WebSocket 메시지 핸들러 - Service Layer 사용
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
    
    # Service 초기화
    websocket_service = WebSocketService()
    
    try:
        # 요청 파싱
        if not event.get('body'):
            raise ValueError("No message body provided")
        
        body = json.loads(event['body'])
        action = body.get('action', 'sendMessage')
        
        # 대화 초기화 액션
        if action == 'clearHistory':
            conversation_id = body.get('conversationId')
            if conversation_id:
                success = websocket_service.clear_history(conversation_id)
                send_message_to_client(connection_id, {
                    'type': 'history_cleared',
                    'message': '대화 기록이 초기화되었습니다.' if success else '초기화 실패'
                }, apigateway_client)
                
                return {
                    'statusCode': 200,
                    'body': json.dumps({'message': 'History cleared'})
                }
        
        # 메시지 전송 액션
        elif action == 'sendMessage':
            # 파라미터 추출
            user_message = body.get('message', '')
            engine_type = body.get('engineType', '11')
            conversation_id = body.get('conversationId')
            user_id = body.get('userId', body.get('email', connection_id))
            conversation_history = body.get('conversationHistory', [])
            user_role = determine_user_role(user_id, body)
            
            logger.info(f"Processing message for {engine_type}, user: {user_id}, role: {user_role}")
            
            # 1. 메시지 처리 시작
            process_result = websocket_service.process_message(
                user_message=user_message,
                engine_type=engine_type,
                conversation_id=conversation_id,
                user_id=user_id,
                conversation_history=conversation_history,
                user_role=user_role
            )
            
            conversation_id = process_result['conversation_id']
            merged_history = process_result['merged_history']
            
            # 2. AI 시작 알림
            send_message_to_client(connection_id, {
                'type': 'ai_start',
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }, apigateway_client)
            
            # 3. 스트리밍 응답 전송
            chunk_index = 0
            total_response = ""
            
            for chunk in websocket_service.stream_response(
                user_message=user_message,
                engine_type=engine_type,
                conversation_id=conversation_id,
                user_id=user_id,
                conversation_history=merged_history,
                user_role=user_role
            ):
                total_response += chunk
                
                # 청크 전송
                send_message_to_client(connection_id, {
                    'type': 'ai_chunk',
                    'chunk': chunk,
                    'chunk_index': chunk_index,
                    'timestamp': datetime.utcnow().isoformat() + 'Z'
                }, apigateway_client)
                
                chunk_index += 1
            
            # 4. 출처 포맷팅 적용
            if "📚 출처:" not in total_response and "http" in total_response:
                formatted_response = CitationFormatter.format_response_with_citations(total_response)
                if formatted_response != total_response:
                    logger.info("Citations formatted for response")
                    # 포맷팅된 출처 섹션만 클라이언트로 전송
                    citation_section = formatted_response[len(total_response):]
                    if citation_section:
                        send_message_to_client(connection_id, {
                            'type': 'ai_chunk',
                            'chunk': citation_section,
                            'chunk_index': chunk_index,
                            'is_citation': True,
                            'timestamp': datetime.utcnow().isoformat() + 'Z'
                        }, apigateway_client)
                        chunk_index += 1
                    total_response = formatted_response
            
            # 5. 사용량 추적
            websocket_service.track_usage(
                user_id=user_id,
                engine_type=engine_type,
                input_text=user_message,
                output_text=total_response
            )

            # 5.5. AI 응답 저장 - ConversationManager import 필요
            from handlers.websocket.conversation_manager import ConversationManager
            conversation_manager = ConversationManager()
            conversation_manager.save_message(
                conversation_id=conversation_id,
                role='assistant',
                content=total_response,
                engine_type=engine_type,
                user_id=user_id
            )
            logger.info(f"AI response saved to conversation: {conversation_id}")

            # 6. 완료 알림
            send_message_to_client(connection_id, {
                'type': 'chat_end',
                'engine': engine_type,
                'conversationId': conversation_id,
                'total_chunks': chunk_index,
                'response_length': len(total_response),
                'message': '응답 생성이 완료되었습니다.',
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }, apigateway_client)
            
            logger.info(f"Chat completed: {chunk_index} chunks, {len(total_response)} chars")
            
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'message': 'Message processed successfully',
                    'chunks_sent': chunk_index,
                    'response_length': len(total_response)
                })
            }
        
        else:
            # 알 수 없는 액션
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
        
        # 에러 전송
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


def determine_user_role(user_id, body):
    """사용자 역할 판단"""
    # body에서 직접 userRole 확인
    if body.get('userRole'):
        return body.get('userRole', 'user')
    
    # 이메일로 판단
    if user_id and '@sedaily.com' in str(user_id):
        return 'admin'
    
    return 'user'


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
        # 연결이 끊어진 경우 정리
        try:
            dynamodb = boto3.resource('dynamodb', region_name=os.environ.get('AWS_REGION', 'us-east-1'))
            connections_table = dynamodb.Table(os.environ.get('WEBSOCKET_TABLE', 'f1-websocket-connections-two'))
            connections_table.delete_item(Key={'connectionId': connection_id})
        except:
            pass
            
    except Exception as e:
        logger.error(f"Error sending message to {connection_id}: {str(e)}")
        raise