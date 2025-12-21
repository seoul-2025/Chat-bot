import json

def lambda_handler(event, context):
    """사용량 추적 API 핸들러"""
    
    try:
        # CORS 헤더
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Methods': 'GET,OPTIONS'
        }
        
        if event['httpMethod'] == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': headers
            }
        
        # 기본 사용량 응답
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({
                'percentage': 0,
                'used': 0,
                'limit': 100
            })
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