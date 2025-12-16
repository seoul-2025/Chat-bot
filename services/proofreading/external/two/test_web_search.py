#!/usr/bin/env python3
"""
웹 검색 기능 테스트 스크립트
Anthropic API의 web_search_20250305 도구 테스트
"""
import os
import sys
import json
import asyncio
import websockets
import logging
from datetime import datetime

# 백엔드 모듈 경로 추가
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# WebSocket 서버 정보 (production 환경에 맞게 수정)
WEBSOCKET_URL = "wss://p062xh167h.execute-api.us-east-1.amazonaws.com/prod"

# 테스트 케이스
TEST_CASES = [
    {
        "name": "현재 뉴스 검색",
        "message": "오늘 2025년 12월 14일 대한민국 최신 뉴스를 알려주세요",
        "expected_web_search": True,
        "expected_citations": True
    },
    {
        "name": "주가 정보 검색", 
        "message": "현재 삼성전자 주가는 어떻게 되나요?",
        "expected_web_search": True,
        "expected_citations": True
    },
    {
        "name": "날씨 정보 검색",
        "message": "서울 오늘 날씨 알려주세요",
        "expected_web_search": True,
        "expected_citations": True
    },
    {
        "name": "일반 질문 (웹 검색 없음)",
        "message": "파이썬에서 리스트와 튜플의 차이점은 무엇인가요?",
        "expected_web_search": False,
        "expected_citations": False
    },
    {
        "name": "웹 검색 키워드 테스트",
        "message": "최신 AI 기술 트렌드를 찾아줘",
        "expected_web_search": True,
        "expected_citations": True
    }
]

async def test_websocket_connection():
    """WebSocket 연결 테스트"""
    try:
        logger.info("WebSocket 연결 테스트 시작...")
        
        uri = WEBSOCKET_URL
        async with websockets.connect(uri) as websocket:
            logger.info(f"✅ WebSocket 연결 성공: {uri}")
            
            # 연결 확인 메시지 전송
            test_message = {
                "action": "sendMessage",
                "message": "연결 테스트",
                "engineType": "Basic",
                "userId": "test@example.com",
                "conversationHistory": []
            }
            
            await websocket.send(json.dumps(test_message))
            logger.info("📤 테스트 메시지 전송 완료")
            
            # 응답 대기
            timeout_count = 0
            while timeout_count < 10:
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                    data = json.loads(response)
                    logger.info(f"📥 응답 수신: {data.get('type', 'unknown')}")
                    
                    if data.get('type') == 'chat_end':
                        logger.info("✅ 연결 테스트 완료")
                        break
                        
                except asyncio.TimeoutError:
                    timeout_count += 1
                    if timeout_count >= 10:
                        logger.warning("⚠️ 응답 대기 시간 초과")
                        break
            
            return True
            
    except Exception as e:
        logger.error(f"❌ WebSocket 연결 실패: {str(e)}")
        logger.info("💡 WebSocket URL을 확인하고 AWS API Gateway가 실행 중인지 확인하세요")
        return False

async def test_web_search_case(test_case):
    """개별 테스트 케이스 실행"""
    logger.info(f"\n{'='*60}")
    logger.info(f"🧪 테스트: {test_case['name']}")
    logger.info(f"💬 메시지: {test_case['message']}")
    logger.info(f"{'='*60}")
    
    try:
        uri = WEBSOCKET_URL
        async with websockets.connect(uri) as websocket:
            message = {
                "action": "sendMessage",
                "message": test_case['message'],
                "engineType": "Basic",
                "userId": "websearch-test@example.com",
                "conversationHistory": [],
                "timestamp": datetime.utcnow().isoformat() + 'Z'
            }
            
            # 메시지 전송
            await websocket.send(json.dumps(message))
            logger.info("📤 메시지 전송 완료")
            
            # 응답 수집
            full_response = ""
            web_search_detected = False
            citations_found = False
            
            timeout_count = 0
            while timeout_count < 30:  # 최대 60초 대기
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                    data = json.loads(response)
                    
                    response_type = data.get('type')
                    
                    if response_type == 'ai_chunk':
                        chunk = data.get('chunk', '')
                        full_response += chunk
                        print(chunk, end='', flush=True)
                        
                        # 웹 검색 도구 사용 감지
                        if 'web_search' in chunk.lower() or 'search' in chunk.lower():
                            web_search_detected = True
                    
                    elif response_type == 'citation_update':
                        formatted_response = data.get('formatted_response', '')
                        if '📚 출처:' in formatted_response:
                            citations_found = True
                            logger.info("\n✅ Citation 포맷팅 감지")
                    
                    elif response_type == 'chat_end':
                        logger.info("\n🏁 응답 생성 완료")
                        break
                        
                    elif response_type == 'error':
                        logger.error(f"❌ 오류 발생: {data.get('message', 'Unknown error')}")
                        return False
                    
                    timeout_count = 0  # 응답 받으면 카운트 리셋
                    
                except asyncio.TimeoutError:
                    timeout_count += 1
                    if timeout_count >= 30:
                        logger.warning("⚠️ 응답 대기 시간 초과")
                        break
            
            # 결과 분석
            logger.info(f"\n📊 테스트 결과 분석:")
            logger.info(f"  • 응답 길이: {len(full_response)} characters")
            logger.info(f"  • 웹 검색 예상: {test_case['expected_web_search']}")
            logger.info(f"  • 웹 검색 감지: {web_search_detected}")
            logger.info(f"  • Citation 예상: {test_case['expected_citations']}")
            logger.info(f"  • Citation 감지: {citations_found}")
            
            # URL 패턴 검사
            import re
            urls_in_response = re.findall(r'https?://[^\s\]]+', full_response)
            logger.info(f"  • 발견된 URL 수: {len(urls_in_response)}")
            
            if urls_in_response:
                logger.info(f"  • URL 예시: {urls_in_response[0] if urls_in_response else 'None'}")
            
            # 테스트 성공 여부 판단
            success = True
            if test_case['expected_web_search'] != web_search_detected:
                logger.warning(f"⚠️ 웹 검색 기대값과 실제값이 다름")
                success = False
            
            if test_case['expected_citations'] and not citations_found and urls_in_response:
                logger.warning(f"⚠️ Citation이 예상되었지만 발견되지 않음")
                success = False
            
            if success:
                logger.info("✅ 테스트 PASS")
            else:
                logger.info("❌ 테스트 FAIL")
            
            return success
            
    except Exception as e:
        logger.error(f"❌ 테스트 실행 오류: {str(e)}")
        return False

