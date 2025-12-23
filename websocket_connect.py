import json
import boto3
from datetime import datetime

def handler(event, context):
    """WebSocket 연결 핸들러"""
    
    try:
        connection_id = event['requestContext']['connectionId']
        
        # DynamoDB 클라이언트
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('bodo-external-backend-v2-prod-websocket-connections')
        
        # 연결 정보 저장
        table.put_item(
            Item={
                'connectionId': connection_id,
                'timestamp': datetime.now().isoformat(),
                'status': 'connected'
            }
        )
        
        print(f"WebSocket 연결 성공: {connection_id}")
        
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Connected'})
        }
        
    except Exception as e:
        print(f"WebSocket 연결 오류: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }