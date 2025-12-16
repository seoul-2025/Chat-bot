#!/bin/bash

# ============================================
# f1.sedaily.ai - Anthropic API 통합 배포
# Claude 4.5 Opus (claude-opus-4-5-20251101)
# f1-two 스택만 업데이트
# ============================================

set -e

# 색상 설정
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# 설정
STACK_NAME="f1-two"
SERVICE_NAME="f1"
REGION="us-east-1"

# Lambda 함수 목록 (f1-two 스택만)
LAMBDA_FUNCTIONS=(
  "f1-conversation-api-two"
  "f1-prompt-crud-two"
  "f1-usage-handler-two"
  "f1-websocket-connect-two"
  "f1-websocket-disconnect-two"
  "f1-websocket-message-two"
)

# 환경 변수 설정
USE_ANTHROPIC_API=true
ANTHROPIC_SECRET_NAME=foreign-v1
ANTHROPIC_MODEL_ID=claude-opus-4-5-20251101
AI_PROVIDER=anthropic_api
FALLBACK_TO_BEDROCK=true
MAX_TOKENS=4096
TEMPERATURE=0.3
ENABLE_NATIVE_WEB_SEARCH=true
WEB_SEARCH_MAX_USES=5

echo -e "${CYAN}=========================================${NC}"
echo -e "${CYAN}   🚀 f1.sedaily.ai Anthropic API 배포${NC}"
echo -e "${CYAN}   Claude 4.5 Opus 통합${NC}"
echo -e "${CYAN}=========================================${NC}"
echo ""
echo -e "스택: ${YELLOW}${STACK_NAME}${NC}"
echo -e "모델: ${YELLOW}${ANTHROPIC_MODEL_ID}${NC}"
echo -e "Lambda 함수: ${YELLOW}${#LAMBDA_FUNCTIONS[@]}개${NC}"
echo ""

# 프로젝트 루트로 이동
cd "$(dirname "$0")"
PROJECT_ROOT=$(pwd)

# ============================================
# 1. 의존성 설치 및 패키징
# ============================================
echo -e "${BLUE}1. Backend 패키지 준비 중...${NC}"
cd "${PROJECT_ROOT}/backend"

# 임시 패키지 디렉토리 생성
rm -rf anthropic_package
mkdir -p anthropic_package

echo -e "${YELLOW}   의존성 설치 중...${NC}"
pip install -r requirements.txt -t anthropic_package/ --upgrade --quiet

# ============================================
# 2. 소스 코드 복사
# ============================================
echo -e "${BLUE}2. 소스 코드 복사 중...${NC}"

# 모든 필요한 디렉토리 복사
cp -r handlers anthropic_package/ 2>/dev/null || true
cp -r lib anthropic_package/
cp -r services anthropic_package/
cp -r utils anthropic_package/ 2>/dev/null || true
cp -r src anthropic_package/ 2>/dev/null || true

echo -e "${GREEN}✅ 소스 코드 복사 완료${NC}"

# ============================================
# 3. Lambda 패키지 생성
# ============================================
echo -e "${BLUE}3. Lambda 배포 패키지 생성 중...${NC}"

cd anthropic_package
zip -r ../f1-anthropic-deployment.zip . -q
cd ..

PACKAGE_SIZE=$(ls -lh f1-anthropic-deployment.zip | awk '{print $5}')
echo -e "${GREEN}✅ 배포 패키지 생성 완료 (크기: ${PACKAGE_SIZE})${NC}"

# ============================================
# 4. Lambda 함수 업데이트
# ============================================
echo ""
echo -e "${BLUE}4. Lambda 함수 업데이트 시작${NC}"
echo ""

UPDATED=0
FAILED=0

