#!/bin/bash

# 다국어 프롬프트 테스트 스크립트
# WebSocket API를 wscat으로 테스트

WEBSOCKET_URL="wss://yxn6bf9go4.execute-api.us-east-1.amazonaws.com/prod"

echo "================================"
echo "다국어 기사 편집 테스트"
echo "================================"
echo ""
echo "사용법: wscat을 설치해야 합니다"
echo "npm install -g wscat"
echo ""
echo "테스트 명령어:"
echo ""

# 체코어 테스트
echo "# 1. 체코어 기사 테스트"
echo "wscat -c $WEBSOCKET_URL"
cat << 'EOF'
{
  "action": "sendMessage",
  "message": "Prezident Trump a jeho ruský protějšek Vladimir Putin se sejdou v Budapešti, aby se pokusili ukončit válku na Ukrajině, uvedl na sociální síti Truth Social americký prezident po svém telefonátu s Putinem.",
  "engineType": "11",
  "userId": "test@example.com",
  "conversationId": "test-czech-001"
}
EOF
echo ""
echo ""

# 폴란드어 테스트
echo "# 2. 폴란드어 기사 테스트"
echo "wscat -c $WEBSOCKET_URL"
cat << 'EOF'
{
  "action": "sendMessage",
  "message": "Premier Tusk ogłosił dziś nowe reformy edukacyjne, które mają na celu poprawę jakości nauczania w polskich szkołach.",
  "engineType": "11",
  "userId": "test@example.com",
  "conversationId": "test-polish-001"
}
EOF
echo ""
echo ""

# 러시아어 테스트
echo "# 3. 러시아어 기사 테스트"
echo "wscat -c $WEBSOCKET_URL"
cat << 'EOF'
{
  "action": "sendMessage",
  "message": "Президент Путин заявил сегодня о новых экономических инициативах, направленных на развитие регионов.",
  "engineType": "11",
  "userId": "test@example.com",
  "conversationId": "test-russian-001"
}
EOF
echo ""
echo ""

# 한국어 테스트
echo "# 4. 한국어 기사 테스트"
echo "wscat -c $WEBSOCKET_URL"
cat << 'EOF'
{
  "action": "sendMessage",
  "message": "문재인 대통령이 오늘 청와대에서 기자회견을 열고 새로운 경제정책을 발표했다.",
  "engineType": "11",
  "userId": "test@example.com",
  "conversationId": "test-korean-001"
}
EOF
echo ""
echo ""

# 영어 테스트
echo "# 5. 영어 기사 테스트"
echo "wscat -c $WEBSOCKET_URL"
cat << 'EOF'
{
  "action": "sendMessage",
  "message": "President Biden announced today a new infrastructure plan aimed at revitalizing American cities.",
  "engineType": "11",
  "userId": "test@example.com",
  "conversationId": "test-english-001"
}
EOF
echo ""
echo ""

echo "================================"
echo "기대 결과:"
echo "================================"
echo "✅ 체코어 입력 → 체코어 응답 (100%)"
echo "✅ 폴란드어 입력 → 폴란드어 응답 (100%)"
echo "✅ 러시아어 입력 → 러시아어 응답 (100%)"
echo "✅ 한국어 입력 → 한국어 응답 (100%)"
echo "✅ 영어 입력 → 영어 응답 (100%)"
echo ""
echo "❌ 체코어 입력 → 한국어 응답 (실패)"
echo "❌ 폴란드어 입력 → 영어 응답 (실패)"
