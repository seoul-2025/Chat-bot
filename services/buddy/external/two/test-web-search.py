#!/usr/bin/env python3
"""
B1 WebSocket API - Web Search 기능 테스트
2025년 12월 14일 최신 뉴스 테스트
"""

import json
import asyncio
import websockets
import uuid
from datetime import datetime

# WebSocket URL
WS_URL = "wss://dwc2m51as4.execute-api.us-east-1.amazonaws.com/prod"

async def test_web_search():
    """웹 검색 기능 테스트"""
    
    # 고유한 사용자 ID 생성
    user_id = f"test-{uuid.uuid4().hex[:8]}"
    conversation_id = f"conv-{uuid.uuid4().hex[:8]}"
    
    print(f"🚀 B1 Web Search Test")
    print(f"📅 Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🔗 WebSocket: {WS_URL}")
    print("=" * 60)
    
    try:
        async with websockets.connect(WS_URL) as websocket:
            print("✅ Connected to WebSocket")
            
            # 테스트 메시지: 2025년 최신 뉴스 요청
            test_message = {
                "action": "sendMessage",
                "data": {
                    "message": "오늘 2025년 12월 14일 대한민국 최신 주요 뉴스 3가지를 알려주세요. 실시간 정보를 기반으로 답변해주세요.",
                    "userId": user_id,
                    "conversationId": conversation_id,
                    "engineType": "general",
                    "timestamp": datetime.now().isoformat()
                }
            }
            
            print(f"\n📤 Sending message:")
            print(f"   '{test_message['data']['message']}'")
            print("\n⏳ Waiting for response...")
            print("-" * 60)
            
            # 메시지 전송
            await websocket.send(json.dumps(test_message))
            
            # 응답 수신
            full_response = ""
            chunk_count = 0
            has_2025_date = False
            has_web_search_indicator = False
            
            while True:
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=300.0)
                    chunk_count += 1
                    
                    try:
                        data = json.loads(response)
                        
                        if isinstance(data, dict):
                            # 일반 메시지 처리
                            if 'message' in data:
                                text = data['message']
                                print(text, end='', flush=True)
                                full_response += text
                                
                                # 2025년 날짜 확인
                                if '2025' in text:
                                    has_2025_date = True
                                # 웹 검색 지표 확인  
                                if any(word in text.lower() for word in ['오늘', '현재', '최신', '실시간', 'http', 'www']):
                                    has_web_search_indicator = True
                                    
                            elif 'type' in data:
                                if data['type'] == 'complete':
                                    break
                                elif data['type'] == 'error':
                                    print(f"\n❌ Error: {data.get('message', 'Unknown')}")
                                    break
                                elif data['type'] == 'ai_start':
                                    print("\n🤖 AI processing started...")
                                    
                    except json.JSONDecodeError:
                        # 일반 텍스트 응답
                        print(response, end='', flush=True)
                        full_response += response
                        
                except asyncio.TimeoutError:
                    print("\n⏰ Response timeout")
                    break
                except websockets.exceptions.ConnectionClosed:
                    print("\n🔌 Connection closed")
                    break
            
            # 결과 분석
            print("\n" + "=" * 60)
            print("📊 Test Results:")
            print(f"   • Response chunks: {chunk_count}")
            print(f"   • Response length: {len(full_response)} chars")
            print(f"   • Contains 2025 date: {'✅ Yes' if has_2025_date else '❌ No'}")
            print(f"   • Has real-time indicators: {'✅ Yes' if has_web_search_indicator else '❌ No'}")
            
            # 2024년 날짜 체크 (잘못된 날짜)
            if '2024' in full_response:
                print(f"   • ⚠️  WARNING: Contains 2024 date (outdated)")
            
            # 웹 검색 성공 판정
            if has_2025_date and has_web_search_indicator:
                print("\n✅ Web Search: WORKING")
                print("   Claude is providing real-time information from 2025!")
            elif '2024' in full_response:
                print("\n❌ Web Search: NOT WORKING")
                print("   Claude is using outdated training data from 2024")
            else:
                print("\n⚠️  Web Search: UNCERTAIN")
                print("   Unable to determine if web search is active")
                
            print("=" * 60)
            
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("=" * 60)
    print("   B1.SEDAILY.AI - WEB SEARCH TEST")
    print("   Testing Claude Opus 4.5 with Web Search")
    print("=" * 60)
    
    asyncio.run(test_web_search())