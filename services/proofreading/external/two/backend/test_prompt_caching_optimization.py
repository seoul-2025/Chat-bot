#!/usr/bin/env python3
"""
Prompt Caching 최적화 테스트 스크립트
P1 서비스의 캐싱 기능 및 비용 계산 테스트
"""

import os
import sys
import json
import logging
from datetime import datetime

# 경로 설정
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_anthropic_client():
    """Anthropic 클라이언트 캐싱 기능 테스트"""
    try:
        from lib.anthropic_client import AnthropicClient
        
        print("\n" + "="*60)
        print("🧪 Testing AnthropicClient with Prompt Caching")
        print("="*60)
        
        # 테스트용 API 키 설정 (실제 테스트시 환경변수로 설정)
        # os.environ['ANTHROPIC_API_KEY'] = 'your-api-key-here'
        
        client = AnthropicClient()
        
        # 테스트 프롬프트
        system_prompt = """당신은 전문적인 교열 전문가입니다. 
        한국어 문서의 맞춤법, 문법, 문체를 검토하고 개선해주세요.
        
        교열 기준:
        1. 맞춤법 및 문법 오류 수정
        2. 문장의 자연스러운 흐름 개선
        3. 일관된 문체 유지
        4. 명확하고 간결한 표현 사용
        
        이 프롬프트는 캐싱되어 비용을 절감합니다."""
        
        user_message = "다음 문장을 교열해주세요: 오늘은 날씨가 너무 좋아서 공원에서 산책을 했습니다."
        
        print(f"\n📝 System Prompt Length: {len(system_prompt)} chars")
        print(f"💬 User Message: {user_message}")
        
        # 첫 번째 요청 (캐시 생성)
        print("\n🚀 First Request (Cache Creation):")
        response = ""
        for chunk in client.stream_response(
            user_message=user_message,
            system_prompt=system_prompt,
            use_caching=True
        ):
            response += chunk
        
        print(f"Response: {response[:200]}...")
        
        # 사용량 정보 확인
        usage = client.get_last_usage()
        if usage:
            print("\n📊 Usage Information:")
            print(f"  - Input Tokens: {usage.get('input_tokens', 0)}")
            print(f"  - Output Tokens: {usage.get('output_tokens', 0)}")
            print(f"  - Cache Read: {usage.get('cache_read_input_tokens', 0)} tokens")
            print(f"  - Cache Write: {usage.get('cache_creation_input_tokens', 0)} tokens")
            if 'total_cost' in usage:
                print(f"  - Total Cost: ${usage['total_cost']:.6f}")
        
        # 두 번째 요청 (캐시 사용)
        print("\n🚀 Second Request (Cache Hit Expected):")
        user_message_2 = "이 문장도 교열해주세요: 저는 어제 도서관에 가서 책을 많이 읽었어요."
        
        response_2 = ""
        for chunk in client.stream_response(
            user_message=user_message_2,
            system_prompt=system_prompt,
            use_caching=True
        ):
            response_2 += chunk
        
        print(f"Response: {response_2[:200]}...")
        
        # 두 번째 요청의 사용량 정보
        usage_2 = client.get_last_usage()
        if usage_2:
            print("\n📊 Second Request Usage:")
            print(f"  - Input Tokens: {usage_2.get('input_tokens', 0)}")
            print(f"  - Output Tokens: {usage_2.get('output_tokens', 0)}")
            print(f"  - Cache Read: {usage_2.get('cache_read_input_tokens', 0)} tokens (Should be > 0)")
            print(f"  - Cache Write: {usage_2.get('cache_creation_input_tokens', 0)} tokens (Should be 0)")
            if 'total_cost' in usage_2:
                print(f"  - Total Cost: ${usage_2['total_cost']:.6f}")
                
                # 비용 절감 계산
                if 'total_cost' in usage:
                    savings = usage['total_cost'] - usage_2['total_cost']
                    savings_percent = (savings / usage['total_cost']) * 100
                    print(f"\n💰 Cost Savings: ${savings:.6f} ({savings_percent:.1f}%)")
        
        print("\n✅ AnthropicClient test completed!")
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


