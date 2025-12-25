@echo off
echo ========================================
echo   f1.sedaily.ai 로컬 테스트 서버
echo ========================================
echo.

REM 가상환경 확인
if not exist "venv" (
    echo 가상환경을 생성합니다...
    python -m venv venv
)

REM 가상환경 활성화
call venv\Scripts\activate.bat

REM 의존성 설치
echo 의존성을 설치합니다...
pip install -r local_requirements.txt

REM 환경변수 설정 (선택사항)
set ANTHROPIC_API_KEY=your-api-key-here
set AWS_REGION=us-east-1
set ENABLE_WEB_SEARCH=false
set ENABLE_NATIVE_WEB_SEARCH=false

echo.
echo 서버를 시작합니다...
echo URL: http://localhost:5000
echo WebSocket: ws://localhost:5000
echo.
echo Ctrl+C로 종료할 수 있습니다.
echo.

REM 서버 실행
python local_server.py

pause