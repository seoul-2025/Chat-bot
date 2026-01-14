import json
import logging

# 로깅 설정
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    """프롬프트 관련 API 핸들러"""
    
    try:
        # HTTP 메서드와 경로 확인
        http_method = event.get('httpMethod', '')
        path = event.get('path', '')
        path_parameters = event.get('pathParameters', {})
        
        logger.info(f"Request: {http_method} {path}")
        logger.info(f"Path parameters: {path_parameters}")
        
        # CORS 헤더
        headers = {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
        }
        
        # OPTIONS 요청 처리 (CORS preflight)
        if http_method == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': headers,
                'body': ''
            }
        
        # 엔진 타입 추출
        engine_type = path_parameters.get('engineType', '11')
        
        # 프롬프트 조회
        if http_method == 'GET' and '/files' not in path:
            return get_prompt(engine_type, headers)
        
        # 파일 목록 조회
        elif http_method == 'GET' and '/files' in path:
            return get_files(engine_type, headers)
        
        else:
            return {
                'statusCode': 404,
                'headers': headers,
                'body': json.dumps({'error': 'Not Found'})
            }
            
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': 'Internal Server Error'})
        }

def get_prompt(engine_type, headers):
    """프롬프트 정보 조회"""
    
    # 기본 프롬프트 데이터
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

def get_files(engine_type, headers):
    """파일 목록 조회"""
    
    # 빈 파일 목록 반환
    files_data = {
        'files': []
    }
    
    return {
        'statusCode': 200,
        'headers': headers,
        'body': json.dumps(files_data)
    }