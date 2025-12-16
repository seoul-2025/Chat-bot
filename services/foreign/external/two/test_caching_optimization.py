#!/usr/bin/env python3
"""
F1 서비스 캐싱 최적화 테스트
- Prompt Caching 동작 확인
- 비용 계산 검증
- Lambda 영구 캐싱 테스트
"""
import sys
import os
import json
import time

# 경로 설정
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

# 환경변수 설정
os.environ['ANTHROPIC_SECRET_NAME'] = 'foreign-v1'
os.environ['ANTHROPIC_MODEL_ID'] = 'claude-opus-4-5-20251101'
os.environ['MAX_TOKENS'] = '4096'
os.environ['TEMPERATURE'] = '0.3'
os.environ['USE_ANTHROPIC_API'] = 'true'
os.environ['ENABLE_NATIVE_WEB_SEARCH'] = 'false'
os.environ['PROMPTS_TABLE'] = 'f1-prompts-two'
os.environ['FILES_TABLE'] = 'f1-files-two'


def test_anthropic_client_caching():
    """AnthropicClient 캐싱 테스트"""
    print("\n=== Anthropic Client Caching Test ===")
    
    from backend.lib.anthropic_client import AnthropicClient
    
    client = AnthropicClient()
    
    # 테스트용 프롬프트
    system_prompt = """당신은 AI 어시스턴트입니다.
    사용자 위치: {{user_location}}
    타임존: {{timezone}}
    """
    
    user_message = "안녕하세요. 오늘 날짜와 시간을 알려주세요."
    
    # 첫 번째 호출 (캐시 생성)
    print("\n1. First API call (cache write)...")
    result1 = client.call_api_with_caching(
        user_message=user_message,
        system_prompt=system_prompt,
        enable_web_search=False
    )
    
    if 'error' not in result1:
        print(f"✅ First call successful")
        if client.last_usage:
            print(f"   - Input tokens: {client.last_usage.get('input_tokens', 0)}")
            print(f"   - Cache write: {client.last_usage.get('cache_creation_input_tokens', 0)}")
            print(f"   - Cost: ${client.last_usage.get('total_cost', 0):.6f}")
    else:
        print(f"❌ Error: {result1['error']}")
    
    time.sleep(2)
    
    # 두 번째 호출 (캐시 히트 기대)
    print("\n2. Second API call (cache read expected)...")
    result2 = client.call_api_with_caching(
        user_message="현재 시간은 몇 시인가요?",
        system_prompt=system_prompt,
        enable_web_search=False
    )
    
    if 'error' not in result2:
        print(f"✅ Second call successful")
        if client.last_usage:
            print(f"   - Input tokens: {client.last_usage.get('input_tokens', 0)}")
            print(f"   - Cache read: {client.last_usage.get('cache_read_input_tokens', 0)}")
            print(f"   - Cost: ${client.last_usage.get('total_cost', 0):.6f}")
    else:
        print(f"❌ Error: {result2['error']}")
    
    print(f"\n📊 Total API cost: ${client.total_cost:.6f}")


def test_websocket_service_caching():
    """WebSocketService 영구 캐싱 테스트"""
    print("\n=== WebSocket Service Permanent Caching Test ===")
    
    from backend.services.websocket_service import WebSocketService, PROMPT_CACHE
    
    service = WebSocketService()
    engine_type = 'foreign_writer'
    
    # 첫 번째 프롬프트 로드 (캐시 미스)
    print(f"\n1. First load for {engine_type} (cache miss expected)...")
    prompt_data1 = service._load_prompt_from_dynamodb(engine_type)
    print(f"   - Loaded: {len(prompt_data1.get('files', []))} files")
    print(f"   - Cache state: {list(PROMPT_CACHE.keys())}")
    
    # 두 번째 프롬프트 로드 (캐시 히트)
    print(f"\n2. Second load for {engine_type} (cache hit expected)...")
    prompt_data2 = service._load_prompt_from_dynamodb(engine_type)
    print(f"   - Loaded from cache: {prompt_data1 is prompt_data2}")
    print(f"   - Cache entries: {len(PROMPT_CACHE)}")
    
    # 다른 엔진 타입 테스트
    another_engine = 'foreign_reporter'
    print(f"\n3. Load different engine {another_engine}...")
    prompt_data3 = service._load_prompt_from_dynamodb(another_engine)
    print(f"   - Cache entries now: {len(PROMPT_CACHE)}")
    print(f"   - Cached engines: {list(PROMPT_CACHE.keys())}")


def test_cost_calculation():
    """비용 계산 로직 테스트"""
    print("\n=== Cost Calculation Test ===")
    
    from backend.lib.anthropic_client import AnthropicClient
    
    client = AnthropicClient()
    
    # 테스트 케이스
    test_cases = [
        {
            'name': 'Normal request',
            'usage': {
                'input_tokens': 1000,
                'output_tokens': 500,
                'cache_read_input_tokens': 0,
                'cache_creation_input_tokens': 0
            },
            'expected_cost': (1000/1_000_000 * 5.0) + (500/1_000_000 * 25.0)  # $0.0175
        },
        {
            'name': 'First request with cache write',
            'usage': {
                'input_tokens': 0,
                'output_tokens': 500,
                'cache_read_input_tokens': 0,
                'cache_creation_input_tokens': 2000
            },
            'expected_cost': (2000/1_000_000 * 10.0) + (500/1_000_000 * 25.0)  # $0.0325
        },
        {
            'name': 'Cached request',
            'usage': {
                'input_tokens': 0,
                'output_tokens': 500,
                'cache_read_input_tokens': 2000,
                'cache_creation_input_tokens': 0
            },
            'expected_cost': (2000/1_000_000 * 0.5) + (500/1_000_000 * 25.0)  # $0.0135
        }
    ]
    
    for test_case in test_cases:
        cost = client._calculate_cost(test_case['usage'])
        expected = test_case['expected_cost']
        status = "✅" if abs(cost - expected) < 0.0001 else "❌"
        
        print(f"\n{test_case['name']}:")
        print(f"   - Usage: {test_case['usage']}")
        print(f"   - Calculated: ${cost:.6f}")
        print(f"   - Expected: ${expected:.6f}")
        print(f"   - {status} {'Passed' if status == '✅' else 'Failed'}")
        
        # 절감률 계산 (캐시된 요청의 경우)
        if test_case['usage']['cache_read_input_tokens'] > 0:
            base_cost = (test_case['usage']['cache_read_input_tokens']/1_000_000 * 5.0) + \
                       (test_case['usage']['output_tokens']/1_000_000 * 25.0)
            savings = (1 - cost/base_cost) * 100
            print(f"   - 💰 Cost savings: {savings:.1f}%")


if __name__ == '__main__':
    print("=" * 60)
    print("F1 Service Caching Optimization Test Suite")
    print("=" * 60)
    
    try:
        # 비용 계산 테스트
        test_cost_calculation()
        
        # WebSocket 서비스 캐싱 테스트 (로컬에서만)
        if 'AWS_LAMBDA_FUNCTION_NAME' not in os.environ:
            test_websocket_service_caching()
        
        # Anthropic API 테스트 (API 키가 있는 경우만)
        # test_anthropic_client_caching()  # 실제 API 호출이므로 주석 처리
        
        print("\n" + "=" * 60)
        print("✅ All tests completed!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()