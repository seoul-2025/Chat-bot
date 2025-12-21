import json
import boto3

def lambda_handler(event, context):
    """WebSocket 연결 핸들러"""
    
    try:
        connection_id = event['requestContext']['connectionId']
        
        # DynamoDB에 연결 정보 저장
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('one-connections')
        
        table.put_item(
            Item={
                'connection_id': connection_id,
                'timestamp': context.aws_request_id
            }
        )
        
        return {'statusCode': 200}
        
    except Exception as e:
        print(f"연결 오류: {e}")
        return {'statusCode': 500}