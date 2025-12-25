@echo off
echo ========================================
echo   f1.sedaily.ai 백엔드 배포 (AWS CLI)
echo ========================================
echo.

set FUNCTION_NAME=f1-two-backend-dev-main
set REGION=us-east-1
set ROLE_ARN=arn:aws:iam::887078546492:role/lambda-execution-role

echo 배포 패키지 생성 중...
cd backend
powershell -Command "Compress-Archive -Path * -DestinationPath deployment.zip -Force"

echo Lambda 함수 생성/업데이트 중...
aws lambda get-function --function-name %FUNCTION_NAME% --region %REGION% >nul 2>&1
if %errorlevel% equ 0 (
    echo 기존 함수 업데이트...
    aws lambda update-function-code --function-name %FUNCTION_NAME% --zip-file fileb://deployment.zip --region %REGION%
) else (
    echo 새 함수 생성...
    aws lambda create-function --function-name %FUNCTION_NAME% --runtime python3.11 --role %ROLE_ARN% --handler handlers.websocket.message.handler --zip-file fileb://deployment.zip --timeout 300 --memory-size 1024 --region %REGION%
)

echo API Gateway 생성 중...
for /f "tokens=*" %%i in ('aws apigateway get-rest-apis --query "items[?name==''f1-two-api''].id" --output text --region %REGION%') do set API_ID=%%i

if "%API_ID%"=="None" (
    echo 새 API Gateway 생성...
    for /f "tokens=*" %%i in ('aws apigateway create-rest-api --name f1-two-api --region %REGION% --query id --output text') do set API_ID=%%i
)

echo API Gateway ID: %API_ID%

echo 배포 완료!
echo API Gateway URL: https://%API_ID%.execute-api.%REGION%.amazonaws.com/prod

pause