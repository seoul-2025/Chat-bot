"""
WebSocket Disconnect Handler
WebSocket 연결 해제 처리 Lambda 핸들러
"""
import json
import boto3
import logging
import os

from utils.logger import setup_logger

logger = setup_logger(__name__)


def handler(event, context):
    """
    WebSocket 연결 해제 핸들러
    """
    logger.info(f"Disconnect event: {json.dumps(event)}")
    
    connection_id = event['requestContext']['connectionId']
    
    try:
        # DynamoDB에서 연결 정보 삭제
        dynamodb = boto3.resource('dynamodb', region_name=os.environ.get('AWS_REGION', 'us-east-1'))
        connections_table = dynamodb.Table(os.environ.get('CONNECTIONS_TABLE', 'one-connections'))
        
        connections_table.delete_item(
            Key={'connectionId': connection_id}
        )
        
        logger.info(f"Connection {connection_id} removed successfully")
        
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Disconnected successfully'})
        }
        
    except Exception as e:
        logger.error(f"Error handling disconnection: {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }