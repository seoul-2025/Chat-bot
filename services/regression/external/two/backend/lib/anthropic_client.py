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

logger = logging.getLogger(__name__)

# Secrets Manager 클라이언트
secrets_client = boto3.client('secretsmanager', region_name='us-east-1')

def get_api_key_from_secrets():
    """Secrets Manager에서 API 키 가져오기"""
    try:
        secret_name = os.environ.get('ANTHROPIC_SECRET_NAME', 'regression-v1')
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
MODEL_ID = "claude-opus-4-5-20251101"  # Claude 4.5 Opus - 2025년 11월 출시 최고 성능 모델
MAX_TOKENS = 4096
TEMPERATURE = 0.7


def stream_anthropic_response(
    user_message: str,
    system_prompt: str,
    api_key: Optional[str] = None,
    enable_web_search: bool = False
) -> Iterator[str]:
    """
    Anthropic API를 통한 스트리밍 응답 생성
    
    Args:
        user_message: 사용자 메시지
        system_prompt: 시스템 프롬프트
        api_key: API 키 (없으면 환경변수 사용)
        enable_web_search: 웹 검색 기능 활성화
    
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
            "accept": "text/event-stream"
        }
        
        # 요청 본문
        body = {
            "model": MODEL_ID,
            "max_tokens": MAX_TOKENS,
            "temperature": TEMPERATURE,
            "system": system_prompt,
            "messages": [
                {"role": "user", "content": user_message}
            ],
            "stream": True
        }
        
        # 웹 검색 도구 추가
        if enable_web_search:
            body["tools"] = [
                {
                    "type": "web_search_20250305",
                    "name": "web_search",
                    "max_uses": 5  # 최대 5번까지 웹 검색 허용
                }
            ]
            logger.info("웹 검색 기능이 활성화되었습니다")
        
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
        enable_web_search: bool = False
    ) -> Iterator[str]:
        """
        스트리밍 응답 생성
        
        Args:
            user_message: 사용자 메시지
            system_prompt: 시스템 프롬프트
            conversation_context: 대화 컨텍스트
            enable_web_search: 웹 검색 기능 활성화
        
        Yields:
            응답 청크
        """
        try:
            # 대화 컨텍스트 포함
            if conversation_context:
                full_prompt = f"{conversation_context}\n\n{system_prompt}"
            else:
                full_prompt = system_prompt
            
            # 우수사례 적용: 날짜 정보를 user_message에 포함
            enhanced_user_message = self._create_message_with_context(user_message, conversation_context)
            
            logger.info(f"Streaming with Anthropic API")
            
            # Anthropic API 스트리밍
            for chunk in stream_anthropic_response(
                user_message=enhanced_user_message,  # 날짜 정보가 포함된 메시지
                system_prompt=full_prompt,
                api_key=self.api_key,
                enable_web_search=enable_web_search
            ):
                yield chunk
        
        except Exception as e:
            logger.error(f"Error in stream_response: {str(e)}")
            yield f"\n\n[오류] 응답 생성 실패: {str(e)}"
    
    def _create_message_with_context(self, user_message: str, conversation_context: str) -> str:
        """대화 컨텍스트를 메시지에 포함"""
        from datetime import datetime, timezone, timedelta
        
        # 한국 시간 (UTC+9)
        kst = timezone(timedelta(hours=9))
        current_time = datetime.now(kst)
        
        # 동적 컨텍스트 정보
        context_info = f"""[현재 세션 정보]
현재 시간: {current_time.strftime('%Y-%m-%d %H:%M:%S KST')}
사용자 위치: 대한민국
타임존: Asia/Seoul (KST)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""
        
        if conversation_context:
            return f"""{context_info}{conversation_context}

위의 대화 내용을 참고하여 답변해주세요.

사용자의 질문: {user_message}
"""
        return f"""{context_info}사용자의 질문: {user_message}"""