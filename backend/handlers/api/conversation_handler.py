import json
import boto3
from datetime import datetime

def lambda_handler(event, context):
    """대화 관리 API 핸들러"""
    
    try:
        method = event['httpMethod']
        path = event['path']
        
        # CORS 헤더
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Methods': 'GET,POST,PATCH,DELETE,OPTIONS'
        }
        
        if method == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': headers
            }
        
        # 간단한 응답
        if method == 'GET' and '/conversations' in path:
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps([])
            }
        
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({'message': 'OK'})
        }
        
    except Exception as e:
        print(f"API 오류: {e}")
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': str(e)})
        }