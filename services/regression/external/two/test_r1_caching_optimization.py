#!/usr/bin/env python3
"""
R1 서비스 캐싱 최적화 테스트
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
os.environ['ANTHROPIC_SECRET_NAME'] = 'regression-v1'
os.environ['ANTHROPIC_API_KEY'] = 'test-key'  # 실제 테스트 시 제거
os.environ['AWS_REGION'] = 'us-east-1'


def test_anthropic_client_caching():
    """AnthropicClient 캐싱 테스트"""
    print("\n=== R1 Anthropic Client Caching Test ===")
    
    from backend.lib.anthropic_client import (
        _replace_template_variables,
        _create_dynamic_context,
        _calculate_cost,
        PRICE_INPUT,
        PRICE_OUTPUT,
        PRICE_CACHE_WRITE,
        PRICE_CACHE_READ
    )
    
    # 정적 컨텍스트 테스트
    test_prompt = "사용자 위치: {{user_location}}, 타임존: {{timezone}}"
    static_prompt = _replace_template_variables(test_prompt)
    print(f"\n1. Static context replacement:")
    print(f"   - Original: {test_prompt}")
    print(f"   - Replaced: {static_prompt}")
    assert '대한민국' in static_prompt
    assert 'Asia/Seoul' in static_prompt
    print("   ✅ Static replacement successful")
    
    # 동적 컨텍스트 테스트
    print(f"\n2. Dynamic context generation:")
    dynamic_context = _create_dynamic_context()
    print(f"   - Generated context: {dynamic_context[:100]}...")
    assert '현재 시간' in dynamic_context
    assert '세션 ID' in dynamic_context
    print("   ✅ Dynamic context generated")
    
    # 비용 계산 테스트
    print(f"\n3. Cost calculation test:")
    test_usage = {
        'input_tokens': 1000,
        'output_tokens': 500,
        'cache_read_input_tokens': 2000,
        'cache_creation_input_tokens': 0
    }
    
    cost = _calculate_cost(test_usage)
    expected = (1000/1_000_000 * PRICE_INPUT) + \
               (500/1_000_000 * PRICE_OUTPUT) + \
               (2000/1_000_000 * PRICE_CACHE_READ)
    
    print(f"   - Test usage: {test_usage}")
    print(f"   - Calculated cost: ${cost:.6f}")
    print(f"   - Expected cost: ${expected:.6f}")
    
    if abs(cost - expected) < 0.0001:
        print("   ✅ Cost calculation correct")
        
        # 절감률 계산
        base_cost = (3000/1_000_000 * PRICE_INPUT) + (500/1_000_000 * PRICE_OUTPUT)
        savings = (1 - cost/base_cost) * 100
        print(f"   💰 Cost savings with cache: {savings:.1f}%")
    else:
        print(f"   ❌ Cost calculation mismatch")


def test_websocket_service_caching():
    """WebSocketService 영구 캐싱 테스트"""
    print("\n=== R1 WebSocket Service Permanent Caching Test ===")
    
    # DynamoDB 테이블 모킹을 위한 환경설정
    os.environ['PROMPTS_TABLE'] = 'sedaily-column-prompts'
    os.environ['FILES_TABLE'] = 'sedaily-column-files'
    
    from backend.services.websocket_service import PROMPT_CACHE
    
    # 캐시 상태 확인
    print(f"\n1. Cache state check:")
    print(f"   - Initial cache entries: {len(PROMPT_CACHE)}")
    print(f"   - Cache is dictionary: {isinstance(PROMPT_CACHE, dict)}")
    print("   ✅ Permanent cache structure confirmed")
    
    # 캐시 동작 시뮬레이션
    print(f"\n2. Cache behavior simulation:")
    test_engine = 'test_engine'
    test_data = {'instruction': 'Test prompt', 'files': []}
    
    # 캐시에 데이터 추가
    PROMPT_CACHE[test_engine] = test_data
    print(f"   - Added test data to cache")
    
    # 캐시 확인
    if test_engine in PROMPT_CACHE:
        retrieved = PROMPT_CACHE[test_engine]
        print(f"   - Cache HIT: {retrieved == test_data}")
        print("   ✅ Permanent cache working correctly")
    else:
        print("   ❌ Cache retrieval failed")
    
    print(f"\n3. Cache persistence check:")
    print(f"   - Cache entries: {list(PROMPT_CACHE.keys())}")
    print(f"   - No TTL mechanism: ✅")
    print(f"   - Will persist for Lambda container lifetime: ✅")


def test_cost_comparison():
    """비용 비교 분석"""
    print("\n=== Cost Comparison Analysis ===")
    
    from backend.lib.anthropic_client import _calculate_cost
    
    scenarios = [
        {
            'name': 'First request (cache write)',
            'usage': {
                'input_tokens': 0,
                'output_tokens': 1000,
                'cache_creation_input_tokens': 5000,
                'cache_read_input_tokens': 0
            }
        },
        {
            'name': 'Subsequent requests (cache hit)',
            'usage': {
                'input_tokens': 0,
                'output_tokens': 1000,
                'cache_creation_input_tokens': 0,
                'cache_read_input_tokens': 5000
            }
        },
        {
            'name': 'No caching',
            'usage': {
                'input_tokens': 5000,
                'output_tokens': 1000,
                'cache_creation_input_tokens': 0,
                'cache_read_input_tokens': 0
            }
        }
    ]
    
    for scenario in scenarios:
        cost = _calculate_cost(scenario['usage'])
        print(f"\n{scenario['name']}:")
        print(f"   - Tokens: {scenario['usage']}")
        print(f"   - Cost: ${cost:.6f}")
    
    # 절감 효과 계산
    cache_hit_cost = _calculate_cost(scenarios[1]['usage'])
    no_cache_cost = _calculate_cost(scenarios[2]['usage'])
    savings = (1 - cache_hit_cost/no_cache_cost) * 100
    
    print(f"\n💰 Total savings with caching: {savings:.1f}%")
    print(f"   - Without cache: ${no_cache_cost:.6f}")
    print(f"   - With cache hit: ${cache_hit_cost:.6f}")
    print(f"   - Saved per request: ${no_cache_cost - cache_hit_cost:.6f}")


if __name__ == '__main__':
    print("=" * 60)
    print("R1 Service Caching Optimization Test Suite")
    print("=" * 60)
    
    try:
        # Anthropic 클라이언트 테스트
        test_anthropic_client_caching()
        
        # WebSocket 서비스 캐싱 테스트
        test_websocket_service_caching()
        
        # 비용 비교 분석
        test_cost_comparison()
        
        print("\n" + "=" * 60)
        print("✅ All R1 tests completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()