def test_citation_formatter():
    """Citation Formatter 단위 테스트"""
    logger.info(f"\n{'='*60}")
    logger.info("🧪 Citation Formatter 단위 테스트")
    logger.info(f"{'='*60}")
    
    try:
        from lib.citation_formatter import CitationFormatter
        
        # 테스트 케이스
        test_text = """
        삼성전자의 주가는 현재 75,000원으로 보고되고 있습니다. 
        자세한 정보는 https://finance.naver.com에서 확인할 수 있습니다.
        또한 https://ytn.co.kr의 최신 뉴스도 참고하시기 바랍니다.
        """
        
        logger.info("📝 원본 텍스트:")
        logger.info(test_text.strip())
        
        # Citation 포맷팅 적용
        formatted = CitationFormatter.format_response_with_citations(test_text)
        
        logger.info("\n📝 포맷팅된 텍스트:")
        logger.info(formatted)
        
        # 결과 검증
        if "📚 출처:" in formatted and "[1]" in formatted:
            logger.info("✅ Citation Formatter 테스트 PASS")
            return True
        else:
            logger.error("❌ Citation Formatter 테스트 FAIL")
            return False
            
    except Exception as e:
        logger.error(f"❌ Citation Formatter 테스트 오류: {str(e)}")
        return False

async def main():
    """메인 테스트 함수"""
    logger.info("🚀 웹 검색 기능 통합 테스트 시작")
    logger.info(f"⏰ 테스트 시작 시간: {datetime.now()}")
    
    # 1. Citation Formatter 단위 테스트
    citation_test_passed = test_citation_formatter()
    
    # 2. WebSocket 연결 테스트
    if WEBSOCKET_URL == "wss://your-api-gateway-url/production":
        logger.warning("⚠️ WebSocket URL이 설정되지 않았습니다.")
        logger.info("💡 실제 API Gateway WebSocket URL로 WEBSOCKET_URL을 변경하세요.")
        logger.info("💡 Citation Formatter 테스트만 실행됩니다.")
        return
    
    connection_test_passed = await test_websocket_connection()
    
    if not connection_test_passed:
        logger.error("❌ WebSocket 연결 실패로 인해 테스트 중단")
        return
    
    # 3. 웹 검색 기능 테스트
    test_results = []
    for test_case in TEST_CASES:
        result = await test_web_search_case(test_case)
        test_results.append({
            'name': test_case['name'],
            'passed': result
        })
        
        # 테스트 간 대기 시간
        await asyncio.sleep(2)
    
    # 4. 결과 요약
    logger.info(f"\n{'='*60}")
    logger.info("📊 테스트 결과 요약")
    logger.info(f"{'='*60}")
    
    total_tests = len(test_results) + (1 if citation_test_passed else 0)
    passed_tests = sum(1 for result in test_results if result['passed']) + (1 if citation_test_passed else 0)
    
    logger.info(f"📋 Citation Formatter: {'✅ PASS' if citation_test_passed else '❌ FAIL'}")
    
    for result in test_results:
        status = "✅ PASS" if result['passed'] else "❌ FAIL"
        logger.info(f"📋 {result['name']}: {status}")
    
    logger.info(f"\n🎯 전체 결과: {passed_tests}/{total_tests} 테스트 통과")
    
    if passed_tests == total_tests:
        logger.info("🎉 모든 테스트가 성공적으로 완료되었습니다!")
    else:
        logger.warning("⚠️ 일부 테스트가 실패했습니다. 로그를 확인하세요.")

if __name__ == "__main__":
    print("🧪 웹 검색 기능 테스트 도구")
    print("=" * 60)
    print("이 스크립트는 다음을 테스트합니다:")
    print("1. Citation Formatter 단위 테스트")
    print("2. WebSocket 연결 테스트") 
    print("3. 웹 검색 기능 통합 테스트")
    print("4. Citation 자동 포맷팅 테스트")
    print("")
    print("⚠️ 주의: WEBSOCKET_URL을 실제 API Gateway URL로 변경해야 합니다.")
    print("=" * 60)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️ 사용자에 의해 테스트가 중단되었습니다.")
    except Exception as e:
        print(f"\n\n❌ 테스트 실행 중 오류 발생: {str(e)}")