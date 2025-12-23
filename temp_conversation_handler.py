import json
import boto3
from datetime import datetime
import uuid

def handler(event, context):
    """대화 관리 API 핸들러 - CORS 지원"""
    
    # CORS 헤더
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
        'Access-Control-Allow-Methods': 'GET,POST,PATCH,DELETE,OPTIONS',
        'Content-Type': 'application/json'
    }
    
    try:
        method = event.get('httpMethod')
        
        # OPTIONS 요청 처리
        if method == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': headers,
                'body': ''
            }
        
        # GET 요청 - 대화 목록 조회
        if method == 'GET':
            query_params = event.get('queryStringParameters') or {}
            user_id = query_params.get('userId', 'anonymous')
            engine_type = query_params.get('engineType', '11')
            
            # 테스트용 더미 데이터
            conversations = [
                {
                    'conversationId': str(uuid.uuid4()),
                    'title': f'대화 {i+1}',
                    'createdAt': datetime.now().isoformat(),
                    'updatedAt': datetime.now().isoformat(),
                    'engineType': engine_type,
                    'messageCount': i + 5
                }
                for i in range(3)
            ]
            
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps({
                    'conversations': conversations,
                    'total': len(conversations)
                })
            }
        
        # POST 요청 - 새 대화 생성
        elif method == 'POST':
            body = json.loads(event.get('body', '{}'))
            
            new_conversation = {
                'conversationId': str(uuid.uuid4()),
                'title': body.get('title', '새 대화'),
                'createdAt': datetime.now().isoformat(),
                'updatedAt': datetime.now().isoformat(),
                'engineType': body.get('engineType', '11'),
                'messageCount': 0
            }
            
            return {
                'statusCode': 201,
                'headers': headers,
                'body': json.dumps(new_conversation)
            }
        
        # 기타 메서드들
        else:
            return {
                'statusCode': 405,
                'headers': headers,
                'body': json.dumps({'error': '지원하지 않는 메서드입니다.'})
            }
            
    except Exception as e:
        print(f"오류: {str(e)}")
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'error': '서버 오류가 발생했습니다.'})
        }