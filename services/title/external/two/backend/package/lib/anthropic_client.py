"""
Anthropic API 직접 호출 클라이언트
AWS Bedrock 대신 Anthropic API를 직접 사용
AWS Secrets Manager와 통합하여 API 키를 안전하게 관리
"""
import os
import json
import logging
import requests
import boto3
from typing import Dict, Any, Iterator, Optional
from functools import lru_cache
from botocore.exceptions import ClientError
from datetime import datetime, timezone, timedelta

logger = logging.getLogger(__name__)

# Secrets Manager 클라이언트
secrets_client = boto3.client('secretsmanager', region_name='us-east-1')

@lru_cache(maxsize=1)
def get_api_key_from_secrets():
    """
    Secrets Manager에서 API 키 가져오기 (캐싱 적용)
    Secret Name: title-v1
    """
    try:
        # 업데이트된 시크릿 이름 사용
        secret_name = os.environ.get('ANTHROPIC_SECRET_NAME', 'title-v1')
        logger.info(f"Retrieving API key from Secrets Manager: {secret_name}")
        
        response = secrets_client.get_secret_value(SecretId=secret_name)
        secret = json.loads(response['SecretString'])
        
        # 새로운 시크릿 구조에 맞게 업데이트
        api_key = secret.get('ANTHROPIC_API_KEY', secret.get('api_key', ''))
        
        if api_key:
            logger.info("Successfully retrieved API key from Secrets Manager")
            # 모델 정보도 시크릿에서 가져오기 (있는 경우)
            global MODEL_ID
            if 'model' in secret:
                MODEL_ID = secret['model']
                logger.info(f"Using model from secret: {MODEL_ID}")
        else:
            logger.warning("API key not found in secret")
            
        return api_key
    except ClientError as e:
        error_code = e.response.get('Error', {}).get('Code', '')
        if error_code == 'ResourceNotFoundException':
            logger.error(f"Secret '{secret_name}' not found in Secrets Manager")
        elif error_code == 'AccessDeniedException':
            logger.error(f"Access denied to secret '{secret_name}'. Check IAM permissions.")
        else:
            logger.error(f"AWS Client Error: {str(e)}")
    except Exception as e:
        logger.error(f"Failed to retrieve API key from Secrets Manager: {str(e)}")
    
    # 폴백: 환경변수에서 가져오기
    api_key = os.environ.get('ANTHROPIC_API_KEY', '')
    if api_key:
        logger.info("Using API key from environment variable (fallback)")
    return api_key

# Anthropic API 설정
ANTHROPIC_API_KEY = None  # 요청 시점에 동적으로 가져옴
ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"
ANTHROPIC_VERSION = "2023-06-01"

# 모델 설정 (Secrets Manager에서 override 가능)
MODEL_ID = "claude-opus-4-5-20251101"  # Claude 4.5 Opus - 최신 최고 성능 모델
MAX_TOKENS = 4096
TEMPERATURE = 0.3  # 웹 검색 기능 활성화 시 더 정확한 응답을 위해 온도 낮춤


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
        
        # 웹 검색 도구 설정
        if enable_web_search:
            body["tools"] = [
                {
                    "type": "web_search_20250305",
                    "name": "web_search",
                    "max_uses": 5  # 최대 5번까지 웹 검색 허용
                }
            ]
        
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


def enhance_system_prompt_with_context(system_prompt: str, enable_web_search: bool = False) -> str:
    """
    시스템 프롬프트에 날짜 정보와 웹 검색 지침 추가
    """
    # 동적 날짜 생성
    kst = timezone(timedelta(hours=9))
    current_time = datetime.now(kst)
    
    context_info = f"""[중요: 현재 세션 정보]
⚠️ 현재 연도: {current_time.year}년 
⚠️ 오늘 날짜: {current_time.strftime('%Y년 %m월 %d일')}
⚠️ 현재 시간: {current_time.strftime('%Y-%m-%d %H:%M:%S KST')}
사용자 위치: 대한민국
타임존: Asia/Seoul (KST)

중요: 응답할 때 반드시 현재 연도 {current_time.year}년을 사용하세요. 2024년이라고 하지 마세요.

"""
    
    # 웹 검색 지침
    web_search_instructions = ""
    if enable_web_search:
        web_search_instructions = f"""
### 📚 웹 검색 출처 표시 (필수)
웹 검색 결과 사용 시 반드시:
1. **정확한 연도 표시**: 오늘은 {current_time.year}년 {current_time.month}월 {current_time.day}일입니다. 2024년이라고 하지 마세요.
2. **인라인 각주**: 정보 제공 시 [1], [2] 형식으로 번호 표시
3. **출처 섹션**: 응답 마지막에 다음 형식으로 출처 명시
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   📚 출처:
   [1] 언론사/사이트명 - 제목 (URL)
   [2] 언론사/사이트명 - 제목 (URL)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
4. **신뢰도 표시**:
   - 공식 언론사: ✅
   - 정부/공공기관: 🏛️
   - 일반 웹사이트: ℹ️

⚠️ 중요: 제목에서 "{current_time.year}년 {current_time.month}월 {current_time.day}일"을 사용하세요. 2024년이라고 하지 마세요.

"""
    
    enhanced_prompt = context_info + web_search_instructions + system_prompt
    return enhanced_prompt


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
        
        Yields:
            응답 청크
        """
        try:
            # 시스템 프롬프트 강화 (날짜 정보 + 웹 검색 지침)
            enhanced_prompt = enhance_system_prompt_with_context(
                system_prompt=system_prompt,
                enable_web_search=enable_web_search
            )
            
            # 대화 컨텍스트 포함
            if conversation_context:
                full_prompt = f"{conversation_context}\n\n{enhanced_prompt}"
            else:
                full_prompt = enhanced_prompt
            
            logger.info(f"Streaming with Anthropic API")
            
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