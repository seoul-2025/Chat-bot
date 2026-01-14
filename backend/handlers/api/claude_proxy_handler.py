import json
import os
import requests
from typing import Dict, Any

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Claude API 프록시 Lambda 핸들러"""
    
    try:
        # CORS 헤더
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,Authorization',
            'Access-Control-Allow-Methods': 'POST,OPTIONS'
        }
        
        # OPTIONS 요청 처리
        if event.get('httpMethod') == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': headers,
                'body': ''
            }
        
        # 요청 본문 파싱
        body = json.loads(event.get('body', '{}'))
        message = body.get('message')
        api_key = body.get('apiKey') or os.environ.get('CLAUDE_API_KEY')
        
        if not api_key:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({'error': 'API 키가 필요합니다.'})
            }
        
        if not message:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({'error': '메시지가 필요합니다.'})
            }
        
        # Claude API 요청
        claude_response = requests.post(
            'https://api.anthropic.com/v1/messages',
            headers={
                'Content-Type': 'application/json',
                'x-api-key': api_key,
                'anthropic-version': '2023-06-01'
            },
            json={
                'model': 'claude-3-5-sonnet-20241022',
                'max_tokens': 4000,
                'messages': [{'role': 'user', 'content': message}]
            }
        )
        
        if not claude_response.ok:
            return {
                'statusCode': claude_response.status_code,
                'headers': headers,
                'body': json.dumps({
                    'error': f'Claude API 오류: {claude_response.status_code}',
                    'details': claude_response.text
                })
            }
        
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps(claude_response.json())
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'error': '서버 오류가 발생했습니다.',
                'details': str(e)
            })
        }