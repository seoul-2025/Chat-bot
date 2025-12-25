#!/usr/bin/env python3
"""
f1 서비스 간단한 테스트 서버
"""
from flask import Flask, jsonify, request
from flask_cors import CORS
import json
from datetime import datetime

app = Flask(__name__)
CORS(app)  # CORS 허용

@app.route('/')
def index():
    return jsonify({
        'service': 'f1.sedaily.ai',
        'status': 'running',
        'message': 'f1 로컬 테스트 서버가 실행 중입니다.',
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    })

@app.route('/api/health')
def health():
    return jsonify({
        'status': 'healthy',
        'service': 'f1.sedaily.ai',
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    })

@app.route('/api/conversation', methods=['POST'])
def conversation():
    """대화 API 엔드포인트"""
    try:
        data = request.get_json()
        message = data.get('message', 'Hello')
        
        # 간단한 응답 반환
        response = {
            'success': True,
            'message': f'f1 서비스에서 받은 메시지: {message}',
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'conversationId': 'test-conversation-123'
        }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/prompts', methods=['GET'])
def get_prompts():
    """프롬프트 목록 API"""
    return jsonify({
        'prompts': [
            {'id': 'F1', 'name': 'f1 General Chat', 'description': 'AI 채팅 서비스'}
        ]
    })

if __name__ == '__main__':
    print("🚀 f1.sedaily.ai 간단한 테스트 서버 시작")
    print("📍 URL: http://localhost:5000")
    print("💡 Ctrl+C로 종료")
    
    app.run(host='0.0.0.0', port=5000, debug=True)