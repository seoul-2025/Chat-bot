# 🚀 b1.sedaily.ai 올바른 배포 가이드

## ✅ 사용할 스크립트

### 📦 프론트엔드 배포
```bash
./deploy-p2-frontend.sh
```
- **S3 버킷**: `p2-two-frontend`
- **CloudFront**: `E2WPOE6AL2G5DZ` 
- **도메인**: https://b1.sedaily.ai

### 🔧 백엔드 Lambda 함수 배포
```bash
./scripts-v2/05-deploy-lambda-code-improved.sh
```
- **Lambda 함수들**: `p2-two-*-two` (6개)

## ⚠️ 사용하지 말 것

### ❌ deprecated-scripts/ 폴더
- 모든 스크립트들이 잘못된 설정 포함
- 절대 실행하지 말 것!

### ❌ 기타 잘못된 스크립트들
```bash
# 이런 스크립트들 사용 금지:
./deploy.sh                    # 설정 불명확
./deploy-service.sh           # 설정 불명확  
./deploy-buddy-v1.sh          # 다른 프로젝트용
```

## 🎯 올바른 배포 순서

1. **백엔드 먼저 배포**
   ```bash
   ./scripts-v2/05-deploy-lambda-code-improved.sh
   ```

2. **프론트엔드 배포** 
   ```bash
   ./deploy-p2-frontend.sh
   ```

3. **확인**
   - https://b1.sedaily.ai 접속 테스트
   - AI 대화 기능 테스트

---
작성일: 2025-12-13