#!/usr/bin/env python3
"""
구체적 키워드 웹 검색 테스트
"""
import os
import sys
from datetime import datetime

# 경로 설정
sys.path.append('backend')
sys.path.append('backend/lib')

def test_specific_search(query):
    """구체적 검색어 테스트"""
    print(f"🔍 검색어: {query}")
    print("="*50)
    
    try:
        from backend.lib.anthropic_client import AnthropicClient
        
        client = AnthropicClient()
        system_prompt = """당신은 최신 정보를 제공하는 뉴스 AI입니다. 
웹 검색 결과를 바탕으로 정확하고 최신의 정보를 제공해주세요."""
        
        print("🤖 AI 응답:")
        print("-"*30)
        
        response_text = ""
        for chunk in client.stream_response(
            user_message=query,
            system_prompt=system_prompt,
            enable_web_search=True
        ):
            print(chunk, end="", flush=True)
            response_text += chunk
        
        print()
        print("-"*30)
        print(f"📊 {len(response_text)} 문자")
        
        return response_text
        
    except Exception as e:
        print(f"❌ 오류: {str(e)}")
        return None

if __name__ == "__main__":
    # 다양한 검색어 테스트
    test_queries = [
        "오늘 한국 증시 상황은?",
        "현재 달러 환율은?", 
        "최근 정부 발표 소식"
    ]
    
    print(f"🕒 {datetime.now().strftime('%H:%M:%S')}")
    print()
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n📋 테스트 {i}/3")
        result = test_specific_search(query)
        
        if result and any(indicator in result.lower() for indicator in ['http', 'url', '출처', '기준']):
            print("✅ 웹 검색 결과 포함됨")
        
        if i < len(test_queries):
            print("\n" + "="*60)
    
    print("\n🎉 모든 테스트 완료!")