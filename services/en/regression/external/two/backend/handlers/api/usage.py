"""
Usage API Handler (Refactored)
사용량 추적 REST API 엔드포인트 - Service Layer 사용
"""
import json
import logging
from urllib.parse import unquote

from src.services import SimpleUsageService
from utils.logger import setup_logger
from utils.response import APIResponse

# 로깅 설정
logger = setup_logger(__name__)


def handler(event, context):
    """
    Lambda 핸들러 - 사용량 API

    Responsibilities:
    1. 요청 파싱
    2. 서비스 계층 호출
    3. 응답 반환
    """
    try:
        logger.info(f"Usage API Event: {json.dumps(event)}")

        # API Gateway v2 형식 처리
        if 'version' in event and event['version'] == '2.0':
            # API Gateway v2 (HTTP API)
            http_method = event.get('requestContext', {}).get('http', {}).get('method')
            path_params = event.get('pathParameters', {})
        else:
            # API Gateway v1 (REST API) 또는 직접 호출
            http_method = event.get('httpMethod')
            path_params = event.get('pathParameters', {})

        # OPTIONS 요청 처리 (CORS preflight)
        if http_method == 'OPTIONS':
            return APIResponse.cors_preflight()

        # 서비스 초기화
        usage_service = SimpleUsageService()

        # 라우팅
        if http_method == 'GET':
            return handle_get_usage(usage_service, path_params)

        elif http_method == 'POST':
            body = event.get('body')
            if not body:
                return APIResponse.error('Request body 필수', 400)

            data = json.loads(body) if isinstance(body, str) else body
            return handle_update_usage(usage_service, data)

        else:
            return APIResponse.error('지원하지 않는 HTTP 메서드', 405)

    except Exception as e:
        logger.error(f"Lambda 핸들러 오류: {e}", exc_info=True)
        return APIResponse.error('서버 내부 오류', 500)


def handle_get_usage(
    service: SimpleUsageService,
    path_params: dict
) -> dict:
    """
    사용량 조회 처리

    Args:
        service: SimpleUsageService 인스턴스
        path_params: 경로 파라미터

    Returns:
        API Response
    """
    try:
        user_id = path_params.get('userId')
        engine_type_or_all = path_params.get('engineType')

        # URL 디코딩 처리 (이메일의 @ 등)
        if user_id:
            user_id = unquote(user_id)

        if not user_id:
            return APIResponse.error('userId 필수', 400)

        if engine_type_or_all == 'all':
            # 전체 사용량 조회
            data = service.get_all_usage(user_id)
            return APIResponse.success({
                'success': True,
                'data': data
            })
        else:
            # 특정 엔진 사용량 조회
            data = service.get_usage(user_id, engine_type_or_all)
            return APIResponse.success({
                'success': True,
                'data': data
            })

    except Exception as e:
        logger.error(f"Error in handle_get_usage: {str(e)}", exc_info=True)
        return APIResponse.error(str(e))


def handle_update_usage(
    service: SimpleUsageService,
    data: dict
) -> dict:
    """
    사용량 업데이트 처리

    Args:
        service: SimpleUsageService 인스턴스
        data: 요청 데이터

    Returns:
        API Response
    """
    try:
        user_id = data.get('userId')
        engine_type = data.get('engineType')
        input_text = data.get('inputText', '')
        output_text = data.get('outputText', '')
        user_plan = data.get('userPlan', 'free')

        # 필수 파라미터 검증
        if not all([user_id, engine_type]):
            return APIResponse.error('userId, engineType 필수', 400)

        # 사용량 업데이트
        result = service.update_usage(
            user_id=user_id,
            engine_type=engine_type,
            input_text=input_text,
            output_text=output_text,
            user_plan=user_plan
        )

        return APIResponse.success(result)

    except Exception as e:
        logger.error(f"Error in handle_update_usage: {str(e)}", exc_info=True)
        return APIResponse.error(str(e))
