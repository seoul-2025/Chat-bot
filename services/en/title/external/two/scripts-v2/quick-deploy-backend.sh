#!/bin/bash

# 빠른 백엔드 재배포 스크립트
set -e

# 설정 파일 확인
if [ ! -f "config.sh" ]; then
    echo "❌ config.sh 파일이 없습니다. 먼저 ./init.sh를 실행하세요."
    exit 1
fi

source config.sh

echo "========================================="
echo "   🚀 빠른 백엔드 재배포"
echo "   스택: ${STACK_NAME}"
echo "========================================="

# Lambda 함수 목록
LAMBDA_FUNCTIONS=(
    "${SERVICE_NAME}-websocket-connect-${CARD_COUNT}"
    "${SERVICE_NAME}-websocket-disconnect-${CARD_COUNT}"
    "${SERVICE_NAME}-websocket-message-${CARD_COUNT}"
    "${SERVICE_NAME}-conversation-api-${CARD_COUNT}"
    "${SERVICE_NAME}-prompt-crud-${CARD_COUNT}"
    "${SERVICE_NAME}-usage-handler-${CARD_COUNT}"
)

# 백엔드 디렉토리로 이동
cd ../backend

echo "📦 [1/2] 배포 패키지 생성 중..."

# 기존 파일 정리
rm -rf package
rm -f deployment.zip

# 의존성 설치
echo "   📥 의존성 설치..."
pip install -r requirements.txt -t package/ -q

# 소스 코드 복사
echo "   📁 소스 코드 복사..."
cp -r handlers package/ 2>/dev/null || true
cp -r src package/ 2>/dev/null || true
cp -r lib package/ 2>/dev/null || true
cp -r utils package/ 2>/dev/null || true

# 캐시 파일 제거
find package -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find package -type f -name "*.pyc" -delete 2>/dev/null || true

# ZIP 생성
echo "   📦 ZIP 패키지 생성..."
cd package
zip -r ../deployment.zip . -q
cd ..

echo "   ✅ 배포 패키지 생성 완료"
echo ""

echo "🚀 [2/2] Lambda 함수 업데이트 중..."

for FUNCTION_NAME in "${LAMBDA_FUNCTIONS[@]}"; do
    echo "   🔄 $FUNCTION_NAME 업데이트 중..."

    aws lambda update-function-code \
        --function-name $FUNCTION_NAME \
        --zip-file fileb://deployment.zip \
        --region ${REGION} \
        --output text \
        --query 'FunctionName' > /dev/null

    if [ $? -eq 0 ]; then
        echo "      ✅ 업데이트 완료"
    else
        echo "      ❌ 업데이트 실패"
    fi
done

# 정리
echo ""
echo "🧹 임시 파일 정리 중..."
rm -rf package
rm -f deployment.zip

# scripts-v2 디렉토리로 복귀
cd ../scripts-v2

echo ""
echo "========================================="
echo "✅ 백엔드 재배포 완료!"
echo "========================================="
echo ""
echo "📋 업데이트된 Lambda 함수:"
for FUNCTION_NAME in "${LAMBDA_FUNCTIONS[@]}"; do
    echo "   • $FUNCTION_NAME"
done
echo ""
echo "⚡ 변경사항이 즉시 반영되었습니다."
echo "========================================="
