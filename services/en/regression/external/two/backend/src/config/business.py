"""
비즈니스 로직 설정
사용량 제한, 대화 제한 등 비즈니스 규칙 관련 설정
"""
import os
from decimal import Decimal


# 사용량 플랜 제한
USAGE_LIMITS = {
    'free': {
        'monthly_tokens': int(os.environ.get('FREE_TIER_TOKENS', '10000')),
        'requests_per_day': int(os.environ.get('FREE_TIER_REQUESTS', '100')),
        'max_tokens_per_request': int(os.environ.get('FREE_TIER_MAX_TOKENS', '1000'))
    },
    'basic': {
        'monthly_tokens': int(os.environ.get('BASIC_TIER_TOKENS', '100000')),
        'requests_per_day': int(os.environ.get('BASIC_TIER_REQUESTS', '1000')),
        'max_tokens_per_request': int(os.environ.get('BASIC_TIER_MAX_TOKENS', '5000'))
    },
    'premium': {
        'monthly_tokens': int(os.environ.get('PREMIUM_TIER_TOKENS', '500000')),
        'requests_per_day': int(os.environ.get('PREMIUM_TIER_REQUESTS', '10000')),
        'max_tokens_per_request': int(os.environ.get('PREMIUM_TIER_MAX_TOKENS', '10000'))
    }
}


# 대화 관련 제한
CONVERSATION_LIMITS = {
    # 대화에 저장될 최대 메시지 수 (메모리 관리)
    'max_messages_in_conversation': int(os.environ.get('MAX_CONVERSATION_MESSAGES', '50')),

    # 대화 히스토리 조회 시 기본 제한
    'default_history_limit': int(os.environ.get('DEFAULT_HISTORY_LIMIT', '20')),

    # 클라이언트-DB 병합 시 최대 메시지 수
    'max_merged_messages': int(os.environ.get('MAX_MERGED_MESSAGES', '30')),

    # Bedrock에 전달할 컨텍스트 메시지 수
    'max_bedrock_context_messages': int(os.environ.get('MAX_BEDROCK_CONTEXT', '10')),
}


# 토큰 추정 (문자당 토큰 수)
TOKEN_ESTIMATION = {
    'korean_chars_per_token': float(os.environ.get('KOREAN_CHARS_PER_TOKEN', '2.5')),
    'english_chars_per_token': float(os.environ.get('ENGLISH_CHARS_PER_TOKEN', '4')),
    'other_chars_per_token': float(os.environ.get('OTHER_CHARS_PER_TOKEN', '3')),
    'numbers_chars_per_token': float(os.environ.get('NUMBERS_CHARS_PER_TOKEN', '3.5')),
    'spaces_chars_per_token': float(os.environ.get('SPACES_CHARS_PER_TOKEN', '4')),
    'special_chars_per_token': float(os.environ.get('SPECIAL_CHARS_PER_TOKEN', '3')),
}


# WebSocket 설정
WEBSOCKET_CONFIG = {
    # 메시지 처리 타임아웃 (초)
    'message_timeout': int(os.environ.get('WS_MESSAGE_TIMEOUT', '300')),

    # 최대 메시지 크기 (바이트)
    'max_message_size': int(os.environ.get('WS_MAX_MESSAGE_SIZE', '1048576')),  # 1MB

    # 연결 타임아웃 (초)
    'connection_timeout': int(os.environ.get('WS_CONNECTION_TIMEOUT', '3600')),  # 1시간

    # 연결 TTL (초) - DynamoDB 자동 삭제
    'connection_ttl': int(os.environ.get('WS_CONNECTION_TTL', '86400')),  # 24시간
}


# 엔진 타입 정의 (완전히 환경변수 기반 - 동적 구성)
def _load_engine_types():
    """
    환경변수에서 엔진 설정을 동적으로 로드

    환경변수 형식:
    AVAILABLE_ENGINES=one,two,three
    ENGINE_ONE_NAME=기업 보도자료
    ENGINE_ONE_DESC=기업 보도자료 전문 엔진
    ENGINE_ONE_MODEL_ID=us.anthropic.claude-sonnet-4-20250514-v1:0
    ENGINE_ONE_INPUT_COST=0.003
    ENGINE_ONE_OUTPUT_COST=0.015
    """
    # 사용 가능한 엔진 ID 목록
    available_engines = os.environ.get('AVAILABLE_ENGINES', 'one,two').split(',')
    available_engines = [e.strip() for e in available_engines if e.strip()]

    engine_types = {}

    for engine_id in available_engines:
        # 환경변수 키는 대문자로 변환 (corporate -> CORPORATE)
        env_key = engine_id.upper()

        engine_types[engine_id] = {
            'name': os.environ.get(f'ENGINE_{env_key}_NAME', f'Engine {engine_id}'),
            'description': os.environ.get(f'ENGINE_{env_key}_DESC', f'Engine {engine_id} description'),
            'model_id': os.environ.get(f'ENGINE_{env_key}_MODEL_ID'),
            'input_cost_per_1k': Decimal(os.environ.get(f'ENGINE_{env_key}_INPUT_COST', '0.003')),
            'output_cost_per_1k': Decimal(os.environ.get(f'ENGINE_{env_key}_OUTPUT_COST', '0.015')),
        }

    return engine_types

