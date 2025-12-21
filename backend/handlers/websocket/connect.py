"""
WebSocket Connect Handler
WebSocket 연결 처리 Lambda 핸들러
"""
import json
import boto3
import logging
import os
from datetime import datetime

from utils.logger import setup_logger

logger = setup_logger(__name__)


def handler(event, context):
    """
    WebSocket 연결 핸들러
    """
    logger.info(f"Connect event: {json.dumps(event)}")
    
    connection_id = event['requestContext']['connectionId']
    
    try:
        # DynamoDB에 연결 정보 저장
        dynamodb = boto3.resource('dynamodb', region_name=os.environ.get('AWS_REGION', 'us-east-1'))
        connections_table = dynamodb.Table(os.environ.get('CONNECTIONS_TABLE', 'one-connections'))
        
        connections_table.put_item(
            Item={
                'connectionId': connection_id,
                'connectedAt': datetime.utcnow().isoformat() + 'Z',
                'ttl': int(datetime.utcnow().timestamp()) + 86400  # 24시간 TTL
            }
        )
        
        logger.info(f"Connection {connection_id} stored successfully")
        
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Connected successfully'})
        }
        
    except Exception as e:
        logger.error(f"Error handling connection: {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }