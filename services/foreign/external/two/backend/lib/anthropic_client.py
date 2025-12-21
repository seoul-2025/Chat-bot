"""
Anthropic API 직접 호출 클라이언트
AWS Bedrock 대신 Anthropic API를 직접 사용
Prompt Caching 최적화 적용
"""
import os
import json
import requests
import boto3
import uuid
from typing import Dict, Any, Iterator, Optional, List
from datetime import datetime, timezone, timedelta

from utils.logger import setup_logger

logger = setup_logger(__name__)

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


def _replace_template_variables(prompt: str) -> str:
    """정적 값만 치환 (캐싱 최적화)"""
    replacements = {
        '{{user_location}}': '대한민국',
        '{{timezone}}': 'Asia/Seoul (KST)'
    }
    
    result = prompt
    for key, value in replacements.items():
        result = result.replace(key, value)
    
    return result


def _create_dynamic_context() -> str:
    """동적 컨텍스트 생성 (user_message에 추가용) - 캐싱 최적화를 위해 여기에만 동적 정보 포함"""
    kst = timezone(timedelta(hours=9))
    current_time = datetime.now(kst)

    return f"""[⚠️ 중요: 현재 세션 정보 - 반드시 참고하세요]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📅 현재 연도: {current_time.year}년
📅 오늘 날짜: {current_time.strftime('%Y년 %m월 %d일')}
🕐 현재 시간: {current_time.strftime('%Y-%m-%d %H:%M:%S KST')}
📍 사용자 위치: 대한민국 (Asia/Seoul)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️ 중요: 응답에서 날짜나 연도를 언급할 때 반드시 위의 현재 날짜 정보를 사용하세요.
2024년이라고 하지 마세요. 현재는 {current_time.year}년입니다.

"""


def get_dynamic_context():
    """동적 컨텍스트 정보 생성 (레거시 호환성)"""
    return _create_dynamic_context()


def stream_anthropic_response(
    user_message: str,
    system_prompt: str,
    api_key: Optional[str] = None,
    enable_web_search: bool = None,
    conversation_history: List[Dict] = None
) -> Iterator[str]:
    """
    Anthropic API를 통한 스트리밍 응답 생성 (Prompt Caching 적용)

    Args:
        user_message: 사용자 메시지
        system_prompt: 시스템 프롬프트 (캐싱을 위해 정적으로 유지)
        api_key: API 키 (없으면 환경변수 사용)
        enable_web_search: 웹 검색 기능 활성화 여부
        conversation_history: 대화 히스토리 리스트 (messages 배열로 변환됨)

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
        
        # 정적 컨텍스트는 system_prompt에 (캐싱용), 동적 컨텍스트는 user_message에
        static_system_prompt = _replace_template_variables(system_prompt)
        dynamic_context = _create_dynamic_context()
        enhanced_user_message = f"{dynamic_context}\n\n{user_message}"

        # 대화 히스토리에서 messages 배열 구성 (캐싱 최적화)
        messages = []
        if conversation_history:
            for msg in conversation_history:
                role = msg.get('role', 'user')
                content = msg.get('content', '')
                if content and role in ['user', 'assistant']:
                    messages.append({"role": role, "content": content})

        # 현재 사용자 메시지 추가 (동적 컨텍스트 포함)
        messages.append({"role": "user", "content": enhanced_user_message})

        logger.info(f"📨 Messages array built: {len(messages)} messages (history: {len(conversation_history) if conversation_history else 0})")

        # 요청 헤더
        headers = {
            "x-api-key": api_key,
            "anthropic-version": ANTHROPIC_VERSION,
            "content-type": "application/json",
            "accept": "text/event-stream",
            "anthropic-beta": "prompt-caching-2024-07-31"  # 캐싱 베타 기능 활성화
        }

        # 프롬프트 캐싱 적용 (system만 캐싱 - 대화 히스토리는 messages로 분리)
        body = {
            "model": MODEL_ID,
            "max_tokens": MAX_TOKENS,
            "temperature": TEMPERATURE,
            "system": [
                {
                    "type": "text",
                    "text": static_system_prompt,
                    "cache_control": { "type": "ephemeral", "ttl": "1h" }  # 1시간 캐시
                }
            ],
            "messages": messages,
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

        # Usage 추적용 변수
        usage_info = {
            'input_tokens': 0,
            'output_tokens': 0,
            'cache_read_input_tokens': 0,
            'cache_creation_input_tokens': 0
        }

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

                        # message_delta에서 usage 정보 추출 (캐시 효과 확인용)
                        elif data.get('type') == 'message_delta':
                            usage = data.get('usage', {})
                            if usage:
                                usage_info['output_tokens'] = usage.get('output_tokens', 0)

                        # message_start에서 초기 usage 정보 추출
                        elif data.get('type') == 'message_start':
                            message = data.get('message', {})
                            usage = message.get('usage', {})
                            if usage:
                                usage_info['input_tokens'] = usage.get('input_tokens', 0)
                                usage_info['cache_read_input_tokens'] = usage.get('cache_read_input_tokens', 0)
                                usage_info['cache_creation_input_tokens'] = usage.get('cache_creation_input_tokens', 0)

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

        # 스트리밍 완료 후 캐시 효과 로깅
        cache_read = usage_info.get('cache_read_input_tokens', 0)
        cache_write = usage_info.get('cache_creation_input_tokens', 0)
        input_tokens = usage_info.get('input_tokens', 0)
        output_tokens = usage_info.get('output_tokens', 0)

        if cache_read > 0 or cache_write > 0:
            # 캐시 HIT/MISS 판정
            if cache_read > 0:
                logger.info(f"🎯 PROMPT CACHE HIT! cache_read: {cache_read} tokens")
            else:
                logger.info(f"📝 PROMPT CACHE MISS - cache_write: {cache_write} tokens (next request will hit)")

            # 비용 절감 계산 (캐시 읽기는 90% 할인)
            savings = (cache_read / 1_000_000) * (5.0 - 0.50)  # $5 -> $0.50 per 1M tokens
            logger.info(f"💰 Token Usage: input={input_tokens}, output={output_tokens}, "
                       f"cache_read={cache_read}, cache_write={cache_write}")
            if savings > 0:
                logger.info(f"💵 Estimated savings from cache: ${savings:.6f}")
        else:
            logger.info(f"📊 Token Usage: input={input_tokens}, output={output_tokens} (no cache info)")
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error: {str(e)}")
        yield f"\n\n[오류] 네트워크 오류: {str(e)}"
    
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        yield f"\n\n[오류] 예상치 못한 오류: {str(e)}"


class AnthropicClient:
    """Anthropic API 직접 호출 클라이언트 (Prompt Caching 및 비용 추적)"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Args:
            api_key: Anthropic API 키 (없으면 Secrets Manager에서 가져옴)
        """
        self.api_key = api_key or get_api_key_from_secrets()
        if not self.api_key:
            logger.warning("Anthropic API key not set")
        
        # 모델 설정
        self.model_id = MODEL_ID
        self.max_tokens = MAX_TOKENS
        self.temperature = TEMPERATURE
        
        # Usage 추적
        self.last_usage = {}
        self.total_cost = 0.0
        
        logger.info(f"AnthropicClient initialized with model: {self.model_id}")
    
    def _calculate_cost(self, usage: Dict[str, int]) -> float:
        """비용 계산 (Claude Opus 4.5 기준)"""
        # 가격 정보 (달러 per 1M tokens)
        PRICE_INPUT = 5.0  # Base Input Tokens
        PRICE_OUTPUT = 25.0  # Output Tokens  
        PRICE_CACHE_WRITE = 10.0  # 1h Cache Writes
        PRICE_CACHE_READ = 0.50  # Cache Hits
        
        cost_input = (usage.get('input_tokens', 0) / 1_000_000) * PRICE_INPUT
        cost_output = (usage.get('output_tokens', 0) / 1_000_000) * PRICE_OUTPUT
        cost_cache_write = (usage.get('cache_creation_input_tokens', 0) / 1_000_000) * PRICE_CACHE_WRITE
        cost_cache_read = (usage.get('cache_read_input_tokens', 0) / 1_000_000) * PRICE_CACHE_READ
        
        total_cost = cost_input + cost_output + cost_cache_write + cost_cache_read
        
        return total_cost
    
    def stream_response(
        self,
        user_message: str,
        system_prompt: str,
        conversation_history: List[Dict] = None,
        enable_web_search: bool = None
    ) -> Iterator[str]:
        """
        스트리밍 응답 생성 (캐싱 최적화 적용)

        Args:
            user_message: 사용자 메시지
            system_prompt: 시스템 프롬프트 (정적 - 캐싱 대상)
            conversation_history: 대화 히스토리 리스트 (messages 배열로 전달)
            enable_web_search: 웹 검색 기능 활성화 여부

        Yields:
            응답 청크
        """
        try:
            # 캐싱 최적화: system_prompt는 정적으로 유지, 대화 히스토리는 messages로 전달
            logger.info(f"Streaming with Anthropic API (Web search: {enable_web_search if enable_web_search is not None else ENABLE_WEB_SEARCH})")
            logger.info(f"📝 System prompt length: {len(system_prompt)} chars (static for caching)")

            # Anthropic API 스트리밍 - 대화 히스토리는 messages로 전달
            for chunk in stream_anthropic_response(
                user_message=user_message,
                system_prompt=system_prompt,
                api_key=self.api_key,
                enable_web_search=enable_web_search,
                conversation_history=conversation_history
            ):
                yield chunk

        except Exception as e:
            logger.error(f"Error in stream_response: {str(e)}")
            yield f"\n\n[오류] 응답 생성 실패: {str(e)}"
    
    def call_api_with_caching(
        self,
        user_message: str,
        system_prompt: str,
        enable_web_search: bool = None
    ) -> Dict[str, Any]:
        """
        Non-streaming API 호출 with prompt caching and usage tracking
        
        Returns:
            Dict with response content and usage info
        """
        try:
            # API 키 확인
            if not self.api_key:
                return {"error": "API key not set"}
            
            # 정적/동적 컨텍스트 분리
            static_system_prompt = _replace_template_variables(system_prompt)
            dynamic_context = _create_dynamic_context()
            enhanced_user_message = f"{dynamic_context}\n\n{user_message}"
            
            # 요청 헤더
            headers = {
                "x-api-key": self.api_key,
                "anthropic-version": ANTHROPIC_VERSION,
                "content-type": "application/json",
                "anthropic-beta": "prompt-caching-2024-07-31"
            }
            
            # 프롬프트 캐싱 적용
            api_params = {
                "model": self.model_id,
                "max_tokens": self.max_tokens,
                "temperature": self.temperature,
                "messages": [{"role": "user", "content": enhanced_user_message}],
                "system": [
                    {
                        "type": "text",
                        "text": static_system_prompt,
                        "cache_control": { "type": "ephemeral", "ttl": "1h" }
                    }
                ]
            }
            
            # 웹 검색 도구 추가
            if enable_web_search if enable_web_search is not None else ENABLE_WEB_SEARCH:
                api_params["tools"] = [
                    {
                        "type": "web_search_20250305",
                        "name": "web_search",
                        "max_uses": WEB_SEARCH_MAX_USES
                    }
                ]
            
            # API 호출
            response = requests.post(
                ANTHROPIC_API_URL,
                headers=headers,
                json=api_params
            )
            
            if response.status_code != 200:
                return {"error": f"API error: {response.status_code} - {response.text}"}
            
            result = response.json()
            
            # Usage 정보 추출 및 저장
            if 'usage' in result:
                usage = result['usage']
                cache_read = usage.get('cache_read_input_tokens', 0)
                cache_write = usage.get('cache_creation_input_tokens', 0)
                
                self.last_usage = {
                    'input_tokens': usage.get('input_tokens', 0),
                    'output_tokens': usage.get('output_tokens', 0),
                    'cache_read_input_tokens': cache_read,
                    'cache_creation_input_tokens': cache_write
                }
                
                # 비용 계산 및 로깅
                cost = self._calculate_cost(self.last_usage)
                self.last_usage['total_cost'] = cost
                self.total_cost += cost
                
                logger.info(f"💰 API Cost: ${cost:.6f} | "
                           f"input: {self.last_usage['input_tokens']}, "
                           f"output: {self.last_usage['output_tokens']}, "
                           f"cache_read: {cache_read}, cache_write: {cache_write}")
                
                # 캐시 효율성 로깅
                if cache_read > 0:
                    cache_hit_ratio = cache_read / (cache_read + cache_write) if (cache_read + cache_write) > 0 else 0
                    logger.info(f"🎯 Cache Hit Ratio: {cache_hit_ratio:.2%}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error in call_api_with_caching: {str(e)}")
            return {"error": str(e)}