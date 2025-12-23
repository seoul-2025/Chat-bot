#!/bin/bash
# D:\one 프로젝트 배포 설정
# ====================================

# AWS Configuration
export AWS_REGION="us-east-1"
export AWS_ACCOUNT_ID="887078546492"

# Service Identification
export SERVICE_NAME="one"
export DOMAIN="your-domain.com"  # 실제 도메인으로 변경 필요

# Lambda Functions
export LAMBDA_FUNCTIONS=(
    "one-websocket-message"
    "one-websocket-connect"
    "one-websocket-disconnect"
    "one-conversation-api"
    "one-usage-handler"
    "one-prompt-crud"
)

# DynamoDB Tables
export DYNAMODB_TABLES=(
    "one-conversations"
    "one-messages"
    "one-prompts"
    "one-usage"
    "one-connections"
)

# S3 Buckets
export FRONTEND_BUCKET="one-frontend-bucket-unique-12345"

# CloudFront Configuration
# 실제 CloudFront Distribution ID로 변경 필요
export CLOUDFRONT_DISTRIBUTION_ID="E1SUZO5B5TC1AU"  # 메인 사이트용 (d3v6ptor2olfy0.cloudfront.net)
export CHAT_CLOUDFRONT_DISTRIBUTION_ID=""  # 채팅 전용 사이트용

# IAM Configuration
export LAMBDA_ROLE="one-lambda-execution-role"

# Secrets Manager
export SECRET_NAME="one-secrets"

# API Configuration
export ANTHROPIC_MODEL="claude-3-5-sonnet-20241022"
export ANTHROPIC_MAX_TOKENS="4096"
export ANTHROPIC_TEMPERATURE="0.7"

# Paths
export BACKEND_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/backend"
export FRONTEND_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export SCRIPTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colors for output
export RED='\033[0;31m'
export GREEN='\033[0;32m'
export YELLOW='\033[1;33m'
export NC='\033[0m' # No Color

# Helper functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}