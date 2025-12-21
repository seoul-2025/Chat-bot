"""
WebSocket Service
WebSocket 메시지 처리 및 Bedrock 통합 서비스
"""
import json
import boto3
import logging
import time
import os
from datetime import datetime
from decimal import Decimal
from typing import List, Dict, Any, Optional, Generator, Tuple
import uuid

from handlers.websocket.conversation_manager import ConversationManager
from lib.bedrock_client_enhanced import BedrockClientEnhanced
from lib.anthropic_client import AnthropicClient, create_enhanced_system_prompt
from lib.citation_formatter import CitationFormatter
from utils.logger import setup_logger

# Logger 초기화
logger = setup_logger(__name__)

# DynamoDB 클라이언트
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
prompts_table = dynamodb.Table('nx-tt-dev-ver3-prompts')
usage_table = dynamodb.Table('nx-tt-dev-ver3-usage-tracking')

# 프롬프트 캐시 (Lambda 컨테이너 재사용 시 유지 - 영구 캐시)
PROMPT_CACHE: Dict[str, Dict[str, Any]] = {}


class WebSocketService:
    """WebSocket 메시지 처리 서비스"""

    # 토큰당 예상 비용 (USD)
    COST_PER_1K_INPUT_TOKENS = {
        'T5': Decimal('0.003'),
        'H8': Decimal('0.015')
    }
    COST_PER_1K_OUTPUT_TOKENS = {
        'T5': Decimal('0.015'),
        'H8': Decimal('0.075')
    }

    def __init__(self):
        # AI 클라이언트 초기화 (환경변수에 따라 선택)
        use_anthropic = os.environ.get('USE_ANTHROPIC_API', 'false').lower() == 'true'
        if use_anthropic:
            self.ai_client = AnthropicClient()
            self.ai_provider = 'anthropic'
            logger.info("Using Anthropic API (Claude 4.5 Opus)")
        else:
            self.ai_client = BedrockClientEnhanced()
            self.ai_provider = 'bedrock'
            logger.info("Using AWS Bedrock (Claude 3.5 Sonnet)")
        
        # Bedrock 클라이언트도 폴백용으로 유지
        self.bedrock_client = BedrockClientEnhanced()
        self.conversation_manager = ConversationManager()
        self.citation_formatter = CitationFormatter()
        self.prompts_table = prompts_table
        self.usage_table = usage_table
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
        
        Returns:
            Dict containing conversation_id and merged_history
        """
        try:
            # 대화 ID가 없으면 생성
            if not conversation_id:
                conversation_id = str(uuid.uuid4())
                logger.info(f"New conversation created: {conversation_id}")
            
            # DB에서 기존 대화 히스토리 조회
            db_history = self.conversation_manager.get_conversation_history(
                conversation_id, 
                limit=20  # 최근 20개 메시지
                ## 대화기억기능
            )
            
            # 클라이언트 히스토리와 DB 히스토리 병합
            merged_history = self._merge_conversation_history(
                client_history=conversation_history,
                db_history=db_history
            )
            
            # 사용자 메시지를 대화에 저장
            self.conversation_manager.save_message(
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
    
    def _load_prompt_from_dynamodb(self, engine_type: str) -> Dict[str, Any]:
        """
        DynamoDB에서 프롬프트와 파일 로드 (인메모리 영구 캐싱 적용)

        캐싱 전략:
        - 영구 캐시: Lambda 컨테이너 수명 동안 유지
        - DB 조회: 컨테이너 재시작 시에만
        - 대량 문서 조회 비용 대폭 절감
        """
        global PROMPT_CACHE

        try:
            # 캐시 확인 (영구 캐시)
            if engine_type in PROMPT_CACHE:
                logger.info(f"✅ Cache HIT for {engine_type} - DB query skipped")
                return PROMPT_CACHE[engine_type]
            
            logger.info(f"❌ Cache MISS for {engine_type} - fetching from DB")

            # 캐시 미스 - DB에서 로드
            prompt_data = self._fetch_prompt_from_db(engine_type)

            # 캐시 업데이트 (영구 저장)
            PROMPT_CACHE[engine_type] = prompt_data
            logger.info(f"💾 Permanently cached prompt for {engine_type} "
                       f"({len(prompt_data.get('files', []))} files, "
                       f"{len(str(prompt_data))} bytes)")

            return prompt_data

        except Exception as e:
            logger.error(f"Error loading prompt: {str(e)}")
            return {'instruction': '', 'description': '', 'files': []}

    def _fetch_prompt_from_db(self, engine_type: str) -> Dict[str, Any]:
        """
        실제 DB 조회 로직 (캐싱 전용)
        캐시 미스 시에만 호출됨
        """
        try:
            start_time = time.time()

            # 프롬프트 테이블에서 기본 정보 로드
            response = self.prompts_table.get_item(Key={'id': engine_type})
            if 'Item' in response:
                item = response['Item']
                prompt_data = {
                    'instruction': item.get('instruction', ''),
                    'description': item.get('description', ''),
                    'files': []
                }

                # files 테이블에서 관련 파일들 로드
                try:
                    files_table = dynamodb.Table('nx-tt-dev-ver3-files')
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

                        elapsed = (time.time() - start_time) * 1000
                        logger.info(f"🔍 DB fetch for {engine_type}: "
                                  f"{len(prompt_data['files'])} files in {elapsed:.0f}ms")
                except Exception as fe:
                    logger.error(f"Error loading files: {str(fe)}")

                return prompt_data
            else:
                logger.warning(f"No prompt found for engine type: {engine_type}")
                return {'instruction': '', 'description': '', 'files': []}
        except Exception as e:
            logger.error(f"Error fetching from DB: {str(e)}")
            return {'instruction': '', 'description': '', 'files': []}

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

        Yields:
            str: 응답 청크
        """
        try:
            # 대화 컨텍스트를 포함한 프롬프트 생성
            formatted_history = self._format_conversation_for_bedrock(conversation_history)

            # DynamoDB에서 프롬프트 로드 (영구 캐싱 적용)
            prompt_data = self._load_prompt_from_dynamodb(engine_type)

            logger.info(f"Loaded prompt for {engine_type}: instruction={len(prompt_data.get('instruction', ''))} chars")
            logger.info(f"Streaming response for engine {engine_type}")
            logger.info(f"Conversation context: {len(formatted_history)} messages")
            
            # AI 스트리밍 호출 (Anthropic 또는 Bedrock)
            total_response = ""
            
            # 웹 검색 활성화 여부 확인
            enable_web_search = os.environ.get('ENABLE_NATIVE_WEB_SEARCH', 'true').lower() == 'true'
            
            # Anthropic API 사용 시
            if self.ai_provider == 'anthropic' and hasattr(self.ai_client, 'stream_response'):
                try:
                    logger.info(f"Using Anthropic API for {engine_type} (web_search: {enable_web_search})")

                    # 체계적인 시스템 프롬프트 생성 (CoT 기반)
                    # 캐싱 최적화: system_prompt는 정적으로 유지, 대화 히스토리는 별도로 전달
                    full_system_prompt = create_enhanced_system_prompt(
                        prompt_data=prompt_data,
                        engine_type=engine_type,
                        user_role=user_role
                    )

                    for chunk in self.ai_client.stream_response(
                        user_message=user_message,
                        system_prompt=full_system_prompt,
                        conversation_history=conversation_history,  # 대화 히스토리를 별도로 전달
                        enable_web_search=enable_web_search,
                        enable_caching=True  # 프롬프트 캐싱 활성화
                    ):
                        total_response += chunk
                        yield chunk
                        
                except Exception as e:
                    # Anthropic API 실패 시 Bedrock으로 폴백
                    if os.environ.get('FALLBACK_TO_BEDROCK', 'true').lower() == 'true':
                        logger.warning(f"Anthropic API failed, falling back to Bedrock: {str(e)}")
                        total_response = ""
                        for chunk in self.bedrock_client.stream_bedrock(
                            user_message=user_message,
                            engine_type=engine_type,
                            conversation_context=formatted_history,
                            user_role=user_role,
                            guidelines=prompt_data.get('instruction'),
                            description=prompt_data.get('description'),
                            files=prompt_data.get('files', [])
                        ):
                            total_response += chunk
                            yield chunk
                    else:
                        raise
            
            # Bedrock 사용 시 (기존 로직)
            else:
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
            
            # 웹 검색 출처 포맷팅 적용 (Anthropic API 사용 시)
            if total_response and self.ai_provider == 'anthropic' and enable_web_search:
                # 출처가 자동으로 포함되지 않은 경우에만 포맷팅 적용
                if "📚 출처:" not in total_response and "http" in total_response:
                    formatted_response = self.citation_formatter.format_response_with_citations(total_response)
                    total_response = formatted_response
                    logger.info("Citation formatting applied")
            
            # AI 응답을 대화에 저장
            if total_response:
                self.conversation_manager.save_message(
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
        """대화 히스토리 초기화"""
        try:
            # 새로운 대화로 재생성
            self.conversation_manager.create_or_update_conversation(
                conversation_id=conversation_id,
                title="Cleared conversation"
            )
            logger.info(f"Cleared history for conversation {conversation_id}")
            return True
        except Exception as e:
            logger.error(f"Error clearing history: {str(e)}")
            return False
    
    def track_usage(
        self,
        user_id: str,
        engine_type: str,
        input_text: str,
        output_text: str
    ) -> None:
        """사용량 추적"""
        try:
            # 토큰 계산 (간단한 추정)
            input_tokens = int(len(input_text.split()) * 1.3)
            output_tokens = int(len(output_text.split()) * 1.3)
            total_tokens = input_tokens + output_tokens

            # 현재 년월 (YYYY-MM)
            now = datetime.now()
            year_month = now.strftime('%Y-%m')

            # DynamoDB 키 (실제 테이블 구조에 맞춤)
            pk = f"user#{user_id}"
            sk = f"engine#{engine_type}#{year_month}"

            # 업데이트
            self.usage_table.update_item(
                Key={
                    'PK': pk,
                    'SK': sk
                },
                UpdateExpression="""
                    SET messageCount = if_not_exists(messageCount, :zero) + :one,
                        inputTokens = if_not_exists(inputTokens, :zero) + :input,
                        outputTokens = if_not_exists(outputTokens, :zero) + :output,
                        totalTokens = if_not_exists(totalTokens, :zero) + :total,
                        engineType = :engine,
                        userId = :userId,
                        yearMonth = :yearMonth,
                        updatedAt = :now,
                        lastUsedAt = :now
                """,
                ExpressionAttributeValues={
                    ':zero': 0,
                    ':one': 1,
                    ':input': input_tokens,
                    ':output': output_tokens,
                    ':total': total_tokens,
                    ':engine': engine_type,
                    ':userId': user_id,
                    ':yearMonth': year_month,
                    ':now': now.isoformat()
                }
            )

            logger.info(f"Usage tracked: {user_id}, {engine_type}, "
                       f"tokens={input_tokens}+{output_tokens}")

        except Exception as e:
            logger.error(f"Error tracking usage: {str(e)}", exc_info=True)
    
    def _merge_conversation_history(
        self,
        client_history: List[Dict],
        db_history: List[Dict]
    ) -> List[Dict]:
        """
        클라이언트와 DB의 대화 히스토리 병합
        
        DB 히스토리를 기준으로 하되, 클라이언트 히스토리에만 있는 메시지는 추가
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
        
        # 최대 30개 메시지만 유지 (컨텍스트 길이 관리) #대화기억기능
        if len(merged) > 30:
            merged = merged[-30:]
        
        return merged

    def _format_conversation_for_bedrock(self, conversation_history: List[Dict]) -> str:
        """
        Bedrock에 전달할 대화 컨텍스트 포맷팅
        """
        if not conversation_history:
            return ""
        
        formatted_messages = []
        for msg in conversation_history[-10:]:  # 최근 10개 메시지만 사용 #대화기억기능
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