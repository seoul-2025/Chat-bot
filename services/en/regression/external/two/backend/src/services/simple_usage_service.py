"""
Simple Usage Service
간단한 사용량 추적 서비스 (API Handler 전용)
기존 복잡한 UsageService와 별도로, usage 테이블의 간단한 CRUD만 담당
"""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from decimal import Decimal
from botocore.exceptions import ClientError

from src.config.business import TOKEN_ESTIMATION, USAGE_LIMITS

logger = logging.getLogger(__name__)


class SimpleUsageService:
    """
    간단한 사용량 추적 서비스

    Note: usage 테이블 구조에 맞춰 간단한 CRUD 작업만 수행
    """

    def __init__(self):
        """서비스 초기화"""
        from src.config.database import get_table_name
        import boto3
        import os

        region = os.environ.get('AWS_REGION', 'us-east-1')
        dynamodb = boto3.resource('dynamodb', region_name=region)

        self.usage_table = dynamodb.Table(get_table_name('usage'))
        logger.info("SimpleUsageService initialized")

    @staticmethod
    def decimal_to_float(obj):
        """
        DynamoDB Decimal을 float로 변환

        Args:
            obj: 변환할 객체 (Decimal, dict, list)

        Returns:
            변환된 객체
        """
        if isinstance(obj, Decimal):
            return float(obj)
        elif isinstance(obj, dict):
            return {k: SimpleUsageService.decimal_to_float(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [SimpleUsageService.decimal_to_float(v) for v in obj]
        return obj

    @staticmethod
    def estimate_tokens(text: str) -> int:
        """
        토큰 추정 (한글/영어 구분)

        Args:
            text: 입력 텍스트

        Returns:
            추정 토큰 수
        """
        if not text:
            return 0

        # 문자 타입별 카운트
        korean_chars = 0
        english_chars = 0
        numbers = 0
        spaces = 0

        for char in text:
            if '가' <= char <= '힣':
                korean_chars += 1
            elif char.isalpha() and char.isascii():
                english_chars += 1
            elif char.isdigit():
                numbers += 1
            elif char.isspace():
                spaces += 1

        # 나머지 특수문자
        special_chars = len(text) - korean_chars - english_chars - numbers - spaces

        # 토큰 계산 (설정값 사용)
        korean_tokens = korean_chars / TOKEN_ESTIMATION['korean_chars_per_token']
        english_tokens = english_chars / TOKEN_ESTIMATION['english_chars_per_token']
        number_tokens = numbers / TOKEN_ESTIMATION['numbers_chars_per_token']
        space_tokens = spaces / TOKEN_ESTIMATION['spaces_chars_per_token']
        special_tokens = special_chars / TOKEN_ESTIMATION['special_chars_per_token']

        total_tokens = (korean_tokens + english_tokens +
                        number_tokens + space_tokens + special_tokens)

        return max(1, int(total_tokens))

    def get_or_create_usage(
        self,
        user_id: str,
        engine_type: str
    ) -> Dict[str, Any]:
        """
        사용량 조회 또는 생성

        Args:
            user_id: 사용자 ID
            engine_type: 엔진 타입

        Returns:
            사용량 레코드
        """
        # 실제 테이블 구조에 맞게 수정: userId (PK), date (SK)
        today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        date_key = f"{today}#{engine_type}"

        try:
            # 먼저 조회
            response = self.usage_table.get_item(
                Key={'userId': user_id, 'date': date_key}
            )

            if 'Item' in response:
                return response['Item']

            # 없으면 새로 생성
            new_item = {
                'userId': user_id,
                'date': date_key,
                'engineType': engine_type,
                'usageDate': today,
                'totalTokens': Decimal('0'),
                'inputTokens': Decimal('0'),
                'outputTokens': Decimal('0'),
                'messageCount': Decimal('0'),
                'createdAt': datetime.now(timezone.utc).isoformat(),
                'updatedAt': datetime.now(timezone.utc).isoformat()
            }

            self.usage_table.put_item(Item=new_item)
            logger.info(f"Created new usage record: {user_id}/{date_key}")

            return new_item

        except ClientError as e:
            logger.error(f"Error getting/creating usage: {e}")
            raise

    def update_usage(
        self,
        user_id: str,
        engine_type: str,
        input_text: str,
        output_text: str,
        user_plan: str = 'free'
    ) -> Dict[str, Any]:
        """
        사용량 업데이트

        Args:
            user_id: 사용자 ID
            engine_type: 엔진 타입
            input_text: 입력 텍스트
            output_text: 출력 텍스트
            user_plan: 사용자 플랜 (free, basic, premium)

        Returns:
            업데이트 결과
        """
        try:
            # 토큰 계산
            input_tokens = self.estimate_tokens(input_text)
            output_tokens = self.estimate_tokens(output_text)
            total_tokens = input_tokens + output_tokens

            # 실제 테이블 구조에 맞게 수정
            today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
            date_key = f"{today}#{engine_type}"

            # 먼저 레코드 확인/생성
            self.get_or_create_usage(user_id, engine_type)

            # 간단한 업데이트 (ADD 사용으로 원자적 증가)
            response = self.usage_table.update_item(
                Key={'userId': user_id, 'date': date_key},
                UpdateExpression="""
                    ADD totalTokens :total,
                        inputTokens :input,
                        outputTokens :output,
                        messageCount :one
                    SET updatedAt = :timestamp,
                        lastUsedAt = :timestamp
                """,
                ExpressionAttributeValues={
                    ':total': Decimal(str(total_tokens)),
                    ':input': Decimal(str(input_tokens)),
                    ':output': Decimal(str(output_tokens)),
                    ':one': Decimal('1'),
                    ':timestamp': datetime.now(timezone.utc).isoformat()
                },
                ReturnValues='ALL_NEW'
            )

            updated_item = self.decimal_to_float(response['Attributes'])

            # 플랜별 월간 한도 가져오기 (설정값 사용)
            monthly_limit = USAGE_LIMITS.get(user_plan, USAGE_LIMITS['free'])['monthly_tokens']
            percentage = min(100, (updated_item['totalTokens'] / monthly_limit) * 100)

            logger.info(f"Usage updated for {user_id}: {total_tokens} tokens")

            return {
                'success': True,
                'usage': updated_item,
                'tokensUsed': total_tokens,
                'percentage': round(percentage, 1),
                'remaining': max(0, monthly_limit - updated_item['totalTokens'])
            }

        except ClientError as e:
            logger.error(f"Error updating usage: {e}")
            return {'success': False, 'error': str(e)}

    def get_usage(
        self,
        user_id: str,
        engine_type: str
    ) -> Optional[Dict[str, Any]]:
        """
        사용량 조회

        Args:
            user_id: 사용자 ID
            engine_type: 엔진 타입

        Returns:
            사용량 데이터 또는 None
        """
        try:
            today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
            date_key = f"{today}#{engine_type}"

            response = self.usage_table.get_item(
                Key={'userId': user_id, 'date': date_key}
            )

            if 'Item' in response:
                return self.decimal_to_float(response['Item'])

            # 없으면 기본값 반환
            return {
                'userId': user_id,
                'engineType': engine_type,
                'usageDate': today,
                'totalTokens': 0,
                'inputTokens': 0,
                'outputTokens': 0,
                'messageCount': 0
            }

        except ClientError as e:
            logger.error(f"Error getting usage: {e}")
            return None

    def get_all_usage(self, user_id: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        모든 엔진의 사용량 조회

        Args:
            user_id: 사용자 ID

        Returns:
            엔진별 사용량 딕셔너리
        """
        try:
            # userId로 모든 사용량 조회
            from boto3.dynamodb.conditions import Key
            response = self.usage_table.query(
                KeyConditionExpression=Key('userId').eq(user_id)
            )

            items = [self.decimal_to_float(item) for item in response.get('Items', [])]

            # 엔진별로 정리
            usage_by_engine = {}
            for item in items:
                engine_type = item.get('engineType', 'unknown')
                usage_date = item.get('usageDate', '')

                if engine_type not in usage_by_engine:
                    usage_by_engine[engine_type] = []

                usage_by_engine[engine_type].append(item)

            # 각 엔진별로 날짜 정렬 (최신순)
            for engine in usage_by_engine:
                usage_by_engine[engine].sort(
                    key=lambda x: x.get('usageDate', ''),
                    reverse=True
                )

            logger.info(f"Retrieved usage for {user_id}: {len(items)} records")

            return usage_by_engine

        except ClientError as e:
            logger.error(f"Error getting all usage: {e}")
            return {}

    def get_usage_percentage(
        self,
        user_id: str,
        engine_type: str,
        user_plan: str = 'free'
    ) -> Dict[str, Any]:
        """
        사용량 퍼센트 계산

        Args:
            user_id: 사용자 ID
            engine_type: 엔진 타입
            user_plan: 사용자 플랜

        Returns:
            사용량 퍼센트 정보
        """
        try:
            usage = self.get_usage(user_id, engine_type)

            if not usage:
                return {
                    'percentage': 0,
                    'remaining': USAGE_LIMITS[user_plan]['monthly_tokens']
                }

            total_tokens = usage.get('totalTokens', 0)
            monthly_limit = USAGE_LIMITS.get(user_plan, USAGE_LIMITS['free'])['monthly_tokens']

            percentage = min(100, (total_tokens / monthly_limit) * 100)
            remaining = max(0, monthly_limit - total_tokens)

            return {
                'percentage': round(percentage, 1),
                'remaining': remaining,
                'totalTokens': total_tokens,
                'monthlyLimit': monthly_limit
            }

        except Exception as e:
            logger.error(f"Error getting usage percentage: {e}")
            return {
                'percentage': 0,
                'remaining': USAGE_LIMITS['free']['monthly_tokens']
            }
