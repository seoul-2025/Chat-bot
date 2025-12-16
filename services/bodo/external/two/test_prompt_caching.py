#!/usr/bin/env python3
"""
Prompt Caching 기능 테스트 스크립트
영구 캐싱 및 비용 최적화 검증
"""

import os
import sys
import json
import time
from datetime import datetime

# 경로 설정
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend'))

# 환경변수 설정
os.environ['USE_ANTHROPIC_API'] = 'true'
os.environ['ENABLE_PROMPT_CACHING'] = 'true'
os.environ['CACHE_TTL'] = '1h'
os.environ['ENABLE_NATIVE_WEB_SEARCH'] = 'false'  # 테스트에서는 웹 검색 비활성화

from backend.lib.anthropic_client import AnthropicClient, _calculate_cost
from backend.services.websocket_service import WebSocketService


def test_prompt_caching():
    """Prompt Caching 기능 테스트"""
    print("\n" + "="*60)
    print("🧪 Prompt Caching 테스트 시작")
    print("="*60)
    
    # Anthropic 클라이언트 초기화
    client = AnthropicClient()
    
    # 테스트 프롬프트
    system_prompt = """당신은 친절한 AI 어시스턴트입니다.
사용자의 질문에 정확하고 도움이 되는 답변을 제공하세요.
{{user_location}}에서 {{timezone}} 시간대를 사용하는 사용자를 위해 최적화되었습니다."""
    
    print("\n📝 테스트 1: 첫 번째 요청 (캐시 생성)")
    print("-" * 40)
    
    response1 = ""
    start_time = time.time()
    
    for chunk in client.stream_response(
        user_message="안녕하세요! 프롬프트 캐싱이 작동하는지 테스트 중입니다.",
        system_prompt=system_prompt
    ):
        response1 += chunk
        print(chunk, end="", flush=True)
    
    elapsed1 = time.time() - start_time
    print(f"\n\n⏱️ 응답 시간: {elapsed1:.2f}초")
    
    # Usage 정보 확인
    usage1 = client.get_last_usage()
    if usage1:
        cost1 = _calculate_cost(usage1)
        print(f"💰 비용: ${cost1:.6f}")
        print(f"📊 토큰 사용:")
        print(f"   - Input: {usage1.get('input_tokens', 0)}")
        print(f"   - Output: {usage1.get('output_tokens', 0)}")
        print(f"   - Cache Write: {usage1.get('cache_creation_input_tokens', 0)}")
        print(f"   - Cache Read: {usage1.get('cache_read_input_tokens', 0)}")
    
    print("\n\n📝 테스트 2: 두 번째 요청 (캐시 활용)")
    print("-" * 40)
    
    response2 = ""
    start_time = time.time()
    
    for chunk in client.stream_response(
        user_message="프롬프트 캐싱이 두 번째 요청에서도 잘 작동하나요?",
        system_prompt=system_prompt
    ):
        response2 += chunk
        print(chunk, end="", flush=True)
    
    elapsed2 = time.time() - start_time
    print(f"\n\n⏱️ 응답 시간: {elapsed2:.2f}초")
    
    # Usage 정보 확인
    usage2 = client.get_last_usage()
    if usage2:
        cost2 = _calculate_cost(usage2)
        print(f"💰 비용: ${cost2:.6f}")
        print(f"📊 토큰 사용:")
        print(f"   - Input: {usage2.get('input_tokens', 0)}")
        print(f"   - Output: {usage2.get('output_tokens', 0)}")
        print(f"   - Cache Write: {usage2.get('cache_creation_input_tokens', 0)}")
        print(f"   - Cache Read: {usage2.get('cache_read_input_tokens', 0)}")
    
    # 결과 비교
    print("\n\n" + "="*60)
    print("📈 캐싱 효과 분석")
    print("="*60)
    
    if usage1 and usage2:
        cache_write = usage1.get('cache_creation_input_tokens', 0)
        cache_read = usage2.get('cache_read_input_tokens', 0)
        
        if cache_write > 0:
            print(f"✅ 첫 번째 요청에서 {cache_write} 토큰이 캐시에 저장되었습니다.")
        
        if cache_read > 0:
            print(f"✅ 두 번째 요청에서 {cache_read} 토큰이 캐시에서 읽혔습니다.")
            
            # 비용 절감 계산
            cost_saved = (cost1 - cost2) if cost1 > cost2 else 0
            if cost_saved > 0:
                percent_saved = (cost_saved / cost1) * 100
                print(f"💰 비용 절감: ${cost_saved:.6f} ({percent_saved:.1f}%)")
        
        # 속도 개선
        if elapsed2 < elapsed1:
            speed_improvement = ((elapsed1 - elapsed2) / elapsed1) * 100
            print(f"⚡ 속도 개선: {speed_improvement:.1f}% 더 빠름")


