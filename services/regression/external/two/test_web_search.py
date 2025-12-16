#!/usr/bin/env python3
"""
웹 검색 기능 테스트 스크립트
"""
import os
import sys
import json
from datetime import datetime

# 경로 설정
sys.path.append('backend')
sys.path.append('backend/lib')
sys.path.append('backend/services')

from backend.lib.anthropic_client import AnthropicClient
from backend.lib.citation_formatter import CitationFormatter

def test_web_search():
    """웹 검색 기능 테스트"""
    print("🔍 웹 검색 기능 테스트 시작...")
    print("="*50)
    
    # 테스트 메시지
    test_message = "오늘의 이유슨?"
    print(f"📝 테스트 메시지: {test_message}")
    print()
    
    try:
        # Anthropic 클라이언트 초기화
        client = AnthropicClient()
        
        # 간단한 시스템 프롬프트
        system_prompt = """당신은 한국어로 답변하는 도움이 되는 AI입니다. 
웹 검색 결과를 활용하여 최신 정보를 제공해주세요."""
        
        print("🤖 AI 응답 생성 중 (웹 검색 활성화)...")
        print("-"*50)
        
        # 웹 검색 활성화하여 스트리밍 응답 생성
        response_text = ""
        for chunk in client.stream_response(
            user_message=test_message,
            system_prompt=system_prompt,
            conversation_context="",
            enable_web_search=True  # 웹 검색 활성화
        ):
            print(chunk, end="", flush=True)
            response_text += chunk
        
        print()
        print("="*50)
        print("✅ 테스트 완료!")
        print(f"📊 응답 길이: {len(response_text)} 문자")
        
        # Citation 테스트
        print()
        print("🏷️ Citation 포맷팅 테스트...")
        
        # 임시 URL이 포함된 텍스트로 Citation 테스트
        test_text_with_url = "관련 정보는 https://ytn.co.kr/example 에서 확인할 수 있습니다."
        formatted = CitationFormatter.format_response_with_citations(test_text_with_url)
        
        if formatted != test_text_with_url:
            print("✅ Citation 포맷팅 작동 확인:")
            print(formatted)
        else:
            print("ℹ️ Citation 포맷팅: URL 없음 또는 변경 없음")
        
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")
        print("💡 가능한 원인:")
        print("   - Anthropic API 키가 설정되지 않음")
        print("   - 네트워크 연결 문제")
        print("   - API 호출 한도 초과")
        
        # 에러 상세 정보
        import traceback
        print("\n🔍 상세 오류 정보:")
        traceback.print_exc()

def test_citation_formatter():
    """Citation Formatter 단독 테스트"""
    print()
    print("🏷️ Citation Formatter 단독 테스트")
    print("="*50)
    
    # 테스트 텍스트 (다양한 도메인)
    test_cases = [
        "YTN 뉴스: https://ytn.co.kr/news/123",
        "정부 발표: https://moef.go.kr/announcement",
        "일반 사이트: https://example.com/article",
        "복합: https://joins.com/news/1 과 https://kbs.co.kr/news/2 참조"
    ]
    
    for i, test_text in enumerate(test_cases, 1):
        print(f"\n📝 테스트 {i}: {test_text}")
        formatted = CitationFormatter.format_response_with_citations(test_text)
        print("➡️ 결과:")
        print(formatted)

if __name__ == "__main__":
    print(f"🕒 테스트 시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Citation Formatter 테스트 (API 호출 없음)
    test_citation_formatter()
    
    print()
    print("🌐 실제 웹 검색 테스트를 진행하시겠습니까?")
    print("⚠️  이 테스트는 실제 Anthropic API를 호출합니다.")
    
    user_input = input("계속하려면 'yes' 입력: ").lower().strip()
    if user_input in ['yes', 'y', '네', 'ㅇ']:
        test_web_search()
    else:
        print("🛑 웹 검색 테스트를 건너뜁니다.")
        print("💡 환경변수 ANTHROPIC_API_KEY 또는 Secrets Manager 설정 후 다시 시도하세요.")