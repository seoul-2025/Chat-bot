import boto3
import json
import os

def test_bedrock_connection():
    """AWS Bedrock Claude API 연결 테스트"""
    
    try:
        # AWS Bedrock 클라이언트 생성
        bedrock = boto3.client(
            'bedrock-runtime',
            region_name='us-east-1'
        )
        
        # Claude 3.5 Sonnet 모델 ID
        model_id = "anthropic.claude-sonnet-4-5-20251101"
        
        # 테스트 메시지
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 100,
            "messages": [{
                "role": "user",
                "content": "안녕하세요! 간단한 테스트 메시지입니다."
            }]
        }
        
        print("Bedrock 연결 테스트 중...")
        
        # API 호출
        response = bedrock.invoke_model(
            modelId=model_id,
            body=json.dumps(body)
        )
        
        # 응답 파싱
        response_body = json.loads(response['body'].read())
        
        print("✅ Bedrock 연결 성공!")
        print(f"응답: {response_body['content'][0]['text']}")
        
    except Exception as e:
        print(f"❌ Bedrock 연결 실패: {e}")
        print("AWS 자격 증명과 권한을 확인하세요.")

if __name__ == "__main__":
    test_bedrock_connection()