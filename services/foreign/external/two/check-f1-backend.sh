#!/bin/bash

echo "🔍 f1 백엔드 상태 확인 중..."

# API Gateway 확인
echo "1. API Gateway 상태:"
aws apigateway get-rest-apis --query 'items[?name==`f1-two-backend-dev`].{Name:name,Id:id,Status:endpointConfiguration.types[0]}' --output table

# Lambda 함수 확인
echo "2. Lambda 함수 상태:"
aws lambda get-function --function-name f1-two-backend-dev-main --query '{Name:Configuration.FunctionName,State:Configuration.State,Runtime:Configuration.Runtime}' --output table

# CloudWatch 로그 확인 (최근 10분)
echo "3. 최근 에러 로그:"
aws logs filter-log-events --log-group-name /aws/lambda/f1-two-backend-dev-main --start-time $(date -d '10 minutes ago' +%s)000 --filter-pattern ERROR

echo "✅ 상태 확인 완료"