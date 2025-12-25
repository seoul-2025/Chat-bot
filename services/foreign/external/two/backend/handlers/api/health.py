"""
Health Check Handler
"""
import json
from datetime import datetime

def handler(event, context):
    """헬스체크 핸들러"""
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Methods': 'GET, POST, OPTIONS'
        },
        'body': json.dumps({
            'status': 'healthy',
            'service': 'f1.sedaily.ai',
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        })
    }