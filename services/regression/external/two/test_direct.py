#!/usr/bin/env python3
"""
직접 웹 검색 테스트 (입력 없이)
"""
import os
import sys
import json
from datetime import datetime

# 경로 설정
sys.path.append('backend')
sys.path.append('backend/lib')
sys.path.append('backend/services')

def test_web_search_direct():
    """웹 검색 기능 직접 테스트"""
    print("🔍 웹 검색 기능 테스트 시작...")
    print("="*50)
    
    # 테스트 메시지
    test_message = "오늘의 이유슨?"
    print(f"📝 테스트 메시지: {test_message}")
    print()
    
    try:
        from backend.lib.anthropic_client import AnthropicClient
        
        # Anthropic 클라이언트 초기화
        client = AnthropicClient()
        
        # 간단한 시스템 프롬프트
        system_prompt = """당신은 한국어로 답변하는 도움이 되는 AI입니다. 
웹 검색 결과를 활용하여 최신 정보를 제공해주세요."""
        
        print("🤖 AI 응답 생성 중 (웹 검색 활성화)...")
        print("-"*50)
        
        # 웹 검색 활성화하여 스트리밍 응답 생성
        response_text = ""
        chunk_count = 0
        
        for chunk in client.stream_response(
            user_message=test_message,
            system_prompt=system_prompt,
            conversation_context="",
            enable_web_search=True  # 웹 검색 활성화
        ):
            print(chunk, end="", flush=True)
            response_text += chunk
            chunk_count += 1
            
            # 너무 길면 중단
            if chunk_count > 100:
                print("\n[응답이 길어서 일부만 표시]")
                break
        
        print()
        print("="*50)
        print("✅ 테스트 완료!")
        print(f"📊 응답 길이: {len(response_text)} 문자")
        print(f"📦 청크 수: {chunk_count}")
        
        # 웹 검색 결과가 포함되었는지 확인
        web_indicators = ['http', '출처', 'source', '검색', '웹']
        found_indicators = [ind for ind in web_indicators if ind in response_text.lower()]
        
        if found_indicators:
            print(f"🌐 웹 검색 결과 포함 확인: {found_indicators}")
        else:
            print("ℹ️ 웹 검색 결과 미확인 (일반 응답일 수 있음)")
        
    except ImportError as e:
        print(f"❌ 모듈 Import 오류: {str(e)}")
        print("💡 경로 문제일 수 있습니다.")
        
        # 파일 존재 확인
        files_to_check = [
            'backend/lib/anthropic_client.py',
            'backend/lib/citation_formatter.py'
        ]
        
        for file_path in files_to_check:
            if os.path.exists(file_path):
                print(f"✅ 파일 존재: {file_path}")
            else:
                print(f"❌ 파일 없음: {file_path}")
        
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

if __name__ == "__main__":
    print(f"🕒 테스트 시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 웹 검색 테스트 바로 실행
    test_web_search_direct()