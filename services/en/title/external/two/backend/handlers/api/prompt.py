"""
Prompt CRUD API Handler (Refactored)
프롬프트 관리 REST API 엔드포인트 - Service Layer 사용
"""
import json
from typing import Dict, Any

from src.services import EnginePromptService
from utils.logger import setup_logger
from utils.response import APIResponse

logger = setup_logger(__name__)


def handler(event, context):
    """
    Lambda 핸들러 - 프롬프트 관리 API

    Responsibilities:
    1. 요청 파싱
    2. 서비스 계층 호출
    3. 응답 반환
    """
    logger.info(f"Prompt API Event: {json.dumps(event)}")

    # API Gateway v2 형식 처리
    if 'version' in event and event['version'] == '2.0':
        # API Gateway v2 (HTTP API)
        http_method = event.get('requestContext', {}).get('http', {}).get('method')
        path = event.get('requestContext', {}).get('http', {}).get('path')
        path_params = event.get('pathParameters', {})
    else:
        # API Gateway v1 (REST API) 또는 직접 호출
        http_method = event.get('httpMethod')
        path = event.get('path', '')
        path_params = event.get('pathParameters', {})

    # OPTIONS 요청 처리 (CORS preflight)
    if http_method == 'OPTIONS':
        return APIResponse.cors_preflight()

    try:
        # 요청 본문 파싱
        body = {}
        if event.get('body'):
            body = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
            logger.info(f"Request body: {body}")

        logger.info(f"Method: {http_method}, Path: {path}, PathParams: {path_params}")

        # 서비스 초기화
        prompt_service = EnginePromptService()

        # 라우팅
        if '/prompts' in path:
            if '/files' in path:
                # 파일 관련 작업
                return handle_files(prompt_service, http_method, path_params, body)
            else:
                # 프롬프트 관련 작업
                return handle_prompts(prompt_service, http_method, path_params, body)

        return APIResponse.error('Not Found', 404)

    except Exception as e:
        logger.error(f"Error in handler: {str(e)}", exc_info=True)
        return APIResponse.error(str(e))


def handle_prompts(
    service: EnginePromptService,
    method: str,
    path_params: Dict,
    body: Dict
) -> Dict:
    """
    프롬프트 (설명, 지침) CRUD 처리

    Args:
        service: EnginePromptService 인스턴스
        method: HTTP 메서드
        path_params: 경로 파라미터
        body: 요청 본문

    Returns:
        API Response
    """
    # promptId와 engineType 둘 다 지원 (API Gateway 호환성)
    engine_type = path_params.get('promptId') or path_params.get('engineType')
    logger.info(f"handle_prompts - method: {method}, engine_type: {engine_type}")

    try:
        if method == 'GET':
            # 프롬프트 조회
            if engine_type:
                # 특정 엔진의 프롬프트 조회
                result = service.get_prompt_with_files(engine_type)
                return APIResponse.success(result)
            else:
                # 모든 프롬프트 조회
                prompts = service.get_all_prompts()
                return APIResponse.success({'prompts': prompts})

        elif method == 'POST':
            # 프롬프트 생성 또는 업데이트
            if not engine_type:
                return APIResponse.error('engineType is required', 400)

            prompt = service.create_or_update_prompt(
                engine_type=engine_type,
                description=body.get('description', ''),
                instruction=body.get('instruction', '')
            )

            return APIResponse.success({
                'message': 'Prompt created/updated successfully',
                'promptId': engine_type,
                'prompt': prompt
            })

        elif method == 'PUT':
            # 프롬프트 부분 업데이트
            if not engine_type:
                return APIResponse.error('engineType is required', 400)

            logger.info(f"Updating prompt {engine_type} with body: {body}")

            success = service.update_prompt(
                engine_type=engine_type,
                description=body.get('description'),
                instruction=body.get('instruction')
            )

            if success:
                return APIResponse.success({'message': 'Prompt updated successfully'})
            else:
                return APIResponse.error('Prompt not found', 404)

        elif method == 'DELETE':
            # 프롬프트 삭제
            if not engine_type:
                return APIResponse.error('engineType is required', 400)

            success = service.delete_prompt(engine_type)

            if success:
                return APIResponse.success({'message': 'Prompt deleted successfully'})
            else:
                return APIResponse.error('Prompt not found', 404)

        return APIResponse.error('Method not allowed', 405)

    except Exception as e:
        logger.error(f"Error in handle_prompts: {str(e)}", exc_info=True)
        return APIResponse.error(str(e))


def handle_files(
    service: EnginePromptService,
    method: str,
    path_params: Dict,
    body: Dict
) -> Dict:
    """
    파일 CRUD 처리

    Args:
        service: EnginePromptService 인스턴스
        method: HTTP 메서드
        path_params: 경로 파라미터
        body: 요청 본문

    Returns:
        API Response
    """
    # promptId와 engineType 둘 다 지원 (API Gateway 호환성)
    engine_type = path_params.get('promptId') or path_params.get('engineType')
    file_id = path_params.get('fileId')

    logger.info(f"handle_files - method: {method}, engine_type: {engine_type}, file_id: {file_id}")

    try:
        if method == 'GET':
            # 파일 목록 조회
            if not engine_type:
                return APIResponse.error('engineType is required', 400)

            files = service.get_files(engine_type)
            return APIResponse.success({'files': files})

        elif method == 'POST':
            # 새 파일 추가
            if not engine_type:
                return APIResponse.error('engineType is required', 400)

            file = service.add_file(
                engine_type=engine_type,
                file_name=body.get('fileName', 'untitled.txt'),
                file_content=body.get('fileContent', '')
            )

            return APIResponse.success({'file': file}, 201)

        elif method == 'PUT':
            # 파일 수정
            if not engine_type or not file_id:
                return APIResponse.error('engineType and fileId are required', 400)

            success = service.update_file(
                engine_type=engine_type,
                file_id=file_id,
                file_name=body.get('fileName'),
                file_content=body.get('fileContent')
            )

            if success:
                return APIResponse.success({'message': 'File updated successfully'})
            else:
                return APIResponse.error('No fields to update or file not found', 400)

        elif method == 'DELETE':
            # 파일 삭제
            if not engine_type or not file_id:
                return APIResponse.error('engineType and fileId are required', 400)

            success = service.delete_file(engine_type, file_id)

            if success:
                return APIResponse.success({'message': 'File deleted successfully'})
            else:
                return APIResponse.error('File not found', 404)

        return APIResponse.error('Method not allowed', 405)

    except Exception as e:
        logger.error(f"Error in handle_files: {str(e)}", exc_info=True)
        return APIResponse.error(str(e))
