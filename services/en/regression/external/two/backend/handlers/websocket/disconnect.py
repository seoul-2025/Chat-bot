"""
WebSocket 연결 해제 핸들러 (Refactored)
"""
import boto3
from src.config.database import get_table_name, AWS_REGION
from utils.logger import get_logger
from utils.response import create_response

logger = get_logger(__name__)


def handler(event, context):
    """
    WebSocket 연결 해제 시 처리

    Responsibilities:
    1. 연결 ID 추출
    2. 연결 정보 DynamoDB에서 삭제
    """
    try:
        connection_id = event['requestContext']['connectionId']

        # 연결 정보 삭제
        dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
        table = dynamodb.Table(get_table_name('websocket_connections'))

        table.delete_item(
            Key={'connectionId': connection_id}
        )

        logger.info(f"WebSocket disconnected: {connection_id}")
        return create_response(200, {'message': 'Disconnected'})

    except Exception as e:
        logger.error(f"Disconnect error: {str(e)}", exc_info=True)
        return create_response(500, {'error': str(e)})
