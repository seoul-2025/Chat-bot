"""
대화(Conversation) 리포지토리
DynamoDB와의 모든 상호작용을 캡슐화
"""
import boto3
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
import logging
import os

from ..models import Conversation, Message

logger = logging.getLogger(__name__)


class ConversationRepository:
    """대화 데이터 접근 계층"""

    def __init__(self, table_name: str = None, region: str = None):
        table_name = table_name or os.environ.get('CONVERSATIONS_TABLE', 'one-conversations')
        region = region or os.environ.get('AWS_REGION', 'us-east-1')
        self.dynamodb = boto3.resource('dynamodb', region_name=region)
        self.table = self.dynamodb.Table(table_name)
        logger.info(f"ConversationRepository initialized with table: {table_name}")
    
    def save(self, conversation: Conversation) -> Conversation:
        """대화 저장"""
        try:
            # ID가 없으면 생성
            if not conversation.conversation_id:
                conversation.conversation_id = str(uuid.uuid4())
            
            # 타임스탬프 업데이트
            now = datetime.now().isoformat()
            if not conversation.created_at:
                conversation.created_at = now
            conversation.updated_at = now
            
            # DynamoDB에 저장
            self.table.put_item(Item=conversation.to_dict())
            
            logger.info(f"Conversation saved: {conversation.conversation_id}")
            return conversation
            
        except Exception as e:
            logger.error(f"Error saving conversation: {str(e)}")
            raise
    
    def find_by_id(self, conversation_id: str) -> Optional[Conversation]:
        """ID로 대화 조회"""
        try:
            response = self.table.get_item(
                Key={'conversationId': conversation_id}
            )
            
            if 'Item' in response:
                return Conversation.from_dict(response['Item'])
            
            return None
            
        except Exception as e:
            logger.error(f"Error finding conversation by id: {str(e)}")
            raise
    
    def find_by_user(self, user_id: str, limit: int = 1000) -> List[Conversation]:
        """사용자별 대화 목록 조회"""
        try:
            conversations = []
            last_evaluated_key = None
            
            while True:
                scan_params = {
                    'FilterExpression': 'userId = :userId',
                    'ExpressionAttributeValues': {
                        ':userId': user_id
                    }
                }

                if limit and limit < 1000:
                    scan_params['Limit'] = limit * 10

                if last_evaluated_key:
                    scan_params['ExclusiveStartKey'] = last_evaluated_key

                response = self.table.scan(**scan_params)
                
                for item in response.get('Items', []):
                    conversations.append(Conversation.from_dict(item))
                
                if limit and len(conversations) >= limit:
                    return conversations[:limit]
                
                last_evaluated_key = response.get('LastEvaluatedKey')
                if not last_evaluated_key:
                    break
            
            return conversations
            
        except Exception as e:
            logger.error(f"Error finding conversations by user: {str(e)}")
            raise
    
    def update_title(self, conversation_id: str, title: str) -> bool:
        """대화 제목 업데이트"""
        try:
            logger.info(f"Updating title for conversation: {conversation_id} to: {title}")
            
            response = self.table.update_item(
                Key={'conversationId': conversation_id},
                UpdateExpression='SET title = :title, updatedAt = :updatedAt',
                ExpressionAttributeValues={
                    ':title': title,
                    ':updatedAt': datetime.now().isoformat()
                },
                ReturnValues='UPDATED_NEW'
            )
            
            logger.info(f"Title successfully updated for conversation: {conversation_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating title for {conversation_id}: {str(e)}")
            raise
    
    def delete(self, conversation_id: str) -> bool:
        """대화 삭제"""
        try:
            self.table.delete_item(
                Key={'conversationId': conversation_id}
            )
            
            logger.info(f"Conversation deleted: {conversation_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting conversation: {str(e)}")
            raise