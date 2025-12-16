# 잘못된 Lambda 함수명을 사용하는 스크립트

이 디렉토리에는 잘못된 Lambda 함수명을 사용하는 스크립트들이 보관되어 있습니다.

## 문제점

### deploy-buddy-v1.sh
- **잘못된 함수명**: `buddy-websocket-message`, `buddy-conversation-api` 등
- **올바른 함수명**: `p2-two-websocket-message-two`, `p2-two-conversation-api-two` 등
- **날짜**: 2024-12-14 이동됨

## 올바른 스크립트

현재 사용해야 하는 올바른 스크립트:
- `/update-buddy-code.sh` - p2-two-* Lambda 함수 배포용
- `/scripts-v2/` 디렉토리의 스크립트들

## 주의사항

이 디렉토리의 스크립트들은 사용하지 마세요. 
b1.sedaily.ai는 p2-two-* Lambda 함수를 사용합니다.