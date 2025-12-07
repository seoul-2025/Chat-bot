"""
Engine Prompt Service
엔진별 프롬프트 관리를 위한 간단한 서비스 (API Handler 전용)
기존 복잡한 PromptService와 별도로, 엔진 타입별 프롬프트 CRUD만 담당
"""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid
import boto3
from boto3.dynamodb.conditions import Key

import os

logger = logging.getLogger(__name__)


class EnginePromptService:
    """
    엔진 타입별 프롬프트 관리 서비스

    Note: 이 서비스는 prompts, files 테이블 구조에 맞춰
    간단한 CRUD 작업만 수행합니다.
    """

    def __init__(self):
        """서비스 초기화"""
        from src.config.database import get_table_name
        import boto3

        region = os.environ.get('AWS_REGION', 'us-east-1')
        dynamodb = boto3.resource('dynamodb', region_name=region)

        self.prompts_table = dynamodb.Table(get_table_name('prompts'))
        self.files_table = dynamodb.Table(get_table_name('files'))
        logger.info("EnginePromptService initialized")

    def get_prompt_with_files(self, engine_type: str) -> Dict[str, Any]:
        """
        엔진 타입별 프롬프트와 파일 조회

        Args:
            engine_type: 엔진 타입 (예: 'one', 'two')

        Returns:
            프롬프트 정보와 파일 목록
        """
        try:
            # 프롬프트 조회
            response = self.prompts_table.get_item(Key={'promptId': engine_type})
            prompt = response.get('Item', {})

            # 파일 조회
            files = self.get_files(engine_type)

            return {
                'prompt': prompt,
                'files': files
            }

        except Exception as e:
            logger.error(f"Error getting prompt with files for {engine_type}: {e}")
            raise

    def get_prompt(self, engine_type: str) -> Optional[Dict[str, Any]]:
        """
        엔진 타입별 프롬프트 조회

        Args:
            engine_type: 엔진 타입

        Returns:
            프롬프트 정보 또는 None
        """
        try:
            response = self.prompts_table.get_item(Key={'promptId': engine_type})
            return response.get('Item')

        except Exception as e:
            logger.error(f"Error getting prompt for {engine_type}: {e}")
            raise

    def get_all_prompts(self) -> List[Dict[str, Any]]:
        """
        모든 프롬프트 조회

        Returns:
            프롬프트 목록
        """
        try:
            response = self.prompts_table.scan()
            items = response.get('Items', [])

            # 중복 제거 (engineType과 promptId가 같은 경우)
            unique_prompts = {
                item.get('engineType', item.get('promptId')): item
                for item in items
            }

            return list(unique_prompts.values())

        except Exception as e:
            logger.error(f"Error scanning prompts: {e}")
            raise

    def create_or_update_prompt(
        self,
        engine_type: str,
        description: str = '',
        instruction: str = ''
    ) -> Dict[str, Any]:
        """
        프롬프트 생성 또는 업데이트

        Args:
            engine_type: 엔진 타입
            description: 설명
            instruction: 지침

        Returns:
            저장된 프롬프트 정보
        """
        try:
            timestamp = datetime.utcnow().isoformat() + 'Z'

            # 기존 프롬프트 확인
            existing = self.get_prompt(engine_type)

            item = {
                'promptId': engine_type,
                'engineType': engine_type,
                'description': description,
                'instruction': instruction,
                'updatedAt': timestamp
            }

            # 새로 생성하는 경우 createdAt 추가
            if not existing:
                item['createdAt'] = timestamp
            else:
                item['createdAt'] = existing.get('createdAt', timestamp)

            self.prompts_table.put_item(Item=item)

            logger.info(f"Prompt {'created' if not existing else 'updated'}: {engine_type}")
            return item

        except Exception as e:
            logger.error(f"Error creating/updating prompt {engine_type}: {e}")
            raise

    def update_prompt(
        self,
        engine_type: str,
        description: Optional[str] = None,
        instruction: Optional[str] = None
    ) -> bool:
        """
        프롬프트 부분 업데이트

        Args:
            engine_type: 엔진 타입
            description: 설명 (Optional)
            instruction: 지침 (Optional)

        Returns:
            성공 여부
        """
        try:
            # 기존 아이템 가져오기
            existing = self.get_prompt(engine_type)
            if not existing:
                logger.warning(f"Prompt not found: {engine_type}")
                return False

            # 업데이트할 항목만 변경
            updated_item = existing.copy()

            if description is not None:
                updated_item['description'] = description

            if instruction is not None:
                updated_item['instruction'] = instruction

            updated_item['updatedAt'] = datetime.utcnow().isoformat() + 'Z'
            updated_item['promptId'] = engine_type
            updated_item['engineType'] = engine_type

            self.prompts_table.put_item(Item=updated_item)

            logger.info(f"Prompt updated: {engine_type}")
            return True

        except Exception as e:
            logger.error(f"Error updating prompt {engine_type}: {e}")
            raise

    def delete_prompt(self, engine_type: str) -> bool:
        """
        프롬프트 삭제

        Args:
            engine_type: 엔진 타입

        Returns:
            성공 여부
        """
        try:
            self.prompts_table.delete_item(Key={'promptId': engine_type})

            logger.info(f"Prompt deleted: {engine_type}")
            return True

        except Exception as e:
            logger.error(f"Error deleting prompt {engine_type}: {e}")
            raise

    # File Operations

    def get_files(self, engine_type: str) -> List[Dict[str, Any]]:
        """
        엔진 타입별 파일 목록 조회

        Args:
            engine_type: 엔진 타입

        Returns:
            파일 목록
        """
        try:
            response = self.files_table.query(
                KeyConditionExpression=Key('promptId').eq(engine_type)
            )
            return response.get('Items', [])

        except Exception as e:
            logger.error(f"Error getting files for {engine_type}: {e}")
            # 에러 발생 시 빈 리스트 반환 (호환성)
            return []

    def add_file(
        self,
        engine_type: str,
        file_name: str,
        file_content: str
    ) -> Dict[str, Any]:
        """
        파일 추가

        Args:
            engine_type: 엔진 타입
            file_name: 파일 이름
            file_content: 파일 내용

        Returns:
            생성된 파일 정보
        """
        try:
            file_id = str(uuid.uuid4())
            timestamp = datetime.utcnow().isoformat() + 'Z'

            item = {
                'promptId': engine_type,
                'fileId': file_id,
                'fileName': file_name,
                'fileContent': file_content,
                'createdAt': timestamp
            }

            self.files_table.put_item(Item=item)

            logger.info(f"File added: {file_name} for {engine_type}")
            return item

        except Exception as e:
            logger.error(f"Error adding file for {engine_type}: {e}")
            raise

    def update_file(
        self,
        engine_type: str,
        file_id: str,
        file_name: Optional[str] = None,
        file_content: Optional[str] = None
    ) -> bool:
        """
        파일 업데이트

        Args:
            engine_type: 엔진 타입
            file_id: 파일 ID
            file_name: 파일 이름 (Optional)
            file_content: 파일 내용 (Optional)

        Returns:
            성공 여부
        """
        try:
            update_expr = []
            expr_attr_values = {}

            if file_name is not None:
                update_expr.append('fileName = :name')
                expr_attr_values[':name'] = file_name

            if file_content is not None:
                update_expr.append('fileContent = :content')
                expr_attr_values[':content'] = file_content

            if not update_expr:
                logger.warning("No fields to update")
                return False

            update_expr.append('updatedAt = :updated')
            expr_attr_values[':updated'] = datetime.utcnow().isoformat() + 'Z'

            self.files_table.update_item(
                Key={'promptId': engine_type, 'fileId': file_id},
                UpdateExpression='SET ' + ', '.join(update_expr),
                ExpressionAttributeValues=expr_attr_values
            )

            logger.info(f"File updated: {file_id} for {engine_type}")
            return True

        except Exception as e:
            logger.error(f"Error updating file {file_id} for {engine_type}: {e}")
            raise

    def delete_file(self, engine_type: str, file_id: str) -> bool:
        """
        파일 삭제

        Args:
            engine_type: 엔진 타입
            file_id: 파일 ID

        Returns:
            성공 여부
        """
        try:
            self.files_table.delete_item(
                Key={'promptId': engine_type, 'fileId': file_id}
            )

            logger.info(f"File deleted: {file_id} for {engine_type}")
            return True

        except Exception as e:
            logger.error(f"Error deleting file {file_id} for {engine_type}: {e}")
            raise
