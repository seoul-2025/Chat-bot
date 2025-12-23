# Node.js 18 베이스 이미지
FROM node:18-alpine

# 작업 디렉토리 설정
WORKDIR /app

# 패키지 파일 복사
COPY package*.json ./

# 의존성 설치
RUN npm install --production

# 애플리케이션 파일 복사
COPY . .

# 프론트엔드 빌드
RUN npm run build

# 포트 노출
EXPOSE 3001

# 서버 실행
CMD ["node", "server.js"]