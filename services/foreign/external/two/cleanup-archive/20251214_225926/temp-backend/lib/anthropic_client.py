"""
Anthropic API 직접 호출 클라이언트
AWS Bedrock 대신 Anthropic API를 직접 사용
"""
import os
import json
import logging
import requests
import boto3
from typing import Dict, Any, Iterator, Optional
from datetime import datetime, timezone, timedelta

logger = logging.getLogger(__name__)

# Secrets Manager 클라이언트
secrets_client = boto3.client('secretsmanager', region_name='us-east-1')

def get_api_key_from_secrets():
    """Secrets Manager에서 API 키 가져오기"""
    try:
        secret_name = os.environ.get('ANTHROPIC_SECRET_NAME', 'foreign-v1')
        response = secrets_client.get_secret_value(SecretId=secret_name)
        secret = json.loads(response['SecretString'])
        return secret.get('api_key', '')
    except Exception as e:
        logger.error(f"Failed to retrieve API key from Secrets Manager: {str(e)}")
        # 폴백: 환경변수에서 가져오기
        return os.environ.get('ANTHROPIC_API_KEY', '')

# Anthropic API 설정
ANTHROPIC_API_KEY = None  # 요청 시점에 동적으로 가져옴
ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"
ANTHROPIC_VERSION = "2023-06-01"

# 모델 설정
MODEL_ID = os.environ.get('ANTHROPIC_MODEL_ID', "claude-opus-4-5-20251101")  # Claude 4.5 Opus - 최신 최고 성능 모델
MAX_TOKENS = int(os.environ.get('MAX_TOKENS', '4096'))
TEMPERATURE = float(os.environ.get('TEMPERATURE', '0.3'))

# 웹 검색 설정
ENABLE_WEB_SEARCH = os.environ.get('ENABLE_NATIVE_WEB_SEARCH', 'true').lower() == 'true'
WEB_SEARCH_MAX_USES = int(os.environ.get('WEB_SEARCH_MAX_USES', '5'))


def get_dynamic_context():
    """동적 컨텍스트 정보 생성"""
    kst = timezone(timedelta(hours=9))
    current_time = datetime.now(kst)
    
    context_info = f"""[현재 세션 정보]
현재 시간: {current_time.strftime('%Y-%m-%d %H:%M:%S KST')}
오늘 날짜: {current_time.strftime('%Y년 %m월 %d일')}
사용자 위치: 대한민국
타임존: Asia/Seoul (KST)

중요: 응답 시 반드시 현재 연도 {current_time.year}년을 기준으로 작성하세요.
"""
    return context_info