ENGINE_TYPES = _load_engine_types()

# 기본 엔진 타입
DEFAULT_ENGINE_TYPE = os.environ.get('DEFAULT_ENGINE_TYPE', 'one')

# 사용 가능한 엔진 타입 목록 (동적으로 ENGINE_TYPES에서 가져옴)
AVAILABLE_ENGINE_TYPES = list(ENGINE_TYPES.keys())

# 엔진 가격 (Backward compatibility)
COST_PER_1K_INPUT_TOKENS = {
    engine_id: config['input_cost_per_1k']
    for engine_id, config in ENGINE_TYPES.items()
}
COST_PER_1K_OUTPUT_TOKENS = {
    engine_id: config['output_cost_per_1k']
    for engine_id, config in ENGINE_TYPES.items()
}

# 기본 비용 (엔진 타입을 찾을 수 없을 때)
DEFAULT_INPUT_TOKEN_COST_PER_1K = Decimal('0.003')
DEFAULT_OUTPUT_TOKEN_COST_PER_1K = Decimal('0.015')

# 비용 계산 정밀도
COST_DECIMAL_PRECISION = Decimal('0.0001')


# 관리자 이메일 주소 (특정 이메일만 관리자)
ADMIN_EMAILS = os.environ.get('ADMIN_EMAILS', 'ai@sedaily.com').split(',')


# 데이터베이스 쿼리 제한
DB_QUERY_LIMITS = {
    'max_conversations_query': int(os.environ.get('MAX_CONVERSATIONS_QUERY', '1000')),
    'default_public_prompts_limit': int(os.environ.get('DEFAULT_PUBLIC_PROMPTS_LIMIT', '50')),
    'max_usage_history_days': int(os.environ.get('MAX_USAGE_HISTORY_DAYS', '90')),
}


# 텍스트 처리 설정
TEXT_PROCESSING = {
    'max_conversation_title_length': int(os.environ.get('MAX_TITLE_LENGTH', '50')),
    'default_conversation_title': os.environ.get('DEFAULT_CONVERSATION_TITLE', 'New Conversation'),
}


# 사용량 제한 기본값 (Usage Service용)
USAGE_LIMITS_DEFAULT = {
    'daily': {
        'requests': int(os.environ.get('DAILY_DEFAULT_REQUESTS', '1000')),
        'tokens': int(os.environ.get('DAILY_DEFAULT_TOKENS', '1000000')),
        'cost': os.environ.get('DAILY_DEFAULT_COST', '100.00')
    },
    'monthly': {
        'requests': int(os.environ.get('MONTHLY_DEFAULT_REQUESTS', '30000')),
        'tokens': int(os.environ.get('MONTHLY_DEFAULT_TOKENS', '30000000')),
        'cost': os.environ.get('MONTHLY_DEFAULT_COST', '3000.00')
    }
}


# 시스템 프롬프트 템플릿 변수
SYSTEM_PROMPT_DEFAULTS = {
    'default_user_location': os.environ.get('DEFAULT_USER_LOCATION', '대한민국'),
    'default_timezone': os.environ.get('DEFAULT_TIMEZONE', 'Asia/Seoul (KST)'),
    'default_timezone_offset': int(os.environ.get('DEFAULT_TIMEZONE_OFFSET', '9')),  # UTC+9
    'session_id_length': int(os.environ.get('SESSION_ID_LENGTH', '8')),
    'knowledge_cutoff_date': os.environ.get('KNOWLEDGE_CUTOFF_DATE', '2025년 1월 31일'),
}


def get_usage_limit(plan: str, limit_type: str) -> int:
    """
    사용량 제한 조회

    Args:
        plan: 플랜 이름 (free, basic, premium)
        limit_type: 제한 타입 (monthly_tokens, requests_per_day, max_tokens_per_request)

    Returns:
        제한값
    """
    plan_limits = USAGE_LIMITS.get(plan.lower(), USAGE_LIMITS['free'])
    return plan_limits.get(limit_type, 0)


def get_conversation_limit(limit_type: str) -> int:
    """
    대화 제한 조회

    Args:
        limit_type: 제한 타입

    Returns:
        제한값
    """
    return CONVERSATION_LIMITS.get(limit_type, 0)
