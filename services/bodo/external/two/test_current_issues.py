#!/usr/bin/env python3
"""
오늘의 주요 이슈 확인 테스트
실시간 웹 검색을 통한 최신 이슈 파악
"""
import os
import sys
from datetime import datetime, timezone, timedelta

# 프로젝트 루트 경로 추가
sys.path.append('/Users/yeong-gwang/Documents/work/서울경제신문/DEV/Sedailyio/Prodction/nuexus_temple/b1(bodo)/backend')

from lib.anthropic_client import stream_anthropic_response, get_api_key_from_secrets
from lib.citation_formatter import CitationFormatter

def ask_about_current_issues():
    """오늘의 주요 이슈에 대해 질문"""
    print("🔍 오늘의 주요 이슈 확인 중...")
    
    try:
        # API 키 확인
        api_key = get_api_key_from_secrets()
        if not api_key:
            print("❌ API 키를 찾을 수 없습니다.")
            return False
        
        # 현재 시간 정보
        kst = timezone(timedelta(hours=9))
        current_time = datetime.now(kst)
        
        # 시스템 프롬프트
        system_prompt = f"""당신은 대한민국의 전문 언론인을 위한 AI 어시스턴트입니다.
현재 시간: {current_time.strftime('%Y-%m-%d %H:%M:%S KST')}

실시간 웹 검색을 통해 가장 최신의 정확한 정보를 제공해주세요.
웹 검색 결과를 사용할 때는 반드시 출처를 명시해주세요:

- 인라인 각주: [1], [2] 형식으로 번호 표시  
- 응답 마지막에 출처 섹션 추가:
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  📚 출처:
  [1] 사이트명 - 제목 (URL)
  [2] 사이트명 - 제목 (URL)
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

언론인의 관점에서 중요한 이슈들을 우선적으로 다뤄주세요."""
        
        # 질문
        question = f"오늘 {current_time.strftime('%Y년 %m월 %d일')} 대한민국의 주요 이슈는 무엇인가요? 정치, 경제, 사회, 국제 분야에서 가장 중요한 뉴스들을 알려주세요."
        
        print(f"📝 질문: {question}")
        print("\n🔄 실시간 검색 및 분석 중...\n")
        print("="*60)
        
        # 웹 검색 활성화하여 스트리밍 호출
        response_text = ""
        for chunk in stream_anthropic_response(
            user_message=question,
            system_prompt=system_prompt,
            api_key=api_key,
            enable_web_search=True
        ):
            print(chunk, end='', flush=True)
            response_text += chunk
        
        print("\n" + "="*60)
        print("📊 응답 분석:")
        
        # Citation 포맷팅이 필요한 경우 적용
        formatter = CitationFormatter()
        if "📚 출처:" not in response_text and "http" in response_text:
            print("🔧 출처 포맷팅 적용 중...")
            formatted_response = formatter.format_response_with_citations(response_text)
            print("\n📚 포맷팅된 응답:")
            print("-" * 40)
            print(formatted_response)
        
        # 결과 분석
        has_urls = "http" in response_text or "www." in response_text
        has_citations = "📚 출처:" in response_text or "[1]" in response_text
        has_current_date = current_time.strftime('%Y') in response_text or "오늘" in response_text
        has_multiple_categories = any(category in response_text for category in ["정치", "경제", "사회", "국제"])
        
        print(f"\n✅ 응답 품질 체크:")
        print(f"- 실시간 정보: {'✅' if has_urls else '❌'}")
        print(f"- 출처 표시: {'✅' if has_citations else '❌'}")
        print(f"- 당일 정보: {'✅' if has_current_date else '❌'}")
        print(f"- 다양한 분야: {'✅' if has_multiple_categories else '❌'}")
        
        success = has_urls and (has_citations or "[" in response_text)
        print(f"\n🎯 전체 결과: {'✅ 성공' if success else '❌ 실패'}")
        
        return success
        
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 오늘의 주요 이슈 확인 테스트")
    print("=" * 60)
    
    # 환경 변수 확인
    print("📋 환경 설정:")
    print(f"- 웹 검색: {os.environ.get('ENABLE_NATIVE_WEB_SEARCH', 'false')}")
    print(f"- Anthropic API: {os.environ.get('USE_ANTHROPIC_API', 'false')}")
    
    # 현재 시간
    kst = timezone(timedelta(hours=9))
    now = datetime.now(kst)
    print(f"- 현재 시간: {now.strftime('%Y-%m-%d %H:%M:%S KST')}")
    print()
    
    # 테스트 실행
    result = ask_about_current_issues()
    
    print("\n" + "=" * 60)
    print(f"🏁 최종 결과: {'✅ 성공적으로 최신 이슈 확인' if result else '❌ 테스트 실패'}")