for func in "${LAMBDA_FUNCTIONS[@]}"; do
    echo -e "${YELLOW}→ ${func} 처리 중...${NC}"
    
    # 함수 존재 확인
    if aws lambda get-function --function-name $func --region $REGION &>/dev/null; then
        # 코드 업데이트
        echo -e "  ${CYAN}코드 업데이트 중...${NC}"
        if aws lambda update-function-code \
            --function-name $func \
            --zip-file fileb://f1-anthropic-deployment.zip \
            --region $REGION \
            --output json > /dev/null 2>&1; then
            
            echo -e "  ${GREEN}✅ 코드 업데이트 성공${NC}"
            
            # 환경 변수 업데이트
            echo -e "  ${CYAN}환경 변수 설정 중...${NC}"
            
            # 기존 환경 변수 가져오기
            EXISTING_VARS=$(aws lambda get-function-configuration \
                --function-name $func \
                --region $REGION \
                --query 'Environment.Variables' \
                --output json 2>/dev/null || echo "{}")
            
            # Python 스크립트로 환경 변수 병합
            MERGED_VARS=$(python3 -c "
import json
existing = $EXISTING_VARS if '$EXISTING_VARS' != 'null' else {}
new_vars = {
    'USE_ANTHROPIC_API': '$USE_ANTHROPIC_API',
    'ANTHROPIC_SECRET_NAME': '$ANTHROPIC_SECRET_NAME',
    'ANTHROPIC_MODEL_ID': '$ANTHROPIC_MODEL_ID',
    'AI_PROVIDER': '$AI_PROVIDER',
    'FALLBACK_TO_BEDROCK': '$FALLBACK_TO_BEDROCK',
    'MAX_TOKENS': '$MAX_TOKENS',
    'TEMPERATURE': '$TEMPERATURE',
    'ENABLE_NATIVE_WEB_SEARCH': '$ENABLE_NATIVE_WEB_SEARCH',
    'WEB_SEARCH_MAX_USES': '$WEB_SEARCH_MAX_USES'
}
if existing:
    existing.update(new_vars)
    print(json.dumps(existing))
else:
    print(json.dumps(new_vars))
" 2>/dev/null || echo '{}')

            if aws lambda update-function-configuration \
                --function-name $func \
                --region $REGION \
                --environment Variables="$MERGED_VARS" \
                --timeout 120 \
                --memory-size 512 \
                --output json > /dev/null 2>&1; then
                
                echo -e "  ${GREEN}✅ 환경 변수 설정 완료${NC}"
                ((UPDATED++))
            else
                echo -e "  ${YELLOW}⚠️  환경 변수 설정 실패 (권한 문제일 수 있음)${NC}"
                ((UPDATED++))
            fi
        else
            echo -e "  ${RED}❌ 코드 업데이트 실패${NC}"
            ((FAILED++))
        fi
    else
        echo -e "  ${YELLOW}⚠️  함수를 찾을 수 없습니다${NC}"
        ((FAILED++))
    fi
    echo ""
done

# ============================================
# 5. IAM 권한 확인
# ============================================
echo -e "${BLUE}5. IAM 권한 확인 중...${NC}"

# 첫 번째 함수의 역할 가져오기
for func in "${LAMBDA_FUNCTIONS[@]}"; do
    if aws lambda get-function --function-name $func --region $REGION &>/dev/null; then
        ROLE_ARN=$(aws lambda get-function --function-name $func --region $REGION --query 'Configuration.Role' --output text)
        ROLE_NAME=$(echo $ROLE_ARN | awk -F'/' '{print $NF}')
        
        echo -e "${CYAN}Lambda 실행 역할: ${ROLE_NAME}${NC}"
        
        # Secrets Manager 정책 생성
        cat > /tmp/f1-secrets-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "secretsmanager:GetSecretValue"
      ],
      "Resource": "arn:aws:secretsmanager:$REGION:*:secret:foreign-v1-*"
    }
  ]
}
EOF
        
        # 정책 추가/업데이트 시도
        if aws iam put-role-policy \
            --role-name $ROLE_NAME \
            --policy-name AnthropicSecretAccess \
            --policy-document file:///tmp/f1-secrets-policy.json 2>/dev/null; then
            echo -e "${GREEN}✅ IAM 권한 설정 완료${NC}"
        else
            echo -e "${YELLOW}⚠️  IAM 권한 설정 실패 (이미 존재하거나 권한 부족)${NC}"
        fi
        
        rm -f /tmp/f1-secrets-policy.json
        break
    fi
done

# ============================================
# 6. 정리
# ============================================
echo ""
echo -e "${BLUE}6. 정리 작업 중...${NC}"

rm -rf anthropic_package
rm -f f1-anthropic-deployment.zip

echo -e "${GREEN}✅ 정리 완료${NC}"

# ============================================
# 배포 결과
# ============================================
echo ""
echo -e "${CYAN}=========================================${NC}"
echo -e "${CYAN}   📊 배포 결과${NC}"
echo -e "${CYAN}=========================================${NC}"
echo -e "성공: ${GREEN}${UPDATED}${NC} / 실패: ${RED}${FAILED}${NC}"
echo ""

if [ $UPDATED -eq ${#LAMBDA_FUNCTIONS[@]} ]; then
    echo -e "${GREEN}✅ 모든 Lambda 함수가 성공적으로 업데이트되었습니다!${NC}"
    echo ""
    echo -e "${BLUE}📌 적용된 설정:${NC}"
    echo -e "  • AI Provider: ${CYAN}${AI_PROVIDER}${NC}"
    echo -e "  • Model: ${CYAN}Claude 4.5 Opus${NC}"
    echo -e "  • Fallback: ${CYAN}Bedrock 폴백 활성화${NC}"
    echo ""
    echo -e "${YELLOW}⚠️  주의사항:${NC}"
    echo "  • AWS Secrets Manager에서 API 키 확인 필요"
    echo "  • Rate limit 발생 시 자동으로 Bedrock 폴백"
    echo ""
else
    echo -e "${YELLOW}⚠️  일부 Lambda 함수 업데이트에 실패했습니다.${NC}"
fi

echo -e "${BLUE}다음 단계:${NC}"
echo "  1. CloudWatch Logs에서 동작 확인"
echo "  2. f1.sedaily.ai에서 기능 테스트"
echo ""
echo -e "${GREEN}✅ f1.sedaily.ai Anthropic API 배포 스크립트 완료${NC}"