def stream_anthropic_response(
    user_message: str,
    system_prompt: str,
    api_key: Optional[str] = None,
    enable_web_search: bool = None
) -> Iterator[str]:
    """
    Anthropic API를 통한 스트리밍 응답 생성
    
    Args:
        user_message: 사용자 메시지
        system_prompt: 시스템 프롬프트
        api_key: API 키 (없으면 환경변수 사용)
        enable_web_search: 웹 검색 기능 활성화 여부
    
    Yields:
        응답 텍스트 청크
    """
    try:
        # API 키 확인 (Secrets Manager에서 가져오기)
        api_key = api_key or get_api_key_from_secrets()
        if not api_key:
            logger.error("Anthropic API key not found")
            yield "[오류] API 키가 설정되지 않았습니다."
            return
        
        # 동적 컨텍스트 추가
        dynamic_context = get_dynamic_context()
        enhanced_system_prompt = f"{dynamic_context}\n\n{system_prompt}"
        
        # 요청 헤더
        headers = {
            "x-api-key": api_key,
            "anthropic-version": ANTHROPIC_VERSION,
            "content-type": "application/json",
            "accept": "text/event-stream"
        }
        
        # 요청 본문
        body = {
            "model": MODEL_ID,
            "max_tokens": MAX_TOKENS,
            "temperature": TEMPERATURE,
            "system": enhanced_system_prompt,
            "messages": [
                {"role": "user", "content": user_message}
            ],
            "stream": True
        }
        
        # 웹 검색 도구 추가
        if enable_web_search if enable_web_search is not None else ENABLE_WEB_SEARCH:
            body["tools"] = [
                {
                    "type": "web_search_20250305",
                    "name": "web_search",
                    "max_uses": WEB_SEARCH_MAX_USES
                }
            ]
            logger.info(f"Web search enabled with max {WEB_SEARCH_MAX_USES} uses")
        
        logger.info(f"Calling Anthropic API with model: {MODEL_ID}")
        
        # API 호출 (스트리밍)
        response = requests.post(
            ANTHROPIC_API_URL,
            headers=headers,
            json=body,
            stream=True
        )
        
        if response.status_code != 200:
            error_msg = f"API 오류: {response.status_code} - {response.text}"
            logger.error(error_msg)
            yield f"[오류] {error_msg}"
            return
        
        # 스트리밍 응답 처리
        for line in response.iter_lines():
            if line:
                line_text = line.decode('utf-8')
                
                # SSE 형식 파싱
                if line_text.startswith('data: '):
                    data_str = line_text[6:]  # 'data: ' 제거
                    
                    if data_str == '[DONE]':
                        logger.info("Streaming completed")
                        break
                    
                    try:
                        data = json.loads(data_str)
                        
                        # 컨텐츠 블록 델타 처리
                        if data.get('type') == 'content_block_delta':
                            delta = data.get('delta', {})
                            if delta.get('type') == 'text_delta':
                                text = delta.get('text', '')
                                if text:
                                    yield text
                        
                        # 에러 처리
                        elif data.get('type') == 'error':
                            error = data.get('error', {})
                            error_msg = error.get('message', '알 수 없는 오류')
                            logger.error(f"API Error: {error_msg}")
                            yield f"\n\n[오류] {error_msg}"
                            break
                    
                    except json.JSONDecodeError as e:
                        logger.warning(f"Failed to parse SSE data: {e}")
                        continue
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error: {str(e)}")
        yield f"\n\n[오류] 네트워크 오류: {str(e)}"
    
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        yield f"\n\n[오류] 예상치 못한 오류: {str(e)}"


class AnthropicClient:
    """Anthropic API 직접 호출 클라이언트"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Args:
            api_key: Anthropic API 키 (없으면 Secrets Manager에서 가져옴)
        """
        self.api_key = api_key or get_api_key_from_secrets()
        if not self.api_key:
            logger.warning("Anthropic API key not set")
        
        logger.info("AnthropicClient initialized")
    
    def stream_response(
        self,
        user_message: str,
        system_prompt: str,
        conversation_context: str = "",
        enable_web_search: bool = None
    ) -> Iterator[str]:
        """
        스트리밍 응답 생성
        
        Args:
            user_message: 사용자 메시지
            system_prompt: 시스템 프롬프트
            conversation_context: 대화 컨텍스트
            enable_web_search: 웹 검색 기능 활성화 여부
        
        Yields:
            응답 청크
        """
        try:
            # 대화 컨텍스트 포함
            if conversation_context:
                full_prompt = f"{conversation_context}\n\n{system_prompt}"
            else:
                full_prompt = system_prompt
            
            logger.info(f"Streaming with Anthropic API (Web search: {enable_web_search if enable_web_search is not None else ENABLE_WEB_SEARCH})")
            
            # Anthropic API 스트리밍
            for chunk in stream_anthropic_response(
                user_message=user_message,
                system_prompt=full_prompt,
                api_key=self.api_key,
                enable_web_search=enable_web_search
            ):
                yield chunk
        
        except Exception as e:
            logger.error(f"Error in stream_response: {str(e)}")
            yield f"\n\n[오류] 응답 생성 실패: {str(e)}"