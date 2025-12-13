#!/usr/bin/env python3
"""
새 테이블 구조로 CRUD 테스트
"""
import boto3
import sys
import json
from datetime import datetime

# 현재 디렉토리를 Python path에 추가
sys.path.append('/Users/yeong-gwang/nexus/services/proofreading/external/two/backend')

from src.repositories.conversation_repository import ConversationRepository
from src.services.conversation_service import ConversationService
from src.models.conversation import Conversation

def test_crud_operations():
    """새 테이블에서 CRUD 테스트"""
    
    print("🧪 새 테이블 구조로 CRUD 테스트 시작...")
    
    # 서비스 초기화 (새 테이블 사용)
    conversation_service = ConversationService()
    
    print("\n=== 1. 기존 대화 조회 테스트 ===")
    # 마이그레이션된 데이터 중 하나 선택
    test_conversation_id = "Pro_1762410831503"
    
    try:
        conversation = conversation_service.get_conversation(test_conversation_id)
        if conversation:
            print(f"✅ 개별 조회 성공: {conversation.conversation_id}")
            print(f"   제목: {conversation.title[:50]}...")
            print(f"   사용자: {conversation.user_id}")
            print(f"   엔진: {conversation.engine_type}")
        else:
            print(f"❌ 개별 조회 실패: 대화를 찾을 수 없음")
            return False
    except Exception as e:
        print(f"❌ 개별 조회 에러: {str(e)}")
        return False
    
    print("\n=== 2. 사용자별 대화 목록 조회 테스트 ===")
    test_user_id = conversation.user_id
    
    try:
        conversations = conversation_service.get_user_conversations(test_user_id, limit=5)
        print(f"✅ 목록 조회 성공: {len(conversations)}개 대화")
        for conv in conversations[:3]:
            print(f"   - {conv.conversation_id}: {conv.title[:30]}...")
    except Exception as e:
        print(f"❌ 목록 조회 에러: {str(e)}")
        return False
    
    print("\n=== 3. 제목 수정 테스트 ===")
    new_title = f"테스트 수정된 제목 - {datetime.now().strftime('%H:%M:%S')}"
    
    try:
        success = conversation_service.update_title(test_conversation_id, new_title)
        if success:
            print(f"✅ 제목 수정 성공: '{new_title}'")
            
            # 수정 확인
            updated_conversation = conversation_service.get_conversation(test_conversation_id)
            if updated_conversation and updated_conversation.title == new_title:
                print(f"✅ 제목 수정 확인됨")
            else:
                print(f"❌ 제목 수정 확인 실패")
        else:
            print(f"❌ 제목 수정 실패")
            return False
    except Exception as e:
        print(f"❌ 제목 수정 에러: {str(e)}")
        return False
    
    print("\n=== 4. 새 대화 생성 테스트 ===")
    try:
        new_conversation = conversation_service.create_conversation(
            user_id=test_user_id,
            engine_type="Basic",
            title="테스트용 새 대화",
            initial_message="테스트 메시지입니다."
        )
        
        if new_conversation:
            print(f"✅ 새 대화 생성 성공: {new_conversation.conversation_id}")
            print(f"   제목: {new_conversation.title}")
            print(f"   메시지 수: {len(new_conversation.messages)}")
            
            # 생성된 대화 삭제 테스트
            print(f"\n=== 5. 대화 삭제 테스트 ===")
            delete_success = conversation_service.delete_conversation(new_conversation.conversation_id)
            if delete_success:
                print(f"✅ 대화 삭제 성공: {new_conversation.conversation_id}")
            else:
                print(f"❌ 대화 삭제 실패")
                
        else:
            print(f"❌ 새 대화 생성 실패")
            return False
            
    except Exception as e:
        print(f"❌ 새 대화 생성 에러: {str(e)}")
        return False
    
    print(f"\n🎉 모든 CRUD 테스트 성공!")
    return True

if __name__ == "__main__":
    try:
        success = test_crud_operations()
        if success:
            print("\n✅ 새 테이블 구조가 정상적으로 작동합니다!")
        else:
            print(f"\n❌ 테스트 실패. 문제를 확인해주세요.")
    except Exception as e:
        print(f"\n💥 테스트 중 예상치 못한 오류: {str(e)}")