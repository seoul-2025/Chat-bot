"""
Anthropic API 직접 호출 클라이언트
AWS Bedrock 대신 Anthropic API를 직접 사용
Prompt Caching 최적화 적용
"""
import os
import json
import logging
import requests
import boto3
import uuid
from typing import Dict, Any, Iterator, Optional
from datetime import datetime, timezone, timedelta

logger = logging.getLogger(__name__)

# Secrets Manager 클라이언트
secrets_client = boto3.client('secretsmanager', region_name='us-east-1')

def get_api_key_from_secrets():
    """Secrets Manager에서 API 키 가져오기"""
    try:
        secret_name = os.environ.get('ANTHROPIC_SECRET_NAME', 'bodo-v1')
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
OPUS_MODEL = "claude-opus-4-5-20251101"  # Claude 4.5 Opus - 최신 최고 성능 모델 (2024년 11월 출시)
MAX_TOKENS = int(os.environ.get('MAX_TOKENS', '4096'))
TEMPERATURE = float(os.environ.get('TEMPERATURE', '0.3'))

# 웹 검색 설정
ENABLE_NATIVE_WEB_SEARCH = os.environ.get('ENABLE_NATIVE_WEB_SEARCH', 'true').lower() == 'true'

# Prompt Caching 설정
ENABLE_PROMPT_CACHING = os.environ.get('ENABLE_PROMPT_CACHING', 'true').lower() == 'true'
CACHE_TTL = os.environ.get('CACHE_TTL', '1h')  # 기본 1시간

# 한국 시간대
kst = timezone(timedelta(hours=9))


def _replace_template_variables(prompt: str) -> str:
    """정적 값만 치환 (캐싱 최적화)"""
    replacements = {
        '{{user_location}}': '대한민국',
        '{{timezone}}': 'Asia/Seoul (KST)'
    }
    
    for key, value in replacements.items():
        prompt = prompt.replace(key, value)
    
    return prompt


def _create_dynamic_context() -> str:
    """동적 컨텍스트 생성 (user_message에 추가용)"""
    current_time = datetime.now(kst)
    session_id = str(uuid.uuid4())[:8]
    
    return f"""[현재 세션 정보]
- 현재 시간: {current_time.strftime('%Y-%m-%d %H:%M:%S KST')}
- 오늘 날짜: {current_time.strftime('%Y년 %m월 %d일')}
- 세션 ID: {session_id}
"""


def _calculate_cost(usage: Dict[str, int]) -> float:
    """비용 계산 (Claude Opus 4.5 기준)"""
    PRICE_INPUT = 5.0  # Base Input Tokens (per 1M)
    PRICE_OUTPUT = 25.0  # Output Tokens (per 1M)
    PRICE_CACHE_WRITE = 10.0  # 1h Cache Writes (per 1M)
    PRICE_CACHE_READ = 0.50  # Cache Hits (per 1M)
    
    cost_input = (usage.get('input_tokens', 0) / 1_000_000) * PRICE_INPUT
    cost_output = (usage.get('output_tokens', 0) / 1_000_000) * PRICE_OUTPUT
    cost_cache_write = (usage.get('cache_creation_input_tokens', 0) / 1_000_000) * PRICE_CACHE_WRITE
    cost_cache_read = (usage.get('cache_read_input_tokens', 0) / 1_000_000) * PRICE_CACHE_READ
    
    return cost_input + cost_output + cost_cache_write + cost_cache_read


