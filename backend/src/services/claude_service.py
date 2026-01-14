import anthropic
import os

async def generate_claude_response(websocket, message, engine):
    """Claude API를 사용한 AI 응답 생성 및 스트리밍"""
    
    try:
        client = anthropic.Anthropic(
            api_key=os.environ.get('CLAUDE_API_KEY')
        )
        
        # Claude Opus 4.5 사용
        model = "claude-opus-4-5-20251101"
        
        # 스트리밍 응답 생성
        with client.messages.stream(
            model=model,
            max_tokens=4000,
            messages=[{
                "role": "user",
                "content": message
            }]
        ) as stream:
            chunk_index = 0
            
            for event in stream:
                if event.type == "content_block_delta":
                    if hasattr(event.delta, 'text') and event.delta.text:
                        await websocket.send_json({
                            "type": "ai_chunk",
                            "chunk": event.delta.text,
                            "chunk_index": chunk_index
                        })
                        chunk_index += 1
        
        # 스트리밍 완료
        await websocket.send_json({
            "type": "chat_end",
            "total_chunks": chunk_index,
            "engine": engine
        })
        
    except Exception as e:
        print(f"Claude API 오류: {e}")
        await websocket.send_json({
            "type": "error",
            "message": f"AI 응답 생성 중 오류: {str(e)}"
        })