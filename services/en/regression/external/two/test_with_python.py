#!/usr/bin/env python3
"""
다국어 프롬프트 테스트 - Python WebSocket 클라이언트
"""
import asyncio
import websockets
import json
import sys

WEBSOCKET_URL = "wss://yxn6bf9go4.execute-api.us-east-1.amazonaws.com/prod"

# 테스트 케이스
TEST_CASES = [
    {
        "name": "Czech (체코어)",
        "message": "Prezident Trump a jeho ruský protějšek Vladimir Putin se sejdou v Budapešti, aby se pokusili ukončit válku na Ukrajině.",
        "expected_language": "Czech",
        "conversation_id": "test-czech-001"
    },
    {
        "name": "Polish (폴란드어)",
        "message": "Premier Tusk ogłosił dziś nowe reformy edukacyjne, które mają na celu poprawę jakości nauczania.",
        "expected_language": "Polish",
        "conversation_id": "test-polish-001"
    },
    {
        "name": "Russian (러시아어)",
        "message": "Президент Путин заявил сегодня о новых экономических инициативах.",
        "expected_language": "Russian",
        "conversation_id": "test-russian-001"
    },
    {
        "name": "Korean (한국어)",
        "message": "문재인 대통령이 오늘 청와대에서 새로운 경제정책을 발표했다.",
        "expected_language": "Korean",
        "conversation_id": "test-korean-001"
    },
    {
        "name": "English (영어)",
        "message": "President Biden announced today a new infrastructure plan.",
        "expected_language": "English",
        "conversation_id": "test-english-001"
    }
]


async def test_single_case(test_case):
    """단일 테스트 케이스 실행"""
    print(f"\n{'='*60}")
    print(f"테스트: {test_case['name']}")
    print(f"입력: {test_case['message'][:80]}...")
    print(f"{'='*60}")

    try:
        async with websockets.connect(WEBSOCKET_URL) as websocket:
            # 메시지 전송
            request = {
                "action": "sendMessage",
                "message": test_case['message'],
                "engineType": "11",
                "userId": "test@example.com",
                "conversationId": test_case['conversation_id']
            }

            await websocket.send(json.dumps(request))
            print(f"✅ 메시지 전송 완료")

            # 응답 수집
            full_response = ""
            chunk_count = 0

            while True:
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=30.0)
                    data = json.loads(response)

                    if data.get('type') == 'ai_start':
                        print(f"🤖 AI 응답 시작...")

                    elif data.get('type') == 'ai_chunk':
                        chunk = data.get('chunk', '')
                        full_response += chunk
                        chunk_count += 1

                        # 첫 100자만 미리보기
                        if chunk_count == 1:
                            print(f"📝 첫 응답: {chunk[:100]}...")

                    elif data.get('type') == 'chat_end':
                        print(f"✅ 응답 완료: {chunk_count} chunks")
                        break

                    elif data.get('type') == 'error':
                        print(f"❌ 오류: {data.get('message')}")
                        return False

                except asyncio.TimeoutError:
                    print(f"⏱️ 타임아웃")
                    break

            # 결과 분석
            print(f"\n{'─'*60}")
            print(f"전체 응답 ({len(full_response)} chars):")
            print(f"{full_response[:300]}...")
            print(f"{'─'*60}")

            # 언어 검증 (간단한 휴리스틱)
            is_correct = check_language(full_response, test_case['expected_language'])

            if is_correct:
                print(f"✅ 성공: {test_case['expected_language']} 언어로 응답됨")
                return True
            else:
                print(f"❌ 실패: {test_case['expected_language']} 언어 예상했으나 다른 언어로 응답됨")
                return False

    except Exception as e:
        print(f"❌ 연결 오류: {e}")
        return False


def check_language(text, expected_language):
    """간단한 언어 검증"""
    # 한글 체크
    if expected_language == "Korean":
        return any('\uac00' <= char <= '\ud7a3' for char in text[:200])

    # 키릴 문자 체크 (러시아어)
    elif expected_language == "Russian":
        return any('\u0400' <= char <= '\u04ff' for char in text[:200])

    # 라틴 문자 기반 언어 (체코어, 폴란드어 등)
    # 간단히 특수 문자 확인
    elif expected_language == "Czech":
        czech_chars = ['č', 'š', 'ž', 'ř', 'ě', 'ů', 'ú', 'ý', 'á', 'í', 'é']
        return any(char in text[:200].lower() for char in czech_chars)

    elif expected_language == "Polish":
        polish_chars = ['ą', 'ć', 'ę', 'ł', 'ń', 'ó', 'ś', 'ź', 'ż']
        return any(char in text[:200].lower() for char in polish_chars)

    elif expected_language == "English":
        # 영어는 한글/키릴이 없고, 특수 문자도 적음
        return not any('\uac00' <= char <= '\ud7a3' for char in text[:200]) and \
               not any('\u0400' <= char <= '\u04ff' for char in text[:200])

    return True  # 기본값


async def run_all_tests():
    """모든 테스트 실행"""
    print(f"""
{'='*60}
다국어 프롬프트 테스트 시작
{'='*60}
WebSocket URL: {WEBSOCKET_URL}
총 테스트: {len(TEST_CASES)}개
""")

    results = []

    for i, test_case in enumerate(TEST_CASES, 1):
        print(f"\n[{i}/{len(TEST_CASES)}] 테스트 실행 중...")
        result = await test_single_case(test_case)
        results.append({
            'name': test_case['name'],
            'passed': result
        })

        # 다음 테스트 전 대기
        if i < len(TEST_CASES):
            await asyncio.sleep(2)

    # 최종 결과
    print(f"\n\n{'='*60}")
    print(f"테스트 결과 요약")
    print(f"{'='*60}")

    passed = sum(1 for r in results if r['passed'])
    total = len(results)

    for result in results:
        status = "✅ PASS" if result['passed'] else "❌ FAIL"
        print(f"{status} - {result['name']}")

    print(f"\n총 {passed}/{total} 테스트 통과")

    if passed == total:
        print(f"🎉 모든 테스트 성공!")
        return 0
    else:
        print(f"⚠️  {total - passed}개 테스트 실패")
        return 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(run_all_tests())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n테스트 중단됨")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n오류 발생: {e}")
        sys.exit(1)