def stream_anthropic_response(
    user_message: str,
    system_prompt: str,
    api_key: Optional[str] = None,
    enable_web_search: bool = False
) -> Iterator[str]:
    """
    Anthropic API를 통한 스트리밍 응답 생성 (Prompt Caching 최적화)
    
    Args:
        user_message: 사용자 메시지
        system_prompt: 시스템 프롬프트
        api_key: API 키 (없으면 환경변수 사용)
    
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
        
        # 요청 헤더
        headers = {
            "x-api-key": api_key,
            "anthropic-version": ANTHROPIC_VERSION,
            "content-type": "application/json",
            "accept": "text/event-stream",
            "anthropic-beta": "prompt-caching-2024-07-31"  # Prompt Caching 베타 헤더
        }
        
        # 정적 컨텍스트는 system_prompt에 포함 (캐싱됨)
        static_system_prompt = _replace_template_variables(system_prompt)
        
        # 동적 컨텍스트는 user_message에 추가 (캐싱 무효화 방지)
        dynamic_context = _create_dynamic_context()
        enhanced_user_message = f"{dynamic_context}\n{user_message}"
        
        # 프롬프트 캐싱 적용 (system만 캐싱)
        api_params = {
            "model": OPUS_MODEL,
            "max_tokens": MAX_TOKENS,
            "temperature": TEMPERATURE,
            "messages": [{"role": "user", "content": enhanced_user_message}],
            "stream": True
        }
        
        # Prompt Caching 적용
        if ENABLE_PROMPT_CACHING:
            api_params["system"] = [
                {
                    "type": "text",
                    "text": static_system_prompt,
                    "cache_control": {"type": "ephemeral", "ttl": CACHE_TTL}  # 1시간 캐시
                }
            ]
            logger.info(f"✅ Prompt caching enabled (TTL: {CACHE_TTL})")
        else:
            api_params["system"] = static_system_prompt
        
        # 웹 검색 도구 설정
        if enable_web_search and ENABLE_NATIVE_WEB_SEARCH:
            api_params["tools"] = [
                {
                    "type": "web_search_20250305",
                    "name": "web_search",
                    "max_uses": 5  # 최대 5번까지 웹 검색 허용
                }
            ]
            logger.info("Web search tool enabled")
        
        logger.info(f"Calling Anthropic API with model: {OPUS_MODEL}")
        if enable_web_search:
            logger.info("Web search enabled for this request")
        
        # API 호출 (스트리밍)
        response = requests.post(
            ANTHROPIC_API_URL,
            headers=headers,
            json=api_params,
            stream=True
        )
        
        # Usage 추적용 변수
        total_usage = {
            'input_tokens': 0,
            'output_tokens': 0,
            'cache_read_input_tokens': 0,
            'cache_creation_input_tokens': 0
        }
        
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
                        
                        # Usage 정보 처리 (message_stop 이벤트)
                        elif data.get('type') == 'message_stop':
                            usage = data.get('usage', {})
                            if usage:
                                total_usage['input_tokens'] = usage.get('input_tokens', 0)
                                total_usage['output_tokens'] = usage.get('output_tokens', 0)
                                total_usage['cache_read_input_tokens'] = usage.get('cache_read_input_tokens', 0)
                                total_usage['cache_creation_input_tokens'] = usage.get('cache_creation_input_tokens', 0)
                                
                                # 비용 계산 및 로깅
                                cost = _calculate_cost(total_usage)
                                logger.info(f"💰 API Cost: ${cost:.6f} | "
                                          f"input: {total_usage['input_tokens']}, "
                                          f"output: {total_usage['output_tokens']}, "
                                          f"cache_read: {total_usage['cache_read_input_tokens']}, "
                                          f"cache_write: {total_usage['cache_creation_input_tokens']}")
                        
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
    """Anthropic API 직접 호출 클라이언트 (Prompt Caching 최적화)"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Args:
            api_key: Anthropic API 키 (없으면 Secrets Manager에서 가져옴)
        """
        self.api_key = api_key or get_api_key_from_secrets()
        if not self.api_key:
            logger.warning("Anthropic API key not set")
        
        self.last_usage = {}  # 마지막 API 호출의 usage 정보 저장
        logger.info("AnthropicClient initialized with Prompt Caching support")
    
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
        
        Yields:
            응답 청크
        """
        try:
            # 대화 컨텍스트 포함
            if conversation_context:
                full_prompt = f"{conversation_context}\n\n{system_prompt}"
            else:
                full_prompt = system_prompt
            
            logger.info(f"Streaming with Anthropic API")
            
            # 웹 검색 설정 결정
            if enable_web_search is None:
                enable_web_search = ENABLE_NATIVE_WEB_SEARCH
            
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
    
    def get_last_usage(self) -> Dict[str, Any]:
        """마지막 API 호출의 usage 정보 반환"""
        return self.last_usage.copy()
    
    def _calculate_cost(self, usage: Dict[str, int]) -> float:
        """비용 계산 (인스턴스 메서드)"""
        return _calculate_cost(usage)