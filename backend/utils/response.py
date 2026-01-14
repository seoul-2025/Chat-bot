"""
API Response Utilities
통일된 API 응답 포맷 제공
"""
import json
from typing import Any, Dict, Optional


class APIResponse:
    """API 응답 생성 헬퍼"""
    
    # 기본 CORS 헤더
    CORS_HEADERS = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
        'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS,PATCH',
        'Access-Control-Allow-Credentials': 'true'
    }
    
    @classmethod
    def success(cls, data: Any = None, status_code: int = 200) -> Dict:
        """성공 응답 생성"""
        return {
            'statusCode': status_code,
            'headers': cls.CORS_HEADERS,
            'body': json.dumps(data, default=str, ensure_ascii=False)
        }
    
    @classmethod
    def error(cls, message: str, status_code: int = 500) -> Dict:
        """에러 응답 생성"""
        return {
            'statusCode': status_code,
            'headers': cls.CORS_HEADERS,
            'body': json.dumps({'error': message}, ensure_ascii=False)
        }
    
    @classmethod
    def cors_preflight(cls) -> Dict:
        """CORS Preflight 응답"""
        return {
            'statusCode': 200,
            'headers': cls.CORS_HEADERS,
            'body': ''
        }