def test_websocket_service():
    """WebSocket 서비스 영구 캐싱 테스트"""
    try:
        from services.websocket_service import WebSocketService, PROMPT_CACHE
        
        print("\n" + "="*60)
        print("🧪 Testing WebSocketService Permanent Caching")
        print("="*60)
        
        service = WebSocketService()
        
        # 테스트용 엔진 타입
        engine_types = ['proofreading', 'grammar_check', 'style_improvement']
        
        for engine_type in engine_types:
            print(f"\n📝 Testing engine: {engine_type}")
            
            # 첫 번째 로드 (캐시 미스)
            print(f"  First load (cache miss expected):")
            prompt_data_1 = service._load_prompt_from_dynamodb(engine_type)
            print(f"    - Files loaded: {len(prompt_data_1.get('files', []))}")
            print(f"    - Instruction length: {len(prompt_data_1.get('instruction', ''))} chars")
            
            # 두 번째 로드 (캐시 히트)
            print(f"  Second load (cache hit expected):")
            prompt_data_2 = service._load_prompt_from_dynamodb(engine_type)
            print(f"    - Files loaded: {len(prompt_data_2.get('files', []))}")
            print(f"    - Data identical: {prompt_data_1 == prompt_data_2}")
        
        # 캐시 상태 확인
        print(f"\n📦 Global Cache Status:")
        print(f"  - Cached engines: {list(PROMPT_CACHE.keys())}")
        print(f"  - Total cache entries: {len(PROMPT_CACHE)}")
        
        # 메모리 사용량 추정
        total_size = sum(len(str(data)) for data in PROMPT_CACHE.values())
        print(f"  - Estimated cache size: {total_size / 1024:.2f} KB")
        
        print("\n✅ WebSocketService test completed!")
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


def test_cost_calculation():
    """비용 계산 로직 테스트"""
    print("\n" + "="*60)
    print("🧪 Testing Cost Calculation Logic")
    print("="*60)
    
    from lib.anthropic_client import AnthropicClient
    
    client = AnthropicClient()
    
    # 테스트 시나리오
    test_cases = [
        {
            "name": "Small request with cache hit",
            "usage": {
                "input_tokens": 100,
                "output_tokens": 500,
                "cache_read_input_tokens": 2000,
                "cache_creation_input_tokens": 0
            }
        },
        {
            "name": "Large request with cache creation",
            "usage": {
                "input_tokens": 500,
                "output_tokens": 2000,
                "cache_read_input_tokens": 0,
                "cache_creation_input_tokens": 5000
            }
        },
        {
            "name": "Medium request with partial cache",
            "usage": {
                "input_tokens": 300,
                "output_tokens": 1000,
                "cache_read_input_tokens": 1500,
                "cache_creation_input_tokens": 1000
            }
        }
    ]
    
    print("\n💰 Claude Opus 4.5 Pricing (per 1M tokens):")
    print("  - Base Input: $5.00")
    print("  - Output: $25.00")
    print("  - Cache Write (1h): $10.00")
    print("  - Cache Read: $0.50")
    
    total_cost = 0
    for case in test_cases:
        print(f"\n📋 {case['name']}:")
        print(f"  Usage: {case['usage']}")
        cost = client._calculate_cost(case['usage'])
        print(f"  💵 Cost: ${cost:.6f}")
        total_cost += cost
    
    print(f"\n📊 Total cost for all scenarios: ${total_cost:.6f}")
    
    # 캐시 효율성 분석
    print("\n📈 Cache Efficiency Analysis:")
    
    # 캐시 없이 같은 요청을 처리했을 때의 비용
    no_cache_usage = {
        "input_tokens": 7400,  # 모든 input + cache_read + cache_creation
        "output_tokens": 3500,  # 모든 output 합계
        "cache_read_input_tokens": 0,
        "cache_creation_input_tokens": 0
    }
    
    no_cache_cost = client._calculate_cost(no_cache_usage)
    savings = no_cache_cost - total_cost
    efficiency = (savings / no_cache_cost) * 100
    
    print(f"  - Cost without caching: ${no_cache_cost:.6f}")
    print(f"  - Cost with caching: ${total_cost:.6f}")
    print(f"  - Savings: ${savings:.6f}")
    print(f"  - Efficiency: {efficiency:.1f}%")
    
    print("\n✅ Cost calculation test completed!")


if __name__ == "__main__":
    print("\n🚀 Starting Prompt Caching Optimization Tests")
    print("=" * 60)
    
    # 환경변수 설정 (테스트용)
    os.environ['ENABLE_PROMPT_CACHING'] = 'true'
    os.environ['PROMPT_CACHE_TTL'] = '1h'
    os.environ['ENABLE_NATIVE_WEB_SEARCH'] = 'false'  # 테스트시 웹 검색 비활성화
    
    # 각 테스트 실행
    print("\n1️⃣ Testing Cost Calculation...")
    test_cost_calculation()
    
    print("\n2️⃣ Testing WebSocket Service...")
    test_websocket_service()
    
    print("\n3️⃣ Testing Anthropic Client...")
    print("⚠️  Note: This requires a valid API key to actually call the API")
    # test_anthropic_client()  # API 키가 있을 때만 활성화
    
    print("\n" + "="*60)
    print("✅ All tests completed!")
    print("="*60)