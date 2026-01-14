import requests
from urllib.parse import urlparse
import json
import os
from datetime import datetime

def extract_domain(url):
    """URL에서 도메인 추출"""
    return urlparse(url).netloc

async def perform_web_search_with_content(query):
    """웹검색 + 콘텐츠 수집"""
    
    try:
        # Google Custom Search API 설정
        api_key = os.environ.get('GOOGLE_SEARCH_API_KEY')
        search_engine_id = os.environ.get('GOOGLE_SEARCH_ENGINE_ID')
        
        if not api_key or not search_engine_id:
            print("Google Search API 키가 설정되지 않음")
            return [], ""
        
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            'key': api_key,
            'cx': search_engine_id,
            'q': query + " 뉴스 site:yna.co.kr OR site:hankookilbo.com OR site:chosun.com",
            'num': 5,
            'dateRestrict': 'd3'  # 최근 3일
        }
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        sources = []
        search_context = ""
        
        # 검색 결과 처리
        for item in data.get('items', []):
            domain = extract_domain(item['link'])
            
            if len(sources) < 5:
                sources.append({
                    "title": item['title'][:100],
                    "url": item['link'],
                    "domain": domain
                })
                
                # Claude에게 제공할 검색 컨텍스트 생성
                search_context += f"\n출처: {item['title']} ({domain})\n"
                search_context += f"요약: {item.get('snippet', '')[:200]}\n"
        
        return sources, search_context
        
    except Exception as e:
        print(f"웹검색 오류: {e}")
        return [], ""

def requires_web_search(message):
    """웹검색이 필요한 질문인지 판단"""
    search_keywords = [
        '뉴스', '이슈', '최근', '오늘', '이번주', 
        '현재', '동향', '상황', '발표', '정책',
        '사건', '사고', '트렌드', '화제'
    ]
    return any(keyword in message for keyword in search_keywords)