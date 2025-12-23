import json
import boto3

def handler(event, context):
    """WebSocket 연결 해제 핸들러"""
    
    try:
        connection_id = event['requestContext']['connectionId']
        
        # DynamoDB 클라이언트
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('bodo-external-backend-v2-prod-websocket-connections')
        
        # 연결 정보 삭제
        table.delete_item(
            Key={'connectionId': connection_id}
        )
        
        print(f"WebSocket 연결 해제: {connection_id}")
        
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Disconnected'})
        }
        
    except Exception as e:
        print(f"WebSocket 연결 해제 오류: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }