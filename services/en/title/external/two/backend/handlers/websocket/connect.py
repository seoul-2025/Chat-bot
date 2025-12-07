"""
WebSocket 연결 핸들러 (Refactored)
"""
import boto3
from datetime import datetime
from src.config.database import get_table_name, AWS_REGION
from src.config.business import DEFAULT_ENGINE_TYPE, WEBSOCKET_CONFIG
from utils.logger import get_logger
from utils.response import create_response

logger = get_logger(__name__)


def handler(event, context):
    """
    WebSocket 연결 시 처리

    Responsibilities:
    1. 연결 ID 추출
    2. 사용자 정보 파싱
    3. 연결 정보 DynamoDB에 저장
    """
    try:
        connection_id = event['requestContext']['connectionId']

        # 쿼리 파라미터에서 사용자 정보 추출
        query_params = event.get('queryStringParameters', {}) or {}
        user_id = query_params.get('userId', 'anonymous')
        engine_type = query_params.get('engineType', DEFAULT_ENGINE_TYPE)

        # 연결 정보 저장
        dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
        table = dynamodb.Table(get_table_name('websocket_connections'))

        table.put_item(
            Item={
                'connectionId': connection_id,
                'userId': user_id,
                'engineType': engine_type,
                'connectedAt': datetime.utcnow().isoformat(),
                'ttl': int(datetime.utcnow().timestamp()) + WEBSOCKET_CONFIG['connection_ttl']
            }
        )

        logger.info(f"WebSocket connected: {connection_id} for user {user_id}")
        return create_response(200, {'message': 'Connected'})

    except Exception as e:
        logger.error(f"Connection error: {str(e)}", exc_info=True)
        return create_response(500, {'error': str(e)})
