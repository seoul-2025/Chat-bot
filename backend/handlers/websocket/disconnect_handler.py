import json
import boto3

def lambda_handler(event, context):
    """WebSocket 연결 해제 핸들러"""
    
    try:
        connection_id = event['requestContext']['connectionId']
        
        # DynamoDB에서 연결 정보 삭제
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('one-connections')
        
        table.delete_item(
            Key={'connection_id': connection_id}
        )
        
        return {'statusCode': 200}
        
    except Exception as e:
        print(f"연결 해제 오류: {e}")
        return {'statusCode': 500}