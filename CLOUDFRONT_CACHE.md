# CloudFront 캐시 관리 가이드

CloudFront가 이전 JavaScript 파일을 캐시하는 문제를 해결하기 위한 스크립트들입니다.

## 📁 추가된 스크립트

### 1. `find-cloudfront-id.sh`
CloudFront Distribution ID를 자동으로 찾아주는 스크립트

```bash
./scripts/find-cloudfront-id.sh
```

### 2. `invalidate-cache.sh`
CloudFront 캐시를 즉시 무효화하는 스크립트

```bash
./scripts/invalidate-cache.sh
```

## 🚀 사용 방법

### 1단계: Distribution ID 찾기
```bash
cd D:\sedaily\Project\external_one
./scripts/find-cloudfront-id.sh
```

이 스크립트는:
- S3 버킷 이름을 기반으로 CloudFront Distribution을 찾습니다
- 찾은 Distribution ID를 `config.sh`에 자동으로 업데이트할 수 있습니다

### 2단계: 배포 시 자동 캐시 무효화
이제 배포 스크립트들이 자동으로 캐시를 무효화합니다:

```bash
# 메인 사이트 배포 (캐시 무효화 포함)
./scripts/deploy-frontend.sh

# 채팅 사이트 배포 (캐시 무효화 포함)
./scripts/deploy-chat-only.sh
```

### 3단계: 즉시 캐시 무효화
배포 없이 캐시만 무효화하려면:

```bash
./scripts/invalidate-cache.sh
```

## ⚙️ 설정

`scripts/config.sh` 파일에 다음 설정이 추가되었습니다:

```bash
# CloudFront Configuration
export CLOUDFRONT_DISTRIBUTION_ID=""          # 메인 사이트용
export CHAT_CLOUDFRONT_DISTRIBUTION_ID=""     # 채팅 전용 사이트용
```

## 🔧 수동 설정

Distribution ID를 수동으로 설정하려면:

1. AWS Console에서 CloudFront 서비스로 이동
2. Distribution 목록에서 해당 Distribution 선택
3. Distribution ID 복사
4. `scripts/config.sh` 파일에서 해당 변수에 ID 입력

## 📝 캐시 무효화 과정

1. **무효화 요청**: `/*` 경로로 모든 파일 무효화
2. **처리 시간**: 일반적으로 1-3분 소요
3. **확인**: 브라우저에서 강제 새로고침 (Ctrl+F5)

## 🚨 문제 해결

### Distribution ID를 찾을 수 없는 경우
```bash
# S3 버킷 확인
aws s3 ls

# CloudFront Distribution 목록 확인
aws cloudfront list-distributions --query 'DistributionList.Items[].{Id:Id,Domain:DomainName,Origin:Origins.Items[0].DomainName}'
```

### 캐시 무효화가 작동하지 않는 경우
1. AWS CLI 권한 확인
2. Distribution ID가 올바른지 확인
3. 브라우저 캐시도 강제 새로고침

## 💡 팁

- 배포 후 항상 브라우저 강제 새로고침 (Ctrl+F5 또는 Cmd+Shift+R)
- 캐시 무효화는 AWS 비용이 발생할 수 있습니다 (월 1000회까지 무료)
- 개발 중에는 브라우저 개발자 도구에서 "Disable cache" 옵션 사용 권장