import json
import boto3
import requests
import os
from datetime import datetime

def handler(event, context):
    """WebSocket 메시지 핸들러"""
    
    try:
        connection_id = event['requestContext']['connectionId']
        domain_name = event['requestContext']['domainName']
        stage = event['requestContext']['stage']
        
        # API Gateway Management API 클라이언트
        apigateway_management_api = boto3.client(
            'apigatewaymanagementapi',
            endpoint_url=f'https://{domain_name}/{stage}'
        )
        
        # 메시지 파싱
        body = json.loads(event.get('body', '{}'))
        action = body.get('action')
        message = body.get('message', '')
        engine_type = body.get('engineType', '11')
        
        print(f"WebSocket 메시지 수신: {action}, 엔진: {engine_type}")
        
        if action == 'sendMessage':
            # Claude API 호출
            claude_api_key = os.environ.get('CLAUDE_API_KEY')
            if not claude_api_key:
                raise Exception('Claude API 키가 설정되지 않았습니다.')
            
            # AI 시작 신호 전송
            send_message_to_client(apigateway_management_api, connection_id, {
                'type': 'ai_start',
                'timestamp': datetime.now().isoformat()
            })
            
            # Claude API 요청
            claude_response = requests.post(
                'https://api.anthropic.com/v1/messages',
                headers={
                    'Content-Type': 'application/json',
                    'x-api-key': claude_api_key,
                    'anthropic-version': '2023-06-01'
                },
                json={
                    'model': 'claude-3-5-sonnet-20241022',
                    'max_tokens': 4000,
                    'messages': [{'role': 'user', 'content': message}]
                }
            )
            
            if claude_response.ok:
                response_data = claude_response.json()
                ai_message = response_data['content'][0]['text']
                
                # 응답을 청크로 나누어 전송
                chunks = [ai_message[i:i+100] for i in range(0, len(ai_message), 100)]
                
                for i, chunk in enumerate(chunks):
                    send_message_to_client(apigateway_management_api, connection_id, {
                        'type': 'ai_chunk',
                        'chunk': chunk,
                        'chunk_index': i
                    })
                
                # 완료 신호
                send_message_to_client(apigateway_management_api, connection_id, {
                    'type': 'chat_end',
                    'total_chunks': len(chunks),
                    'engine': engine_type
                })
            else:
                # 오류 응답
                send_message_to_client(apigateway_management_api, connection_id, {
                    'type': 'error',
                    'message': f'Claude API 오류: {claude_response.status_code}'
                })
        
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Message processed'})
        }
        
    except Exception as e:
        print(f"WebSocket 메시지 처리 오류: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

def send_message_to_client(apigateway_management_api, connection_id, message):
    """클라이언트에게 메시지 전송"""
    try:
        apigateway_management_api.post_to_connection(
            ConnectionId=connection_id,
            Data=json.dumps(message)
        )
    except Exception as e:
        print(f"메시지 전송 오류: {str(e)}")