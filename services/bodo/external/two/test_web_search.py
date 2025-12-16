#!/usr/bin/env python3
"""
웹 검색 기능 테스트 스크립트
Anthropic API의 web_search_20250305 도구 테스트
"""
import os
import sys
import json
import requests
from datetime import datetime, timezone, timedelta

# 프로젝트 루트 경로 추가
sys.path.append('/Users/yeong-gwang/Documents/work/서울경제신문/DEV/Sedailyio/Prodction/nuexus_temple/b1(bodo)/backend')

from lib.anthropic_client import stream_anthropic_response, get_api_key_from_secrets
from lib.citation_formatter import CitationFormatter

def test_web_search_direct():
    """직접 Anthropic API 호출로 웹 검색 테스트"""
    print("🔍 웹 검색 기능 테스트 시작...")
    
    try:
        # API 키 확인
        api_key = get_api_key_from_secrets()
        if not api_key:
            print("❌ API 키를 찾을 수 없습니다.")
            return False
        
        print("✅ API 키 확인됨")
        
        # 현재 시간 정보
        kst = timezone(timedelta(hours=9))
        current_time = datetime.now(kst)
        
        # 시스템 프롬프트
        system_prompt = f"""당신은 한국의 전문 언론인을 위한 AI 어시스턴트입니다.
현재 시간: {current_time.strftime('%Y-%m-%d %H:%M:%S KST')}

웹 검색 결과를 사용할 때는 반드시 출처를 명시해주세요.
- 인라인 각주: [1], [2] 형식으로 번호 표시
- 응답 마지막에 출처 섹션 추가:
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  📚 출처:
  [1] 사이트명 - 제목 (URL)
  [2] 사이트명 - 제목 (URL)
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        
        # 테스트 질문 (실시간 정보가 필요한 질문)
        test_message = f"오늘 {current_time.strftime('%Y년 %m월 %d일')} 대한민국 최신 뉴스를 3개 알려주세요."
        
        print(f"📝 테스트 질문: {test_message}")
        print("\n🔄 응답 생성 중...\n")
        
        # 웹 검색 활성화하여 스트리밍 호출
        response_text = ""
        for chunk in stream_anthropic_response(
            user_message=test_message,
            system_prompt=system_prompt,
            api_key=api_key,
            enable_web_search=True  # 웹 검색 활성화
        ):
            print(chunk, end='', flush=True)
            response_text += chunk
        
        print("\n\n" + "="*50)
        print("📊 테스트 결과 분석:")
        
        # Citation 포맷팅 테스트
        formatter = CitationFormatter()
        if "📚 출처:" not in response_text and "http" in response_text:
            print("🔧 Citation 포맷팅 적용 중...")
            formatted_response = formatter.format_response_with_citations(response_text)
            print("\n📚 포맷팅된 응답:")
            print(formatted_response)
        
        # 결과 분석
        has_urls = "http" in response_text
        has_citations = "📚 출처:" in response_text or "[1]" in response_text
        has_current_info = any(keyword in response_text.lower() for keyword in ["2025", "오늘", "최신", "현재"])
        
        print(f"\n✅ 테스트 결과:")
        print(f"- URL 포함: {'✅' if has_urls else '❌'}")
        print(f"- 출처 표시: {'✅' if has_citations else '❌'}")
        print(f"- 최신 정보: {'✅' if has_current_info else '❌'}")
        
        success = has_urls and has_current_info
        print(f"\n🎯 전체 결과: {'✅ 성공' if success else '❌ 실패'}")
        
        return success
        
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")
        return False

def test_citation_formatter():
    """Citation Formatter 단독 테스트"""
    print("\n🧪 Citation Formatter 테스트...")
    
    # 테스트 텍스트 (URL 포함)
    test_text = """최근 경제 동향에 따르면 한국은행이 기준금리를 조정했습니다 https://yna.co.kr/view/AKR20251214001 
또한 정부에서 새로운 정책을 발표했습니다 https://korea.kr/newsWeb/pages/brief/partNews/view.do?newsId=123"""
    
    formatter = CitationFormatter()
    formatted_text = formatter.format_response_with_citations(test_text)
    
    print("원본 텍스트:")
    print(test_text)
    print("\n포맷팅된 텍스트:")
    print(formatted_text)
    
    # 결과 확인
    has_footnotes = "[1]" in formatted_text and "[2]" in formatted_text
    has_source_section = "📚 출처:" in formatted_text
    
    print(f"\n결과: {'✅ 성공' if has_footnotes and has_source_section else '❌ 실패'}")
    return has_footnotes and has_source_section

if __name__ == "__main__":
    print("🚀 웹 검색 기능 종합 테스트")
    print("=" * 50)
    
    # 환경 변수 확인
    print("📋 환경 설정 확인:")
    print(f"- ENABLE_NATIVE_WEB_SEARCH: {os.environ.get('ENABLE_NATIVE_WEB_SEARCH', 'false')}")
    print(f"- USE_ANTHROPIC_API: {os.environ.get('USE_ANTHROPIC_API', 'false')}")
    print(f"- ANTHROPIC_SECRET_NAME: {os.environ.get('ANTHROPIC_SECRET_NAME', 'Not Set')}")
    
    print("\n1️⃣ Citation Formatter 테스트")
    citation_success = test_citation_formatter()
    
    print("\n2️⃣ 웹 검색 기능 테스트")
    web_search_success = test_web_search_direct()
    
    print("\n" + "=" * 50)
    print("🏁 최종 결과")
    print(f"- Citation Formatter: {'✅' if citation_success else '❌'}")
    print(f"- 웹 검색 기능: {'✅' if web_search_success else '❌'}")
    
    overall_success = citation_success and web_search_success
    print(f"\n🎯 전체: {'✅ 모든 테스트 통과' if overall_success else '❌ 일부 실패'}")