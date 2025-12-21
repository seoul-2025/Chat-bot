import json
import os
import anthropic

def lambda_handler(event, context):
    """채팅 API 핸들러"""
    
    try:
        # CORS 헤더
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Methods': 'POST,OPTIONS'
        }
        
        if event['httpMethod'] == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': headers
            }
        
        # 요청 데이터 파싱
        body = json.loads(event.get('body', '{}'))
        message = body.get('message', '')
        
        if not message:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({'error': '메시지가 필요합니다'})
            }
        
        # Claude API 호출
        client = anthropic.Anthropic(
            api_key=os.environ.get('CLAUDE_API_KEY')
        )
        
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4000,
            messages=[{
                "role": "user",
                "content": message
            }]
        )
        
        # 응답 반환
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({
                'response': response.content[0].text,
                'engine': 'claude'
            })
        }
        
    except Exception as e:
        print(f"채팅 API 오류: {e}")
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': str(e)})
        }