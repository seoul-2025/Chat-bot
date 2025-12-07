#!/bin/bash

# ============================================
# f1.sedaily.ai - Anthropic API 배포 스크립트
# Claude 4.5 Opus 통합 배포
# ============================================

set -e

# 색상 설정
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# 프로젝트 루트 디렉토리
PROJECT_ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BACKEND_DIR="$PROJECT_ROOT/backend/extracted"
CONFIG_FILE="$PROJECT_ROOT/config/production.env"

# 환경 설정 로드
if [ -f "$CONFIG_FILE" ]; then
    echo -e "${BLUE}📋 환경 설정 로드 중...${NC}"
    source "$CONFIG_FILE"
    echo -e "${GREEN}✅ 설정 로드 완료${NC}"
else
    echo -e "${YELLOW}⚠️  설정 파일 없음. 기본값 사용${NC}"
fi

# Lambda 함수 이름 (f1 서비스 관련 모든 함수들)
LAMBDA_FUNCTIONS=(
    "f1-websocket-message-two"
    "f1-websocket-connect-two"
    "f1-websocket-disconnect-two"
    "f1-conversation-api-two"
    "f1-prompt-crud-two"
    "f1-usage-handler-two"
    "f1-websocket-message"
    "f1-conversation-api"
    "f1-websocket-lambda"
    "f1-api-two"
)

# Nova 버전 함수들
NOVA_FUNCTIONS=(
    "f1-nova-websocket-message-two"
    "f1-nova-websocket-connect-two"
    "f1-nova-websocket-disconnect-two"
    "f1-nova-conversation-api-two"
    "f1-nova-prompt-crud-two"
    "f1-nova-usage-handler-two"
)

# tf1 버전 함수들
TF1_FUNCTIONS=(
    "tf1-websocket-message-two"
    "tf1-websocket-connect-two"
    "tf1-websocket-disconnect-two"
    "tf1-conversation-api-two"
    "tf1-prompt-crud-two"
    "tf1-usage-handler-two"
)

echo ""
echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}   🚀 f1.sedaily.ai Anthropic API 배포${NC}"
echo -e "${CYAN}========================================${NC}"
echo ""

# ============================================
# 1. 의존성 설치 및 패키징
# ============================================
echo -e "${BLUE}1. Python 패키지 설치 중...${NC}"
cd "$PROJECT_ROOT/backend"

# 기존 package 디렉토리 삭제
rm -rf package
mkdir -p package

# 의존성 설치
pip install -r requirements.txt -t package/ --upgrade 2>&1 | tail -5

echo -e "${GREEN}✅ 패키지 설치 완료${NC}"

# ============================================
# 2. 소스 코드 복사
# ============================================
echo ""
echo -e "${BLUE}2. 소스 코드 복사 중...${NC}"

# extracted 디렉토리에서 코드 복사
cd extracted
cp -r handlers ../package/
cp -r lib ../package/
cp -r services ../package/
cp -r utils ../package/
cp -r src ../package/
cd ..

echo -e "${GREEN}✅ 소스 코드 복사 완료${NC}"

# ============================================
# 3. Lambda 패키지 생성
# ============================================
echo ""
echo -e "${BLUE}3. Lambda 배포 패키지 생성 중...${NC}"

cd package
zip -r ../lambda-deployment.zip . -q
cd ..

PACKAGE_SIZE=$(ls -lh lambda-deployment.zip | awk '{print $5}')
echo -e "${GREEN}✅ 배포 패키지 생성 완료 (크기: $PACKAGE_SIZE)${NC}"

# ============================================
# 4. Lambda 함수 업데이트
# ============================================
echo ""
echo -e "${BLUE}4. Lambda 함수 업데이트 중...${NC}"

UPDATED=0
FAILED=0

# 모든 Lambda 함수 업데이트 시도
ALL_FUNCTIONS=("${LAMBDA_FUNCTIONS[@]}" "${NOVA_FUNCTIONS[@]}" "${TF1_FUNCTIONS[@]}")

for func in "${ALL_FUNCTIONS[@]}"; do
    echo -e "${YELLOW}→ $func 확인 중...${NC}"
    
    # 함수 존재 여부 확인
    if aws lambda get-function --function-name $func --region $AWS_REGION &>/dev/null; then
        echo -e "  ${CYAN}함수 발견. 코드 업데이트 중...${NC}"
        
        # 코드 업데이트
        aws lambda update-function-code \
            --function-name $func \
            --zip-file fileb://lambda-deployment.zip \
            --region $AWS_REGION \
            --output json 2>&1 | grep -E "FunctionName|CodeSize" || true
        
        if [ $? -eq 0 ]; then
            echo -e "  ${GREEN}✅ 코드 업데이트 완료${NC}"
            
            # 환경 변수 업데이트
            echo -e "  ${CYAN}환경 변수 업데이트 중...${NC}"
            
            # 기존 환경 변수 가져오기
            EXISTING_VARS=$(aws lambda get-function-configuration \
                --function-name $func \
                --region $AWS_REGION \
                --query 'Environment.Variables' \
                --output json 2>/dev/null || echo "{}")
            
            # 새로운 환경 변수 추가 (기존 환경 변수 유지)
            if [ "$EXISTING_VARS" = "null" ] || [ "$EXISTING_VARS" = "{}" ]; then
                # 환경 변수가 없는 경우 새로 설정
                aws lambda update-function-configuration \
                    --function-name $func \
                    --region $AWS_REGION \
                    --environment Variables='{
                        "USE_ANTHROPIC_API":"'${USE_ANTHROPIC_API:-true}'",
                        "ANTHROPIC_SECRET_NAME":"'${ANTHROPIC_SECRET_NAME:-foreign-v1}'",
                        "ANTHROPIC_MODEL_ID":"'${ANTHROPIC_MODEL_ID:-claude-opus-4-5-20251101}'",
                        "AI_PROVIDER":"'${AI_PROVIDER:-anthropic_api}'",
                        "FALLBACK_TO_BEDROCK":"'${FALLBACK_TO_BEDROCK:-true}'"
                    }' \
                    --timeout 120 \
                    --memory-size 512 \
                    --output json 2>&1 | grep -E "FunctionName|State" || echo "  처리 중..."
            else
                # 기존 환경 변수가 있는 경우 병합
                MERGED_VARS=$(python3 -c "
import json
import os
existing = $EXISTING_VARS
new_vars = {
    'USE_ANTHROPIC_API': '${USE_ANTHROPIC_API:-true}',
    'ANTHROPIC_SECRET_NAME': '${ANTHROPIC_SECRET_NAME:-foreign-v1}',
    'ANTHROPIC_MODEL_ID': '${ANTHROPIC_MODEL_ID:-claude-opus-4-5-20251101}',
    'AI_PROVIDER': '${AI_PROVIDER:-anthropic_api}',
    'FALLBACK_TO_BEDROCK': '${FALLBACK_TO_BEDROCK:-true}'
}
if existing:
    existing.update(new_vars)
    print(json.dumps(existing))
else:
    print(json.dumps(new_vars))
" 2>/dev/null || echo '{"USE_ANTHROPIC_API":"true","ANTHROPIC_SECRET_NAME":"foreign-v1","ANTHROPIC_MODEL_ID":"claude-opus-4-5-20251101","AI_PROVIDER":"anthropic_api","FALLBACK_TO_BEDROCK":"true"}')

                aws lambda update-function-configuration \
                    --function-name $func \
                    --region $AWS_REGION \
                    --environment Variables="$MERGED_VARS" \
                    --timeout 120 \
                    --memory-size 512 \
                    --output json 2>&1 | grep -E "FunctionName|State" || echo "  처리 중..."
            fi
            
            echo -e "  ${GREEN}✅ 환경 변수 업데이트 완료${NC}"
            ((UPDATED++))
        else
            echo -e "  ${RED}❌ 코드 업데이트 실패${NC}"
            ((FAILED++))
        fi
    fi
done

# ============================================
# 5. IAM 권한 확인/추가
# ============================================
echo ""
echo -e "${BLUE}5. IAM 권한 설정 중...${NC}"

# 첫 번째 존재하는 함수에서 역할 가져오기
for func in "${ALL_FUNCTIONS[@]}"; do
    if aws lambda get-function --function-name $func --region $AWS_REGION &>/dev/null; then
        ROLE_ARN=$(aws lambda get-function --function-name $func --region $AWS_REGION --query 'Configuration.Role' --output text)
        ROLE_NAME=$(echo $ROLE_ARN | awk -F'/' '{print $NF}')
        
        echo -e "${CYAN}Lambda 실행 역할: $ROLE_NAME${NC}"
        
        # Secrets Manager 정책 생성
        cat > /tmp/secrets-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "secretsmanager:GetSecretValue"
      ],
      "Resource": "arn:aws:secretsmanager:$AWS_REGION:*:secret:foreign-v1-*"
    }
  ]
}
EOF
        
        # 정책 추가/업데이트
        aws iam put-role-policy \
            --role-name $ROLE_NAME \
            --policy-name AnthropicSecretAccess \
            --policy-document file:///tmp/secrets-policy.json 2>&1 \
            && echo -e "${GREEN}✅ IAM 권한 설정 완료${NC}" \
            || echo -e "${YELLOW}⚠️  IAM 권한이 이미 존재하거나 권한 부족${NC}"
        
        break
    fi
done

# ============================================
# 6. 정리
# ============================================
echo ""
echo -e "${BLUE}6. 정리 작업 중...${NC}"

rm -f lambda-deployment.zip
rm -rf package
rm -f /tmp/secrets-policy.json

echo -e "${GREEN}✅ 정리 완료${NC}"

# ============================================
# 배포 결과
# ============================================
echo ""
echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}   📊 배포 결과${NC}"
echo -e "${CYAN}========================================${NC}"
echo -e "성공: ${GREEN}$UPDATED${NC} / 실패: ${RED}$FAILED${NC}"
echo ""
echo -e "${BLUE}📌 적용된 설정:${NC}"
echo -e "  • AI Provider: ${CYAN}${AI_PROVIDER:-anthropic_api}${NC}"
echo -e "  • Model: ${CYAN}${ANTHROPIC_MODEL_ID:-claude-opus-4-5-20251101}${NC}"
echo -e "  • Fallback: ${CYAN}${FALLBACK_TO_BEDROCK:-true}${NC}"
echo ""
echo -e "${YELLOW}⚠️  다음 단계:${NC}"
echo "  1. AWS Secrets Manager에서 API 키 설정 확인"
echo "  2. CloudWatch Logs에서 동작 확인"
echo "  3. f1.sedaily.ai에서 테스트"
echo ""

if [ $UPDATED -eq 0 ]; then
    echo -e "${RED}⚠️  업데이트된 함수가 없습니다.${NC}"
    echo "  Lambda 함수 목록을 확인하세요:"
    echo "  aws lambda list-functions --region $AWS_REGION --query \"Functions[?contains(FunctionName, 'f1')].FunctionName\""
fi

echo -e "${GREEN}✅ f1.sedaily.ai Anthropic API 배포 완료${NC}"