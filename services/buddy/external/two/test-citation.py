#!/usr/bin/env python3
"""
Claude Web Search with Citations 테스트
출처 정보가 포함된 웹 검색 테스트
"""

import os
import requests
import json
import boto3

# AWS Secrets Manager에서 API 키 가져오기
secrets_client = boto3.client('secretsmanager', region_name='us-east-1')
response = secrets_client.get_secret_value(SecretId='buddy-v1')
secret = json.loads(response['SecretString'])
API_KEY = secret.get('api_key') or secret.get('API_KEY')

print(f"API Key: {API_KEY[:20]}...")

url = "https://api.anthropic.com/v1/messages"
headers = {
    "x-api-key": API_KEY,
    "anthropic-version": "2023-06-01",
    "content-type": "application/json",
}

# 출처 정보 요청 포함한 테스트
print("\n" + "=" * 60)
print("웹 검색 + 출처 표시 테스트")
print("=" * 60)

# 시스템 프롬프트에 출처 표시 지시
system_prompt = """당신은 정확한 정보를 제공하는 AI 어시스턴트입니다.
웹 검색 결과를 사용할 때는 반드시 다음 형식으로 출처를 표시하세요:
1. 정보 제공 시 [1], [2] 등의 각주 번호 사용
2. 응답 마지막에 "📚 출처:" 섹션 추가
3. 각 출처마다 번호, 제목, URL 표시

예시:
대한민국의 수도는 서울입니다[1].
📚 출처:
[1] 위키백과 - 대한민국 (https://ko.wikipedia.org/wiki/대한민국)
"""

data = {
    "model": "claude-opus-4-5-20251101",
    "max_tokens": 2048,
    "temperature": 0.3,
    "system": system_prompt,
    "messages": [
        {
            "role": "user",
            "content": "오늘 2025년 12월 14일 대한민국 최신 뉴스 2가지를 알려주세요. 각 뉴스의 출처를 명확히 표시해주세요."
        }
    ],
    "tools": [
        {
            "type": "web_search_20250305",
            "name": "web_search",
            "max_uses": 3
        }
    ]
}

print("요청 전송 중...")
resp = requests.post(url, headers=headers, json=data)
print(f"Status: {resp.status_code}")

if resp.status_code == 200:
    result = resp.json()
    print(f"\nModel: {result.get('model', 'unknown')}")
    
    # Usage 정보 출력
    usage = result.get('usage', {})
    print(f"Input tokens: {usage.get('input_tokens', 0)}")
    print(f"Output tokens: {usage.get('output_tokens', 0)}")
    
    # 웹 검색 사용 정보
    if 'server_tool_use' in usage:
        web_searches = usage['server_tool_use'].get('web_search_requests', 0)
        print(f"웹 검색 횟수: {web_searches}")
    
    print("\n" + "=" * 60)
    print("응답 내용:")
    print("=" * 60)
    
    # content 배열 처리
    for content in result.get('content', []):
        if content.get('type') == 'text':
            print(content.get('text', ''))
        elif content.get('type') == 'tool_use':
            print(f"\n[도구 사용: {content.get('name')}]")
            # tool_use 내용도 확인
            if content.get('input'):
                print(f"검색 쿼리: {content.get('input', {}).get('query', 'N/A')}")
    
    # Citation 정보가 있는지 확인
    if 'citations' in result:
        print("\n" + "=" * 60)
        print("인용 정보:")
        print("=" * 60)
        for citation in result['citations']:
            print(f"- {citation.get('title', 'N/A')}")
            print(f"  URL: {citation.get('url', 'N/A')}")
            print(f"  인용 텍스트: {citation.get('cited_text', 'N/A')}")
            print()
    
else:
    print(f"Error: {resp.text[:500]}")
    error_data = resp.json() if resp.headers.get('content-type') == 'application/json' else {}
    if 'error' in error_data:
        print(f"Error details: {error_data['error']}")

print("\n" + "=" * 60)
print("테스트 완료")
print("=" * 60)