# ⚠️ 사용하지 말 것 - 잘못된 스크립트들

이 폴더의 스크립트들은 **잘못된 설정**으로 인해 사용하면 안됩니다.

## ❌ incorrect-lambda-names/
- **문제**: 잘못된 Lambda 함수명 사용 (`buddy-*` 대신 `p2-two-*` 사용해야 함)
- **파일**: deploy-buddy-v1.sh
- **이동일**: 2024-12-14

## ❌ wrong-deploy-scripts/ (구 deploy/ 폴더)
- **문제**: 잘못된 CloudFront ID (`E3R1GGMJXE66MJ`) 사용
- **문제**: 잘못된 S3 버킷 (`b1.sedaily.ai`) 사용  
- **실제**: b1.sedaily.ai는 CloudFront `E2WPOE6AL2G5DZ`와 S3 `p2-two-frontend` 사용

## ✅ 올바른 b1.sedaily.ai 배포 스크립트
```bash
# 백엔드 Lambda 함수들 배포 (권장)
./update-buddy-code.sh

# 프론트엔드만 배포
./deploy-p2-frontend.sh

# 또는 scripts-v2 사용
./scripts-v2/05-deploy-lambda-code-improved.sh
```

## ⚠️ 주의사항
deprecated-scripts 폴더의 어떤 스크립트도 실행하지 마세요!

---
정리일: 2024-12-14