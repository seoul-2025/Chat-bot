#!/bin/bash

# GSI 추가 스크립트
TABLE_NAME="p2-two-conversations-two"
REGION="us-east-1"

echo "Adding conversationId-index GSI to $TABLE_NAME..."

# GSI 추가
aws dynamodb update-table \
    --table-name $TABLE_NAME \
    --attribute-definitions \
        AttributeName=conversationId,AttributeType=S \
    --global-secondary-index-updates \
        '[
            {
                "Create": {
                    "IndexName": "conversationId-index",
                    "KeySchema": [
                        {"AttributeName":"conversationId","KeyType":"HASH"}
                    ],
                    "Projection": {"ProjectionType":"ALL"}
                }
            }
        ]' \
    --region $REGION

echo "Waiting for GSI to be created..."

# GSI 생성 대기 (최대 5분)
for i in {1..30}; do
    STATUS=$(aws dynamodb describe-table \
        --table-name $TABLE_NAME \
        --region $REGION \
        --query 'Table.GlobalSecondaryIndexes[?IndexName==`conversationId-index`].IndexStatus' \
        --output text 2>/dev/null)
    
    if [ "$STATUS" == "ACTIVE" ]; then
        echo "✅ GSI conversationId-index created successfully!"
        break
    elif [ "$STATUS" == "CREATING" ]; then
        echo "⏳ Creating GSI... (attempt $i/30)"
        sleep 10
    else
        if [ $i -eq 1 ]; then
            echo "Starting GSI creation..."
        fi
        sleep 10
    fi
done

# 최종 GSI 목록 확인
echo ""
echo "Current GSIs:"
aws dynamodb describe-table \
    --table-name $TABLE_NAME \
    --region $REGION \
    --query 'Table.GlobalSecondaryIndexes[*].[IndexName,IndexStatus]' \
    --output table