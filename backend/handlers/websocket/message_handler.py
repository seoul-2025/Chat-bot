import json
import boto3
import asyncio
from datetime import datetime

def lambda_handler(event, context):
    """WebSocket 메시지 핸들러"""
    
    try:
        # WebSocket 메시지 처리
        body = json.loads(event.get('body', '{}'))
        connection_id = event['requestContext']['connectionId']
        
        # 간단한 응답 전송
        gateway_api = boto3.client('apigatewaymanagementapi',
            endpoint_url=f"https://{event['requestContext']['domainName']}/{event['requestContext']['stage']}")
        
        # AI 응답 시뮬레이션
        response_message = {
            "type": "ai_chunk",
            "chunk": "안녕하세요! 현재 AI 서비스를 설정 중입니다.",
            "chunk_index": 0
        }
        
        gateway_api.post_to_connection(
            ConnectionId=connection_id,
            Data=json.dumps(response_message)
        )
        
        # 완료 메시지
        end_message = {
            "type": "chat_end",
            "total_chunks": 1,
            "engine": "claude"
        }
        
        gateway_api.post_to_connection(
            ConnectionId=connection_id,
            Data=json.dumps(end_message)
        )
        
        return {'statusCode': 200}
        
    except Exception as e:
        print(f"메시지 처리 오류: {e}")
        return {'statusCode': 500}