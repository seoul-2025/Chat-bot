import boto3
import json

def test_bedrock_streaming():
    """AWS Bedrock Claude API 스트리밍 테스트"""
    
    try:
        bedrock = boto3.client(
            'bedrock-runtime',
            region_name='us-east-1'
        )
        
        model_id = "anthropic.claude-sonnet-4-5-20251101"
        
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 200,
            "messages": [{
                "role": "user",
                "content": "Python에 대해 간단히 설명해주세요."
            }]
        }
        
        print("Bedrock 스트리밍 테스트 중...")
        
        # 스트리밍 응답
        response = bedrock.invoke_model_with_response_stream(
            modelId=model_id,
            body=json.dumps(body)
        )
        
        print("✅ 스트리밍 응답:")
        
        for event in response['body']:
            if 'chunk' in event:
                chunk_data = json.loads(event['chunk']['bytes'])
                
                if chunk_data['type'] == 'content_block_delta':
                    if 'text' in chunk_data['delta']:
                        print(chunk_data['delta']['text'], end='', flush=True)
        
        print("\n\n✅ 스트리밍 테스트 완료!")
        
    except Exception as e:
        print(f"❌ 스트리밍 테스트 실패: {e}")

if __name__ == "__main__":
    test_bedrock_streaming()