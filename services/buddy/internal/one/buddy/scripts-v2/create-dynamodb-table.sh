#!/bin/bash

# DynamoDB 테이블 생성 스크립트
TABLE_NAME="p2-two-conversations-two"
REGION="us-east-1"

echo "Creating DynamoDB table: $TABLE_NAME"

# 테이블 생성
aws dynamodb create-table \
    --table-name $TABLE_NAME \
    --attribute-definitions \
        AttributeName=userId,AttributeType=S \
        AttributeName=conversationId,AttributeType=S \
        AttributeName=createdAt,AttributeType=S \
    --key-schema \
        AttributeName=userId,KeyType=HASH \
        AttributeName=conversationId,KeyType=RANGE \
    --global-secondary-indexes \
        '[
            {
                "IndexName": "conversationId-index",
                "Keys": [
                    {"AttributeName":"conversationId","KeyType":"HASH"}
                ],
                "Projection": {"ProjectionType":"ALL"},
                "BillingMode": "PAY_PER_REQUEST"
            },
            {
                "IndexName": "userId-createdAt-index",
                "Keys": [
                    {"AttributeName":"userId","KeyType":"HASH"},
                    {"AttributeName":"createdAt","KeyType":"RANGE"}
                ],
                "Projection": {"ProjectionType":"ALL"},
                "BillingMode": "PAY_PER_REQUEST"
            }
        ]' \
    --billing-mode PAY_PER_REQUEST \
    --region $REGION

echo "Waiting for table to become active..."
aws dynamodb wait table-exists --table-name $TABLE_NAME --region $REGION

# 테이블 상태 확인
aws dynamodb describe-table \
    --table-name $TABLE_NAME \
    --region $REGION \
    --query 'Table.TableStatus' \
    --output text

echo "Table $TABLE_NAME created successfully!"