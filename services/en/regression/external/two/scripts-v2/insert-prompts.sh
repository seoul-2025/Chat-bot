#!/bin/bash
source config.sh

echo "==========================================="
echo "   초기 프롬프트 데이터 생성"
echo "   테이블: ${PROMPTS_TABLE}"
echo "==========================================="

# 프롬프트 11 생성 (엔진 11용 - Quick Edit)
echo "📝 프롬프트 11 생성 중..."
aws dynamodb put-item \
  --table-name ${PROMPTS_TABLE} \
  --item '{
    "promptId": {"S": "11"},
    "userId": {"S": "system"},
    "engineType": {"S": "11"},
    "promptName": {"S": "Quick Edit Prompt"},
    "description": {"S": "Quick editing engine for articles under 1,000 words. Optimized for first sentence impact and mobile readability."},
    "instruction": {"S": "You are an expert article editor specializing in quick editing. Transform articles under 1,000 words for maximum impact. Focus on: 1) Creating killer opening sentences, 2) Moving buried exclusives to paragraph 1, 3) Converting large numbers to relatable figures, 4) Applying Seoul Economic Daily style guide, 5) Optimizing for mobile first-screen viewing, 6) Pre-empting desk feedback."},
    "isPublic": {"BOOL": true},
    "createdAt": {"S": "'$(date -u +"%Y-%m-%dT%H:%M:%SZ")'"},
    "updatedAt": {"S": "'$(date -u +"%Y-%m-%dT%H:%M:%SZ")'"}
  }' \
  --region ${REGION}

if [ $? -eq 0 ]; then
  echo "✅ 프롬프트 11 생성 완료"
else
  echo "❌ 프롬프트 11 생성 실패"
fi

# 프롬프트 22 생성 (엔진 22용 - Deep Edit)
echo "📝 프롬프트 22 생성 중..."
aws dynamodb put-item \
  --table-name ${PROMPTS_TABLE} \
  --item '{
    "promptId": {"S": "22"},
    "userId": {"S": "system"},
    "engineType": {"S": "22"},
    "promptName": {"S": "Deep Edit Prompt"},
    "description": {"S": "Structural analysis proofreading for articles over 1,000 words. Redesigns narrative structure for maximum reader engagement from start to finish."},
    "instruction": {"S": "You are an expert article editor specializing in structural analysis. Transform long-form articles (1,000+ words) into engaging narratives that readers finish. Focus on: 1) Designing tension-maintaining structure, 2) Converting flat listings into dramatic narrative arcs, 3) Transforming boring data into compelling stories, 4) Managing reader fatigue with strategic breathing spots, 5) Discovering and placing buried killer facts in optimal positions, 6) Creating structures that even rival journalists read to the end."},
    "isPublic": {"BOOL": true},
    "createdAt": {"S": "'$(date -u +"%Y-%m-%dT%H:%M:%SZ")'"},
    "updatedAt": {"S": "'$(date -u +"%Y-%m-%dT%H:%M:%SZ")'"}
  }' \
  --region ${REGION}

if [ $? -eq 0 ]; then
  echo "✅ 프롬프트 22 생성 완료"
else
  echo "❌ 프롬프트 22 생성 실패"
fi

echo ""
echo "==========================================="
echo "✅ 초기 프롬프트 데이터 생성 완료"
echo "==========================================="
echo ""
echo "📊 생성된 프롬프트 확인:"
aws dynamodb scan --table-name ${PROMPTS_TABLE} --region ${REGION} --query 'Items[*].[promptId.S, promptName.S, engineType.S]' --output table
