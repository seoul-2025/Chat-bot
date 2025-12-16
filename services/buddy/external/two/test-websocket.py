#!/usr/bin/env python3
"""
B1 WebSocket API 테스트 스크립트
웹 검색 기능 테스트
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
    user_id = f"test-user-{uuid.uuid4().hex[:8]}"
    conversation_id = f"test-conv-{uuid.uuid4().hex[:8]}"
    
    print(f"🚀 Connecting to: {WS_URL}")
    print(f"👤 User ID: {user_id}")
    print(f"💬 Conversation ID: {conversation_id}")
    print("-" * 50)
    
    try:
        async with websockets.connect(WS_URL) as websocket:
            print("✅ WebSocket 연결 성공!")
            
            # 테스트 메시지 1: 웹 검색이 필요한 질문
            test_message = {
                "action": "sendMessage",
                "data": {
                    "message": "오늘 대한민국 주요 뉴스 3가지만 알려줘",
                    "userId": user_id,
                    "conversationId": conversation_id,
                    "engineType": "general",
                    "timestamp": datetime.now().isoformat()
                }
            }
            
            print(f"\n📤 Sending test message:")
            print(f"   '{test_message['data']['message']}'")
            
            # 메시지 전송
            await websocket.send(json.dumps(test_message))
            print("✅ Message sent successfully")
            
            # 응답 수신
            print("\n📥 Receiving response:")
            print("-" * 50)
            
            full_response = ""
            message_count = 0
            
            while True:
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=30.0)
                    message_count += 1
                    
                    # JSON 파싱 시도
                    try:
                        data = json.loads(response)
                        
                        # 메시지 타입 확인
                        if isinstance(data, dict):
                            if 'message' in data:
                                # 일반 메시지
                                print(data.get('message', ''), end='', flush=True)
                                full_response += data.get('message', '')
                            elif 'type' in data:
                                # 시스템 메시지
                                if data['type'] == 'complete':
                                    print("\n✅ Response complete")
                                    break
                                elif data['type'] == 'error':
                                    print(f"\n❌ Error: {data.get('message', 'Unknown error')}")
                                    break
                                else:
                                    print(f"\nℹ️  System: {data}")
                        else:
                            # 텍스트 응답
                            print(response, end='', flush=True)
                            full_response += response
                            
                    except json.JSONDecodeError:
                        # JSON이 아닌 일반 텍스트
                        print(response, end='', flush=True)
                        full_response += response
                        
                except asyncio.TimeoutError:
                    print("\n⏰ Timeout - No more data")
                    break
                except websockets.exceptions.ConnectionClosed:
                    print("\n🔌 Connection closed")
                    break
            
            print("\n" + "-" * 50)
            print(f"📊 Statistics:")
            print(f"   • Messages received: {message_count}")
            print(f"   • Total response length: {len(full_response)} chars")
            
            # 웹 검색 관련 키워드 체크
            web_search_indicators = ['오늘', '2024', '2025', '뉴스', '최신', '현재']
            found_indicators = [word for word in web_search_indicators if word in full_response]
            
            if found_indicators:
                print(f"   • 🔍 Web search indicators found: {', '.join(found_indicators)}")
                print(f"   • ✅ Web search likely activated!")
            else:
                print(f"   • ⚠️  No clear web search indicators found")
                
            # 두 번째 테스트: 일반 질문 (웹 검색 불필요)
            print("\n" + "=" * 50)
            print("🧪 Test 2: General question (no web search needed)")
            print("=" * 50)
            
            test_message2 = {
                "action": "sendMessage",
                "data": {
                    "message": "파이썬에서 리스트와 튜플의 차이점은 뭐야?",
                    "userId": user_id,
                    "conversationId": conversation_id,
                    "engineType": "general",
                    "timestamp": datetime.now().isoformat()
                }
            }
            
            print(f"\n📤 Sending test message 2:")
            print(f"   '{test_message2['data']['message']}'")
            
            await websocket.send(json.dumps(test_message2))
            print("✅ Message sent")
            
            print("\n📥 Response preview (first 500 chars):")
            print("-" * 50)
            
            response_preview = ""
            while len(response_preview) < 500:
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    
                    try:
                        data = json.loads(response)
                        if isinstance(data, dict) and 'message' in data:
                            response_preview += data['message']
                            print(data['message'], end='', flush=True)
                    except json.JSONDecodeError:
                        response_preview += response
                        print(response, end='', flush=True)
                        
                except asyncio.TimeoutError:
                    break
                except websockets.exceptions.ConnectionClosed:
                    break
            
            print("\n" + "-" * 50)
            print("✅ Test completed!")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("=" * 50)
    print("   B1 WebSocket API - Web Search Test")
    print("=" * 50)
    
    # 이벤트 루프 실행
    asyncio.run(test_web_search())