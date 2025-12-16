#!/usr/bin/env python3
"""
날짜 문제 직접 테스트
"""
import os
import sys
from datetime import datetime, timezone, timedelta

# 경로 설정
sys.path.append('backend')
sys.path.append('backend/lib')

def test_date_handling():
    """날짜 처리 직접 테스트"""
    print("🔍 날짜 처리 테스트 시작...")
    print("="*50)
    
    # 현재 시간 확인
    kst = timezone(timedelta(hours=9))
    current_time = datetime.now(kst)
    print(f"✅ 시스템 현재 시간: {current_time}")
    print(f"✅ 포맷된 날짜: {current_time.strftime('%Y년 %m월 %d일')}")
    
    try:
        from backend.lib.anthropic_client import AnthropicClient
        
        # Anthropic 클라이언트 초기화
        client = AnthropicClient()
        
        # 테스트 메시지
        test_messages = [
            "오늘 며칠이야?",
            "어제는 며칠이었어?",
            "내일은 며칠이야?"
        ]
        
        for msg in test_messages:
            print(f"\n📝 질문: {msg}")
            print("-"*30)
            
            # 명시적으로 현재 날짜를 포함한 시스템 프롬프트
            system_prompt = f"""당신은 한국어 AI 어시스턴트입니다.

매우 중요: 현재 날짜는 {current_time.strftime('%Y년 %m월 %d일')}입니다.
절대적으로 이 날짜를 기준으로 답변하세요."""
            
            # 사용자 메시지에도 날짜 정보 포함
            enhanced_message = f"""[시스템 정보: 오늘은 {current_time.strftime('%Y년 %m월 %d일 %H시 %M분')}입니다]

{msg}"""
            
            response_text = ""
            for chunk in client.stream_response(
                user_message=enhanced_message,
                system_prompt=system_prompt,
                conversation_context="",
                enable_web_search=False  # 웹 검색 비활성화로 순수 테스트
            ):
                print(chunk, end="", flush=True)
                response_text += chunk
            
            print()
            
            # 결과 분석
            if "2025" in response_text:
                print("✅ 올바른 연도(2025) 인식!")
            elif "2024" in response_text:
                print("❌ 잘못된 연도(2024) 출력됨")
            
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_date_handling()