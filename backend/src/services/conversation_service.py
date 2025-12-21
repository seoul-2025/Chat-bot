"""
대화(Conversation) 비즈니스 로직
"""
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime

from ..models import Conversation, Message
from ..repositories import ConversationRepository

logger = logging.getLogger(__name__)


class ConversationService:
    """대화 관련 비즈니스 로직"""
    
    def __init__(self, repository: Optional[ConversationRepository] = None):
        self.repository = repository or ConversationRepository()
    
    def create_conversation(
        self,
        user_id: str,
        engine_type: str,
        title: Optional[str] = None,
        initial_message: Optional[str] = None
    ) -> Conversation:
        """새 대화 생성"""
        try:
            # 대화 모델 생성
            conversation = Conversation(
                conversation_id='',  # 자동 생성
                user_id=user_id,
                engine_type=engine_type,
                title=title or f"새 대화 - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            )
            
            # 초기 메시지 추가
            if initial_message:
                message = Message(
                    role='user',
                    content=initial_message,
                    timestamp=datetime.now().isoformat()
                )
                conversation.messages.append(message)
            
            # 저장
            saved = self.repository.save(conversation)
            logger.info(f"Conversation created: {saved.conversation_id}")
            
            return saved
            
        except Exception as e:
            logger.error(f"Error creating conversation: {str(e)}")
            raise
    
    def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """대화 조회"""
        try:
            return self.repository.find_by_id(conversation_id)
        except Exception as e:
            logger.error(f"Error getting conversation: {str(e)}")
            raise
    
    def get_user_conversations(
        self,
        user_id: str,
        limit: int = 1000
    ) -> List[Conversation]:
        """사용자의 대화 목록 조회"""
        try:
            return self.repository.find_by_user(user_id, limit)
        except Exception as e:
            logger.error(f"Error getting user conversations: {str(e)}")
            raise
    
    def update_title(self, conversation_id: str, title: str) -> bool:
        """대화 제목 업데이트"""
        try:
            logger.info(f"ConversationService.update_title called: {conversation_id} -> {title}")
            result = self.repository.update_title(conversation_id, title)
            logger.info(f"Repository update_title returned: {result}")
            return result
        except Exception as e:
            logger.error(f"Error in ConversationService.update_title: {str(e)}")
            raise
    
    def delete_conversation(self, conversation_id: str) -> bool:
        """대화 삭제"""
        try:
            return self.repository.delete(conversation_id)
        except Exception as e:
            logger.error(f"Error deleting conversation: {str(e)}")
            raise