def test_websocket_cache():
    """WebSocket 서비스의 영구 캐싱 테스트"""
    print("\n\n" + "="*60)
    print("🧪 WebSocket 영구 캐싱 테스트")
    print("="*60)
    
    # WebSocketService 초기화
    ws_service = WebSocketService()
    
    # 캐시 상태 확인
    stats = ws_service.get_cache_stats()
    print(f"\n📊 초기 캐시 상태:")
    print(f"   - 캐시 엔트리: {stats['total_entries']}")
    print(f"   - 영구 캐시: {stats['permanent_cache']}")
    
    # 첫 번째 프롬프트 로드 (캐시 미스)
    print("\n📝 첫 번째 프롬프트 로드 (engine: test-engine)")
    start_time = time.time()
    prompt1 = ws_service._load_prompt_from_dynamodb('test-engine')
    elapsed1 = (time.time() - start_time) * 1000
    print(f"   ⏱️ 로드 시간: {elapsed1:.0f}ms")
    
    # 두 번째 프롬프트 로드 (캐시 히트)
    print("\n📝 두 번째 프롬프트 로드 (engine: test-engine)")
    start_time = time.time()
    prompt2 = ws_service._load_prompt_from_dynamodb('test-engine')
    elapsed2 = (time.time() - start_time) * 1000
    print(f"   ⏱️ 로드 시간: {elapsed2:.0f}ms")
    
    # 캐시 상태 재확인
    stats = ws_service.get_cache_stats()
    print(f"\n📊 최종 캐시 상태:")
    print(f"   - 캐시 엔트리: {stats['total_entries']}")
    print(f"   - 캐시된 엔진: {stats['engines']}")
    print(f"   - 캐시 크기: {stats['cache_size_bytes']} bytes")
    
    # 성능 개선 확인
    if elapsed2 < elapsed1:
        improvement = ((elapsed1 - elapsed2) / elapsed1) * 100
        print(f"\n✅ 캐시 히트로 {improvement:.1f}% 속도 향상!")
        print(f"   (DB 조회 {elapsed1:.0f}ms → 캐시 {elapsed2:.0f}ms)")
    
    # 캐시 클리어 테스트
    print("\n🗑️ 캐시 클리어 테스트")
    ws_service.clear_prompt_cache('test-engine')
    stats = ws_service.get_cache_stats()
    print(f"   - 남은 엔트리: {stats['total_entries']}")


def main():
    """메인 테스트 함수"""
    print("\n" + "🚀"*30)
    print("W1 서비스 Prompt Caching 최적화 테스트")
    print("🚀"*30)
    
    try:
        # Prompt Caching 테스트
        test_prompt_caching()
        
        # WebSocket 영구 캐싱 테스트
        test_websocket_cache()
        
        print("\n\n" + "="*60)
        print("✅ 모든 테스트 완료!")
        print("="*60)
        
    except Exception as e:
        print(f"\n\n❌ 테스트 실패: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())