#!/usr/bin/env python3
"""
Anthropic API 직접 테스트 - Web Search 기능
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

# 테스트 1: 웹 검색 도구 포함
print("\n" + "=" * 60)
print("TEST 1: With Web Search Tool")
print("=" * 60)

data_with_search = {
    "model": "claude-opus-4-5-20251101",
    "max_tokens": 512,
    "temperature": 0.3,
    "messages": [
        {
            "role": "user",
            "content": "오늘 2025년 12월 14일 대한민국 최신 뉴스를 알려주세요. 웹 검색을 사용해서 실시간 정보를 제공해주세요."
        }
    ],
    "tools": [
        {
            "type": "web_search_20250305",
            "name": "web_search",
            "max_uses": 3
        }
    ],
}

resp1 = requests.post(url, headers=headers, data=json.dumps(data_with_search))
print(f"Status: {resp1.status_code}")

if resp1.status_code == 200:
    result = resp1.json()
    print(f"Model: {result.get('model', 'unknown')}")
    print(f"Usage: {result.get('usage', {})}")
    print("\nResponse:")
    print("-" * 40)
    
    # content 배열 처리
    for content in result.get('content', []):
        if content.get('type') == 'text':
            print(content.get('text', ''))
        elif content.get('type') == 'tool_use':
            print(f"[Tool Used: {content.get('name')}]")
    print("-" * 40)
else:
    print(f"Error: {resp1.text[:500]}")

# 테스트 2: 웹 검색 도구 없이
print("\n" + "=" * 60)
print("TEST 2: Without Web Search Tool")
print("=" * 60)

data_without_search = {
    "model": "claude-opus-4-5-20251101",
    "max_tokens": 512,
    "temperature": 0.3,
    "messages": [
        {
            "role": "user",
            "content": "오늘 2025년 12월 14일 대한민국 최신 뉴스를 알려주세요."
        }
    ]
}

resp2 = requests.post(url, headers=headers, data=json.dumps(data_without_search))
print(f"Status: {resp2.status_code}")

if resp2.status_code == 200:
    result = resp2.json()
    print("\nResponse preview (first 500 chars):")
    print("-" * 40)
    for content in result.get('content', []):
        if content.get('type') == 'text':
            text = content.get('text', '')
            print(text[:500] + "..." if len(text) > 500 else text)
            break
    print("-" * 40)
    
    # 날짜 체크
    full_text = ''.join([c.get('text', '') for c in result.get('content', []) if c.get('type') == 'text'])
    if '2025' in full_text:
        print("✅ Contains 2025 date")
    if '2024' in full_text:
        print("⚠️  Contains 2024 date (outdated)")
else:
    print(f"Error: {resp2.text[:500]}")

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)