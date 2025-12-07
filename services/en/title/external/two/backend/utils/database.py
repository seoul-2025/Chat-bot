"""
Database Utilities
DynamoDB 연결 및 공통 작업을 위한 유틸리티
"""
import boto3
import logging
import os
from typing import Optional
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


def get_dynamodb_resource(region: str = None):
    """
    DynamoDB 리소스 객체 생성

    Args:
        region: AWS 리전 (기본값: 환경변수 또는 us-east-1)

    Returns:
        boto3 DynamoDB resource
    """
    region = region or os.environ.get('AWS_REGION', 'us-east-1')
    return boto3.resource('dynamodb', region_name=region)


def get_dynamodb_client(region: str = None):
    """
    DynamoDB 클라이언트 객체 생성

    Args:
        region: AWS 리전 (기본값: 환경변수 또는 us-east-1)

    Returns:
        boto3 DynamoDB client
    """
    region = region or os.environ.get('AWS_REGION', 'us-east-1')
    return boto3.client('dynamodb', region_name=region)


def get_table(table_name: str, region: str = None):
    """
    DynamoDB 테이블 객체 가져오기

    Args:
        table_name: 테이블 이름
        region: AWS 리전

    Returns:
        DynamoDB Table 객체
    """
    dynamodb = get_dynamodb_resource(region)
    return dynamodb.Table(table_name)


def get_table_from_env(env_var: str, default_name: str, region: str = None):
    """
    환경변수로부터 테이블 이름을 읽어 테이블 객체 반환

    Args:
        env_var: 환경변수 이름 (예: 'CONVERSATIONS_TABLE')
        default_name: 기본 테이블 이름 (환경변수가 없을 때)
        region: AWS 리전

    Returns:
        DynamoDB Table 객체
    """
    table_name = os.environ.get(env_var, default_name)
    return get_table(table_name, region)


def table_exists(table_name: str, region: str = None) -> bool:
    """
    테이블 존재 여부 확인

    Args:
        table_name: 테이블 이름
        region: AWS 리전

    Returns:
        테이블 존재 여부
    """
    try:
        client = get_dynamodb_client(region)
        client.describe_table(TableName=table_name)
        return True
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            return False
        raise


def create_connection_pool(max_pool_connections: int = 50):
    """
    DynamoDB 연결 풀 설정

    Args:
        max_pool_connections: 최대 연결 수

    Returns:
        설정된 boto3 Config 객체
    """
    from botocore.config import Config

    return Config(
        max_pool_connections=max_pool_connections,
        retries={
            'max_attempts': 3,
            'mode': 'standard'
        }
    )


# 공통 테이블 객체 (캐싱)
_table_cache = {}


def get_cached_table(table_name: str, region: str = None):
    """
    캐시된 테이블 객체 반환 (성능 최적화)

    Args:
        table_name: 테이블 이름
        region: AWS 리전

    Returns:
        DynamoDB Table 객체
    """
    cache_key = f"{table_name}:{region or 'default'}"

    if cache_key not in _table_cache:
        _table_cache[cache_key] = get_table(table_name, region)
        logger.info(f"Cached table: {table_name}")

    return _table_cache[cache_key]


def clear_table_cache():
    """테이블 캐시 초기화 (테스트 시 유용)"""
    global _table_cache
    _table_cache = {}
    logger.info("Table cache cleared")


# 공통 DynamoDB 작업 헬퍼

def safe_get_item(table, key: dict) -> Optional[dict]:
    """
    안전한 아이템 조회 (에러 핸들링 포함)

    Args:
        table: DynamoDB Table 객체
        key: Primary key

    Returns:
        Item 딕셔너리 또는 None
    """
    try:
        response = table.get_item(Key=key)
        return response.get('Item')
    except ClientError as e:
        logger.error(f"Error getting item: {e}")
        return None


def safe_put_item(table, item: dict) -> bool:
    """
    안전한 아이템 저장 (에러 핸들링 포함)

    Args:
        table: DynamoDB Table 객체
        item: 저장할 아이템

    Returns:
        성공 여부
    """
    try:
        table.put_item(Item=item)
        return True
    except ClientError as e:
        logger.error(f"Error putting item: {e}")
        return False


def safe_update_item(table, key: dict, update_expression: str, expression_values: dict) -> bool:
    """
    안전한 아이템 업데이트 (에러 핸들링 포함)

    Args:
        table: DynamoDB Table 객체
        key: Primary key
        update_expression: UpdateExpression 문자열
        expression_values: ExpressionAttributeValues 딕셔너리

    Returns:
        성공 여부
    """
    try:
        table.update_item(
            Key=key,
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_values
        )
        return True
    except ClientError as e:
        logger.error(f"Error updating item: {e}")
        return False


def safe_delete_item(table, key: dict) -> bool:
    """
    안전한 아이템 삭제 (에러 핸들링 포함)

    Args:
        table: DynamoDB Table 객체
        key: Primary key

    Returns:
        성공 여부
    """
    try:
        table.delete_item(Key=key)
        return True
    except ClientError as e:
        logger.error(f"Error deleting item: {e}")
        return False


def batch_write_items(table, items: list, batch_size: int = 25) -> bool:
    """
    배치 쓰기 작업

    Args:
        table: DynamoDB Table 객체
        items: 쓸 아이템 리스트
        batch_size: 배치 크기 (최대 25)

    Returns:
        성공 여부
    """
    try:
        with table.batch_writer() as batch:
            for i, item in enumerate(items):
                batch.put_item(Item=item)

                # 배치 크기마다 로그
                if (i + 1) % batch_size == 0:
                    logger.info(f"Batch write progress: {i + 1}/{len(items)}")

        logger.info(f"Batch write completed: {len(items)} items")
        return True

    except ClientError as e:
        logger.error(f"Error in batch write: {e}")
        return False
