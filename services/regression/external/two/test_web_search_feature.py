#!/usr/bin/env python3
"""
웹 검색 기능 종합 테스트
"""
import os
import sys
from datetime import datetime, timezone, timedelta

# 경로 설정
sys.path.append('backend')
sys.path.append('backend/lib')
sys.path.append('backend/services')

def test_web_search_queries():
    """다양한 웹 검색 쿼리 테스트"""
    print("🔍 웹 검색 기능 종합 테스트")
    print("="*60)
    
    try:
        from backend.lib.anthropic_client import AnthropicClient
        from backend.lib.citation_formatter import CitationFormatter
        
        # Anthropic 클라이언트 초기화
        client = AnthropicClient()
        
        # 웹 검색이 필요한 테스트 쿼리들
        test_queries = [
            "오늘 한국 주요 뉴스 3가지만 알려줘",
            "현재 달러 환율은 얼마야?",
            "최신 AI 기술 동향은?",
            "서울 날씨 어때?",
            "삼성전자 주가는?"
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n{'='*60}")
            print(f"📝 테스트 {i}: {query}")
            print("-"*60)
            
            system_prompt = """당신은 최신 정보를 제공하는 AI 어시스턴트입니다.
웹 검색 결과를 활용하여 정확하고 최신의 정보를 제공해주세요.
URL이 있다면 포함해주세요."""
            
            response_text = ""
            chunk_count = 0
            
            print("🤖 응답:")
            print()
            
            # 웹 검색 활성화하여 스트리밍
            for chunk in client.stream_response(
                user_message=query,
                system_prompt=system_prompt,
                conversation_context="",
                enable_web_search=True  # ✅ 웹 검색 활성화
            ):
                print(chunk, end="", flush=True)
                response_text += chunk
                chunk_count += 1
                
                # 너무 길면 중단
                if chunk_count > 200:
                    print("\n[... 응답 생략 ...]")
                    break
            
            print()
            print()
            
            # 응답 분석
            print("📊 분석:")
            
            # 웹 검색 지표 확인
            web_indicators = ['http://', 'https://', 'www.', '.com', '.co.kr', '검색', '최신', '현재', '오늘']
            found_indicators = [ind for ind in web_indicators if ind.lower() in response_text.lower()]
            
            if found_indicators:
                print(f"  ✅ 웹 정보 포함 확인: {found_indicators[:3]}")
            else:
                print("  ⚠️ 웹 정보 미확인")
            
            # URL 검출
            import re
            urls = re.findall(r'https?://[^\s\])]+ ', response_text)
            if urls:
                print(f"  🔗 발견된 URL: {len(urls)}개")
                for url in urls[:3]:  # 최대 3개만 표시
                    print(f"     - {url[:50]}...")
            
            # Citation 테스트
            if urls:
                print("\n  🏷️ Citation 포맷팅 테스트:")
                formatted = CitationFormatter.format_response_with_citations(response_text)
                if "[1]" in formatted or "📚 출처:" in formatted:
                    print("     ✅ Citation 포맷팅 성공!")
                else:
                    print("     ⚠️ Citation 포맷팅 미적용")
            
            print(f"\n  📈 통계: {len(response_text)} 문자, {chunk_count} 청크")
            
            # 잠시 대기
            if i < len(test_queries):
                import time
                print("\n⏳ 다음 테스트까지 2초 대기...")
                time.sleep(2)
    
    except Exception as e:
        print(f"\n❌ 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*60)
    print("✅ 웹 검색 기능 테스트 완료!")

def test_citation_formatting():
    """Citation 포맷팅 단독 테스트"""
    print("\n📚 Citation Formatter 테스트")
    print("="*60)
    
    from backend.lib.citation_formatter import CitationFormatter
    
    test_text = """
    최신 뉴스에 따르면 https://ytn.co.kr/news/20251214 에서 발표한 내용과
    정부 공식 사이트 https://korea.kr/briefing/12345 의 보도자료,
    그리고 일반 사이트 https://example.com/article 를 참고하면...
    """
    
    print("원본 텍스트:")
    print(test_text)
    print("\n포맷팅 결과:")
    formatted = CitationFormatter.format_response_with_citations(test_text)
    print(formatted)

if __name__ == "__main__":
    kst = timezone(timedelta(hours=9))
    current_time = datetime.now(kst)
    print(f"🕐 테스트 시작: {current_time.strftime('%Y-%m-%d %H:%M:%S KST')}\n")
    
    # 웹 검색 테스트
    test_web_search_queries()
    
    # Citation 테스트
    test_citation_formatting()