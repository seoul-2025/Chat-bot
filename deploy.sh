#!/bin/bash

echo "🚀 배포 시작..."

# 1. 프론트엔드 빌드
echo "📦 프론트엔드 빌드 중..."
npm run build

# 2. 빌드 파일 확인
if [ ! -d "dist" ]; then
  echo "❌ 빌드 실패: dist 폴더가 없습니다."
  exit 1
fi

# 3. 서버 파일 준비
echo "🔧 서버 파일 준비 중..."
cp server.js dist/
cp package.json dist/
cp .env.production dist/.env

# 4. 배포 완료
echo "✅ 배포 준비 완료!"
echo "📁 배포 파일: dist/ 폴더"
echo "🌐 서버 실행: cd dist && npm install --production && node server.js"