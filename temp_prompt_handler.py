import json
from datetime import datetime

def handler(event, context):
    """프롬프트 API 핸들러 - CORS 지원"""
    
    # CORS 헤더
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
        'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
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
        
        path_params = event.get('pathParameters') or {}
        engine_type = path_params.get('engineType', '11')
        
        # GET 요청 - 프롬프트 조회
        if method == 'GET':
            if 'files' in event.get('path', ''):
                # 프롬프트 파일 목록 조회
                return {
                    'statusCode': 200,
                    'headers': headers,
                    'body': json.dumps({'files': []})
                }
            else:
                # 프롬프트 조회
                prompt_data = {
                    'engineType': engine_type,
                    'description': f'{engine_type} 엔진 전용 AI 어시스턴트',
                    'instructions': f'{engine_type} 엔진에 맞는 전문적인 답변을 제공해주세요.',
                    'files': []
                }
                return {
                    'statusCode': 200,
                    'headers': headers,
                    'body': json.dumps(prompt_data)
                }
        
        # POST/PUT 요청 - 프롬프트 생성/수정
        elif method in ['POST', 'PUT']:
            body = json.loads(event.get('body', '{}'))
            
            result = {
                'success': True,
                'message': '프롬프트가 성공적으로 저장되었습니다.',
                'engineType': engine_type,
                'updatedAt': datetime.now().isoformat()
            }
            
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps(result)
            }
        
        # DELETE 요청 - 프롬프트 삭제
        elif method == 'DELETE':
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps({
                    'success': True,
                    'message': '프롬프트가 성공적으로 삭제되었습니다.'
                })
            }
        
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