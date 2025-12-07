"""
WebSocket Service
WebSocket 메시지 처리 및 Bedrock 통합 서비스
"""
import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional, Generator
import uuid

from ..repositories import ConversationRepository
from ..models import Conversation, Message
from ..config.business import CONVERSATION_LIMITS, TEXT_PROCESSING
from ..config.database import AWS_REGION
from lib.bedrock_client_enhanced import BedrockClientEnhanced

logger = logging.getLogger(__name__)


class WebSocketService:
    """WebSocket 메시지 처리 서비스"""

    def __init__(
        self,
        conversation_repository: ConversationRepository = None,
        prompt_service=None,  # PromptService는 순환참조 방지를 위해 나중에 주입
        bedrock_client: BedrockClientEnhanced = None
    ):
        """
        의존성 주입을 통한 초기화

        Args:
            conversation_repository: 대화 저장소 (테스트 시 Mock 가능)
            prompt_service: 프롬프트 서비스
            bedrock_client: Bedrock 클라이언트
        """
        self.conversation_repo = conversation_repository or ConversationRepository()
        self.prompt_service = prompt_service  # PromptService를 나중에 설정
        self.bedrock_client = bedrock_client or BedrockClientEnhanced()
        logger.info("WebSocketService initialized")

    def process_message(
        self,
        user_message: str,
        engine_type: str,
        conversation_id: Optional[str],
        user_id: str,
        conversation_history: List[Dict],
        user_role: str = 'user'
    ) -> Dict[str, Any]:
        """
        메시지 처리 및 대화 히스토리 병합

        Args:
            user_message: 사용자 메시지
            engine_type: 엔진 타입 (one, two, three 등)
            conversation_id: 대화 ID (없으면 새로 생성)
            user_id: 사용자 ID
            conversation_history: 클라이언트에서 전달된 대화 히스토리
            user_role: 사용자 역할

        Returns:
            Dict containing conversation_id and merged_history
        """
        try:
            # 대화 ID가 없으면 생성
            if not conversation_id:
                conversation_id = str(uuid.uuid4())
                logger.info(f"New conversation created: {conversation_id}")

            # DB에서 기존 대화 조회
            conversation = self.conversation_repo.find_by_id(conversation_id)

            # DB에서 기존 대화 히스토리 조회
            db_history = []
            if conversation and conversation.messages:
                # 최근 N개 메시지만 사용
                limit = CONVERSATION_LIMITS['default_history_limit']
                recent_messages = conversation.messages[-limit:] if len(conversation.messages) > limit else conversation.messages
                db_history = [
                    {
                        'role': msg.role,
                        'content': msg.content,
                        'timestamp': msg.timestamp
                    }
                    for msg in recent_messages
                ]

            # 클라이언트 히스토리와 DB 히스토리 병합
            merged_history = self._merge_conversation_history(
                client_history=conversation_history,
                db_history=db_history
            )

            # 사용자 메시지 저장
            self._save_message(
                conversation_id=conversation_id,
                role='user',
                content=user_message,
                engine_type=engine_type,
                user_id=user_id
            )

            # 병합된 히스토리에 현재 메시지 추가
            merged_history.append({
                'role': 'user',
                'content': user_message,
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            })

            logger.info(f"Processed message for conversation {conversation_id}")
            logger.info(f"Merged history length: {len(merged_history)}")

            return {
                'conversation_id': conversation_id,
                'merged_history': merged_history
            }

        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            raise

    def stream_response(
        self,
        user_message: str,
        engine_type: str,
        conversation_id: str,
        user_id: str,
        conversation_history: List[Dict],
        user_role: str = 'user'
    ) -> Generator[str, None, None]:
        """
        Bedrock 스트리밍 응답 생성

        Args:
            user_message: 사용자 메시지
            engine_type: 엔진 타입
            conversation_id: 대화 ID
            user_id: 사용자 ID
            conversation_history: 대화 히스토리
            user_role: 사용자 역할

        Yields:
            str: 응답 청크
        """
        try:
            # 대화 컨텍스트를 포함한 프롬프트 생성
            formatted_history = self._format_conversation_for_bedrock(conversation_history)

            # 프롬프트 데이터 로드 (PromptService 사용)
            prompt_data = self._load_prompt_data(engine_type)
            logger.info(f"Loaded prompt for {engine_type}: instruction={len(prompt_data.get('instruction', ''))} chars")

            logger.info(f"Streaming response for engine {engine_type}")
            logger.info(f"Conversation context: {len(formatted_history)} messages")

            # Bedrock 스트리밍 호출
            total_response = ""
            for chunk in self.bedrock_client.stream_bedrock(
                user_message=user_message,
                engine_type=engine_type,
                conversation_context=formatted_history,  # 대화 컨텍스트 전달
                user_role=user_role,
                guidelines=prompt_data.get('instruction'),  # DynamoDB instruction 전달
                description=prompt_data.get('description'),  # DynamoDB description 전달
                files=prompt_data.get('files', [])  # DynamoDB files 전달
            ):
                total_response += chunk
                yield chunk

            # AI 응답을 대화에 저장
            if total_response:
                self._save_message(
                    conversation_id=conversation_id,
                    role='assistant',
                    content=total_response,
                    engine_type=engine_type,
                    user_id=user_id
                )
                logger.info(f"AI response saved: {len(total_response)} chars")

        except Exception as e:
            logger.error(f"Error streaming response: {str(e)}")
            raise

    def clear_history(self, conversation_id: str) -> bool:
        """
        대화 히스토리 초기화

        Args:
            conversation_id: 대화 ID

        Returns:
            성공 여부
        """
        try:
            conversation = self.conversation_repo.find_by_id(conversation_id)

            if conversation:
                # 메시지만 비우고 대화는 유지
                conversation.messages = []
                conversation.title = "Cleared conversation"
                conversation.updated_at = datetime.now().isoformat()
                self.conversation_repo.save(conversation)

                logger.info(f"Cleared history for conversation {conversation_id}")
                return True
            else:
                logger.warning(f"Conversation not found: {conversation_id}")
                return False

        except Exception as e:
            logger.error(f"Error clearing history: {str(e)}")
            return False

    def track_usage(
        self,
        user_id: str,
        engine_type: str,
        input_text: str,
        output_text: str,
        user_plan: str = 'free'
    ) -> None:
        """
        사용량 추적 및 저장

        Args:
            user_id: 사용자 ID
            engine_type: 엔진 타입
            input_text: 입력 텍스트
            output_text: 출력 텍스트
            user_plan: 사용자 플랜 (free, basic, premium)
        """
        try:
            # SimpleUsageService를 통해 사용량 저장
            from .simple_usage_service import SimpleUsageService

            usage_service = SimpleUsageService()
            result = usage_service.update_usage(
                user_id=user_id,
                engine_type=engine_type,
                input_text=input_text,
                output_text=output_text,
                user_plan=user_plan
            )

            logger.info(f"Usage tracked and saved - User: {user_id}, Engine: {engine_type}")
            logger.info(f"Result: {result}")

        except Exception as e:
            logger.error(f"Error tracking usage: {str(e)}", exc_info=True)

    def _save_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        engine_type: str,
        user_id: str
    ) -> bool:
        """
        메시지 저장 (내부 메서드)

        Args:
            conversation_id: 대화 ID
            role: 역할 (user, assistant)
            content: 메시지 내용
            engine_type: 엔진 타입
            user_id: 사용자 ID

        Returns:
            성공 여부
        """
        try:
            timestamp = datetime.utcnow().isoformat() + 'Z'
            message_id = str(uuid.uuid4())

            # 기존 대화 조회
            conversation = self.conversation_repo.find_by_id(conversation_id)

            if conversation:
                # 기존 대화에 메시지 추가
                new_message = Message(
                    role=role,
                    content=content,
                    timestamp=timestamp,
                    type=role
                )
                conversation.messages.append(new_message)

                # 최근 N개 메시지만 유지 (메모리 관리)
                max_messages = CONVERSATION_LIMITS['max_messages_in_conversation']
                if len(conversation.messages) > max_messages:
                    conversation.messages = conversation.messages[-max_messages:]

                conversation.updated_at = timestamp

            else:
                # 새 대화 생성
                title_length = TEXT_PROCESSING['max_conversation_title_length']
                default_title = TEXT_PROCESSING['default_conversation_title']
                conversation = Conversation(
                    conversation_id=conversation_id,
                    user_id=user_id,
                    engine_type=engine_type,
                    title=content[:title_length] if role == 'user' else default_title,
                    messages=[
                        Message(
                            role=role,
                            content=content,
                            timestamp=timestamp,
                            type=role
                        )
                    ],
                    created_at=timestamp,
                    updated_at=timestamp
                )

            # 저장
            self.conversation_repo.save(conversation)
            logger.info(f"Message saved: {conversation_id} - {role}")
            return True

        except Exception as e:
            logger.error(f"Error saving message: {str(e)}")
            return False

    def _load_prompt_data(self, engine_type: str) -> Dict[str, Any]:
        """
        프롬프트 데이터 로드

        Args:
            engine_type: 엔진 타입

        Returns:
            프롬프트 데이터 (instruction, description, files)
        """
        try:
            # PromptService가 설정되어 있으면 사용
            if self.prompt_service:
                return self.prompt_service.get_prompt_with_files(engine_type)

            # Fallback: 직접 DynamoDB에서 로드 (레거시 호환성)
            from ..config.aws import DYNAMODB_TABLES
            from ..config.database import get_table_name
            import boto3

            dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
            prompts_table = dynamodb.Table(get_table_name('prompts'))
            files_table = dynamodb.Table(get_table_name('files'))

            # 프롬프트 테이블에서 기본 정보 로드
            response = prompts_table.get_item(Key={'promptId': engine_type})
            if 'Item' in response:
                item = response['Item']
                prompt_data = {
                    'instruction': item.get('instruction', ''),
                    'description': item.get('description', ''),
                    'files': []
                }

                # files 테이블에서 관련 파일들 로드
                try:
                    files_response = files_table.scan(
                        FilterExpression='promptId = :promptId',
                        ExpressionAttributeValues={':promptId': engine_type}
                    )

                    if 'Items' in files_response:
                        for file_item in files_response['Items']:
                            prompt_data['files'].append({
                                'fileName': file_item.get('fileName', ''),
                                'fileContent': file_item.get('fileContent', ''),
                                'fileType': 'text'  # 기본값
                            })
                        logger.info(f"Loaded {len(prompt_data['files'])} files for {engine_type}")
                except Exception as fe:
                    logger.error(f"Error loading files: {str(fe)}")

                return prompt_data
            else:
                logger.warning(f"No prompt found for engine type: {engine_type}")
                return {'instruction': '', 'description': '', 'files': []}

        except Exception as e:
            logger.error(f"Error loading prompt data: {str(e)}")
            return {'instruction': '', 'description': '', 'files': []}

    def _merge_conversation_history(
        self,
        client_history: List[Dict],
        db_history: List[Dict]
    ) -> List[Dict]:
        """
        클라이언트와 DB의 대화 히스토리 병합

        DB 히스토리를 기준으로 하되, 클라이언트 히스토리에만 있는 메시지는 추가

        Args:
            client_history: 클라이언트 대화 히스토리
            db_history: DB 대화 히스토리

        Returns:
            병합된 대화 히스토리
        """
        merged = []

        # DB 히스토리를 기본으로 사용
        for msg in db_history:
            merged.append({
                'role': msg.get('role', msg.get('type', 'user')),
                'content': msg.get('content', ''),
                'timestamp': msg.get('timestamp', '')
            })

        # 클라이언트 히스토리에만 있는 메시지 확인 및 추가
        db_timestamps = {msg.get('timestamp') for msg in db_history if msg.get('timestamp')}

        for msg in client_history:
            timestamp = msg.get('timestamp')
            # 타임스탬프가 없거나 DB에 없는 메시지는 새로운 메시지로 간주
            if not timestamp or timestamp not in db_timestamps:
                # 중복 방지를 위해 최근 메시지와 비교
                content = msg.get('content', '')
                if not merged or merged[-1].get('content') != content:
                    merged.append({
                        'role': msg.get('role', 'user'),
                        'content': content,
                        'timestamp': timestamp or datetime.utcnow().isoformat() + 'Z'
                    })

        # 최대 N개 메시지만 유지 (컨텍스트 길이 관리)
        max_merged = CONVERSATION_LIMITS['max_merged_messages']
        if len(merged) > max_merged:
            merged = merged[-max_merged:]

        return merged

    def _format_conversation_for_bedrock(self, conversation_history: List[Dict]) -> str:
        """
        Bedrock에 전달할 대화 컨텍스트 포맷팅

        Args:
            conversation_history: 대화 히스토리

        Returns:
            포맷팅된 대화 컨텍스트 문자열
        """
        if not conversation_history:
            return ""

        formatted_messages = []
        # 최근 N개 메시지만 사용
        max_context = CONVERSATION_LIMITS['max_bedrock_context_messages']
        for msg in conversation_history[-max_context:]:
            role = msg.get('role', 'user')
            content = msg.get('content', '')

            if content:
                if role == 'user':
                    formatted_messages.append(f"사용자: {content}")
                elif role == 'assistant':
                    formatted_messages.append(f"AI: {content}")

        if formatted_messages:
            return "\n\n=== 이전 대화 내용 ===\n" + "\n\n".join(formatted_messages) + "\n\n=== 현재 질문 ==="

        return ""
