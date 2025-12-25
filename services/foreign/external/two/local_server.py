#!/usr/bin/env python3
"""
f1 서비스 로컬 테스트 서버
Flask를 사용한 WebSocket 및 API 엔드포인트 제공
"""
import os
import sys
import json
from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
from datetime import datetime
import uuid

# 백엔드 모듈 경로 추가
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

try:
    from services.websocket_service import WebSocketService
    from utils.logger import setup_logger
except ImportError as e:
    print(f"Import error: {e}")
    print("백엔드 모듈을 찾을 수 없습니다. 경로를 확인해주세요.")
    sys.exit(1)

# Flask 앱 초기화
app = Flask(__name__)
app.config['SECRET_KEY'] = 'f1-local-test-key'
socketio = SocketIO(app, cors_allowed_origins="*")

# 로거 설정
logger = setup_logger(__name__)

# WebSocket 서비스 초기화
websocket_service = WebSocketService()

@app.route('/')
def index():
    return """
    <h1>f1.sedaily.ai 로컬 테스트 서버</h1>
    <p>WebSocket 연결: ws://localhost:5000</p>
    <p>API 엔드포인트:</p>
    <ul>
        <li>GET /api/health - 헬스체크</li>
        <li>POST /api/test-message - 메시지 테스트</li>
    </ul>
    """

@app.route('/api/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'service': 'f1.sedaily.ai',
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    })

@app.route('/api/test-message', methods=['POST'])
def test_message():
    """메시지 처리 테스트 API"""
    try:
        data = request.get_json()
        user_message = data.get('message', 'Hello')
        engine_type = data.get('engineType', 'F1')
        
        # 테스트용 파라미터
        conversation_id = str(uuid.uuid4())
        user_id = 'test-user'
        conversation_history = []
        
        # 메시지 처리
        process_result = websocket_service.process_message(
            user_message=user_message,
            engine_type=engine_type,
            conversation_id=conversation_id,
            user_id=user_id,
            conversation_history=conversation_history,
            user_role='user'
        )
        
        # 응답 수집
        response_chunks = []
        for chunk in websocket_service.stream_response(
            user_message=user_message,
            engine_type=engine_type,
            conversation_id=process_result['conversation_id'],
            user_id=user_id,
            conversation_history=process_result['merged_history'],
            user_role='user'
        ):
            response_chunks.append(chunk)
        
        full_response = ''.join(response_chunks)
        
        return jsonify({
            'success': True,
            'conversation_id': process_result['conversation_id'],
            'response': full_response,
            'chunks_count': len(response_chunks)
        })
        
    except Exception as e:
        logger.error(f"Test message error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@socketio.on('connect')
def handle_connect():
    logger.info(f"Client connected: {request.sid}")
    emit('connected', {'message': 'f1 서비스에 연결되었습니다.'})

@socketio.on('disconnect')
def handle_disconnect():
    logger.info(f"Client disconnected: {request.sid}")

@socketio.on('message')
def handle_message(data):
    """WebSocket 메시지 처리"""
    try:
        logger.info(f"Received message: {data}")
        
        # 메시지 파라미터 추출
        user_message = data.get('message', '')
        engine_type = data.get('engineType', 'F1')
        conversation_id = data.get('conversationId') or str(uuid.uuid4())
        user_id = data.get('userId', request.sid)
        conversation_history = data.get('conversationHistory', [])
        
        # 처리 시작 알림
        emit('ai_start', {
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        })
        
        # 메시지 처리
        process_result = websocket_service.process_message(
            user_message=user_message,
            engine_type=engine_type,
            conversation_id=conversation_id,
            user_id=user_id,
            conversation_history=conversation_history,
            user_role='user'
        )
        
        # 스트리밍 응답
        chunk_index = 0
        total_response = ""
        
        for chunk in websocket_service.stream_response(
            user_message=user_message,
            engine_type=engine_type,
            conversation_id=process_result['conversation_id'],
            user_id=user_id,
            conversation_history=process_result['merged_history'],
            user_role='user'
        ):
            total_response += chunk
            
            # 청크 전송
            emit('ai_chunk', {
                'chunk': chunk,
                'chunk_index': chunk_index,
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            })
            
            chunk_index += 1
        
        # 완료 알림
        emit('chat_end', {
            'engine': engine_type,
            'conversationId': process_result['conversation_id'],
            'total_chunks': chunk_index,
            'response_length': len(total_response),
            'message': '응답 생성이 완료되었습니다.',
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        })
        
        # 사용량 추적
        websocket_service.track_usage(
            user_id=user_id,
            engine_type=engine_type,
            input_text=user_message,
            output_text=total_response
        )
        
        logger.info(f"Message processed: {chunk_index} chunks, {len(total_response)} chars")
        
    except Exception as e:
        logger.error(f"WebSocket message error: {str(e)}")
        emit('error', {
            'message': f'처리 중 오류가 발생했습니다: {str(e)}'
        })

if __name__ == '__main__':
    print("🚀 f1.sedaily.ai 로컬 테스트 서버 시작")
    print("📍 URL: http://localhost:5000")
    print("🔌 WebSocket: ws://localhost:5000")
    print("💡 Ctrl+C로 종료")
    
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)