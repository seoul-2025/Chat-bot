import json
import random
from datetime import datetime

def lambda_handler(event, context):
    """사용량 추적 API 핸들러"""
    
    try:
        # CORS 헤더
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Methods': 'GET,POST,OPTIONS'
        }
        
        if event['httpMethod'] == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': headers
            }
        
        method = event.get('httpMethod')
        
        if method == 'GET':
            # 사용량 조회
            path_params = event.get('pathParameters', {})
            user_id = path_params.get('user_id')
            conversation_id = path_params.get('conversation_id')
            
            # 테스트용 더미 데이터
            usage_data = {
                'success': True,
                'data': {
                    'totalTokens': random.randint(1000, 3000),
                    'inputTokens': random.randint(500, 1500),
                    'outputTokens': random.randint(500, 1500),
                    'messageCount': random.randint(10, 30),
                    'lastUsedAt': datetime.now().isoformat()
                }
            }
            
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps(usage_data)
            }
            
        elif method == 'POST':
            # 사용량 업데이트
            body = json.loads(event.get('body', '{}'))
            user_id = body.get('userId')
            engine_type = body.get('engineType')
            input_text = body.get('inputText', '')
            output_text = body.get('outputText', '')
            
            # 테스트용 응답
            result = {
                'success': True,
                'tokensUsed': len(input_text) + len(output_text),
                'percentage': random.randint(10, 40),
                'remaining': 7500
            }
            
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps(result)
            }
        
        return {
            'statusCode': 405,
            'headers': headers,
            'body': json.dumps({'error': '지원하지 않는 메서드입니다.'})
        }
        
    except Exception as e:
        print(f"사용량 API 오류: {e}")
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': str(e)})
        }