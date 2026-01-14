#!/bin/bash

# .env 파일에서 환경변수 로드
if [ -f .env ]; then
    export $(cat .env | xargs)
fi

# 기존 Lambda 함수 업데이트
echo "기존 Lambda 함수 업데이트 중..."

# ZIP 파일 생성
zip -r lambda_function.zip backend/ -x "*.pyc" "__pycache__/*"

# WebSocket 메시지 핸들러 업데이트
aws lambda update-function-code \
    --function-name one-websocket-message \
    --zip-file fileb://lambda_function.zip \
    --region us-east-1

echo "백엔드 업데이트 완료"

# 임시 파일 삭제
rm lambda_function.zip