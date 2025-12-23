#!/bin/bash

# Lambda 함수 생성 또는 업데이트
FUNCTION_NAME="claude-api-proxy"
ZIP_FILE="claude-api-lambda.zip"
ROLE_ARN="arn:aws:iam::887078546492:role/one-lambda-execution-role"

echo "🚀 Lambda 함수 배포 시작..."

# 함수 존재 여부 확인
if aws lambda get-function --function-name $FUNCTION_NAME 2>/dev/null; then
    echo "📦 기존 함수 업데이트 중..."
    aws lambda update-function-code \
        --function-name $FUNCTION_NAME \
        --zip-file fileb://$ZIP_FILE
else
    echo "🆕 새 함수 생성 중..."
    aws lambda create-function \
        --function-name $FUNCTION_NAME \
        --runtime nodejs18.x \
        --role $ROLE_ARN \
        --handler lambda-handler.handler \
        --zip-file fileb://$ZIP_FILE \
        --timeout 30 \
        --memory-size 512
fi

# 환경 변수 설정
echo "🔧 환경 변수 설정 중..."
aws lambda update-function-configuration \
    --function-name $FUNCTION_NAME \
    --environment Variables="{CLAUDE_API_KEY=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}"

echo "✅ Lambda 함수 배포 완료!"
echo "📍 함수명: $FUNCTION_NAME"