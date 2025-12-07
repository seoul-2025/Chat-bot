# Lambda Layer Python 라이브러리 호환 문제 해결

## 🚨 문제 상황

Lambda Layer에서 `PyPDF2`, `Pillow`, `python-magic` 등이 작동하지 않는 이유:

1. **아키텍처 불일치**: 로컬(macOS/Windows)과 Lambda(Linux x86_64) 환경이 다름
2. **바이너리 의존성**: Pillow, python-magic은 시스템 라이브러리 필요
3. **경로 문제**: Layer 구조가 잘못되면 import 실패

---

## ✅ 해결 방법 1: 프론트엔드 처리 (권장)

**현재 프로젝트 방식 - Python 라이브러리 불필요**

```
PDF 파일 → 프론트엔드(PDF.js) → 텍스트 추출 → 백엔드(텍스트만)
```

### 장점
- Lambda Layer 문제 완전 회피
- 서버 비용 절감
- 더 빠른 처리
- 보안 향상 (파일을 서버에 업로드하지 않음)

### 구현 코드
이미 구현되어 있음:
- 파일: `frontend/src/features/chat/components/FileUploadButton.jsx`
- 가이드: `frontend/PDF_UPLOAD_GUIDE.md`

---

## ✅ 해결 방법 2: Lambda Layer 올바르게 생성

만약 꼭 백엔드에서 처리해야 한다면:

### Step 1: Docker로 Lambda 환경에서 빌드

```bash
# 1. Dockerfile 생성
cat > Dockerfile.lambda-layer << 'EOF'
FROM public.ecr.aws/lambda/python:3.11

# 작업 디렉토리 생성
WORKDIR /opt

# requirements.txt 복사
COPY requirements.txt .

# Lambda Layer 구조에 맞게 설치
RUN pip install -r requirements.txt -t /opt/python/

# 불필요한 파일 제거 (용량 절약)
RUN find /opt/python -type d -name "tests" -exec rm -rf {} +
RUN find /opt/python -type d -name "__pycache__" -exec rm -rf {} +
RUN rm -rf /opt/python/*.dist-info
EOF

# 2. requirements.txt 생성
cat > requirements-layer.txt << 'EOF'
PyPDF2==3.0.1
Pillow==10.0.0
python-magic-bin==0.4.14  # Windows/Mac용 바이너리 포함
EOF

# 3. Docker로 빌드
docker build -f Dockerfile.lambda-layer -t lambda-layer-builder .

# 4. 빌드된 파일 추출
docker run --rm -v $(pwd):/output lambda-layer-builder \
  bash -c "cd /opt && zip -r /output/lambda-layer.zip python/"

# 5. Layer 업로드
aws lambda publish-layer-version \
  --layer-name python-pdf-processing \
  --description "PyPDF2, Pillow for Lambda" \
  --zip-file fileb://lambda-layer.zip \
  --compatible-runtimes python3.11 \
  --compatible-architectures x86_64
```

### Step 2: Lambda Layer 구조 확인

Layer는 반드시 이 구조여야 함:

```
lambda-layer.zip
└── python/
    ├── PyPDF2/
    ├── PIL/
    ├── magic/
    └── ... (other packages)
```

**잘못된 구조 (작동 안됨):**
```
lambda-layer.zip
├── PyPDF2/
├── PIL/
└── magic/
```

### Step 3: Lambda 함수에 Layer 연결

```bash
aws lambda update-function-configuration \
  --function-name your-function-name \
  --layers arn:aws:lambda:region:account-id:layer:python-pdf-processing:1
```

---

## 🔧 특정 라이브러리별 해결책

### PyPDF2
```bash
# Docker 사용
docker run --rm -v $(pwd):/var/task public.ecr.aws/lambda/python:3.11 \
  pip install PyPDF2 -t /var/task/python/

# 또는 간단히
mkdir -p python
pip install PyPDF2 -t python/ --platform manylinux2014_x86_64 --only-binary=:all:
zip -r layer.zip python/
```

### Pillow (이미지 처리)
```bash
# Pillow는 바이너리 의존성이 있으므로 반드시 Docker 사용
docker run --rm -v $(pwd):/var/task public.ecr.aws/lambda/python:3.11 \
  pip install Pillow -t /var/task/python/
```

### python-magic
```bash
# python-magic-bin 사용 (바이너리 포함)
pip install python-magic-bin -t python/

# 또는 libmagic 시스템 라이브러리 포함
# (더 복잡함 - 권장하지 않음)
```

---

## 📋 Layer 생성 스크립트 (완전 자동화)

```bash
#!/bin/bash
# create-lambda-layer.sh

set -e

LAYER_NAME="python-pdf-layer"
PYTHON_VERSION="3.11"
REGION="us-east-1"

echo "🔨 Creating Lambda Layer for Python $PYTHON_VERSION..."

# 1. 임시 디렉토리 생성
rm -rf lambda-layer
mkdir -p lambda-layer/python

# 2. requirements.txt 생성
cat > lambda-layer/requirements.txt << 'EOF'
PyPDF2==3.0.1
Pillow==10.0.0
python-magic-bin==0.4.14
EOF

# 3. Docker로 Lambda 환경에서 설치
echo "📦 Installing packages in Lambda environment..."
docker run --rm \
  -v $(pwd)/lambda-layer:/var/task \
  public.ecr.aws/lambda/python:$PYTHON_VERSION \
  bash -c "pip install -r /var/task/requirements.txt -t /var/task/python/"

# 4. 불필요한 파일 제거
echo "🧹 Cleaning up unnecessary files..."
cd lambda-layer
find python -type d -name "tests" -exec rm -rf {} + 2>/dev/null || true
find python -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find python -type d -name "*.dist-info" -exec rm -rf {} + 2>/dev/null || true
rm -f requirements.txt

# 5. ZIP 파일 생성
echo "📦 Creating ZIP file..."
zip -r ../lambda-layer.zip python/ -q

# 6. AWS Lambda Layer 업로드
echo "☁️  Uploading to AWS Lambda..."
cd ..
LAYER_ARN=$(aws lambda publish-layer-version \
  --layer-name $LAYER_NAME \
  --description "PyPDF2, Pillow for Lambda Python $PYTHON_VERSION" \
  --zip-file fileb://lambda-layer.zip \
  --compatible-runtimes python$PYTHON_VERSION \
  --compatible-architectures x86_64 \
  --region $REGION \
  --query 'LayerVersionArn' \
  --output text)

echo "✅ Layer created successfully!"
echo "Layer ARN: $LAYER_ARN"

# 7. 정리
rm -rf lambda-layer lambda-layer.zip

echo "
🎉 Done! Add this Layer to your Lambda function:

aws lambda update-function-configuration \\
  --function-name YOUR_FUNCTION_NAME \\
  --layers $LAYER_ARN \\
  --region $REGION
"
```

**사용 방법:**
```bash
chmod +x create-lambda-layer.sh
./create-lambda-layer.sh
```

---

## 🐛 트러블슈팅

### 문제 1: "No module named 'PyPDF2'"

**원인:** Layer 구조가 잘못됨

**확인:**
```bash
unzip -l lambda-layer.zip | head -20

# 올바른 출력:
# python/PyPDF2/__init__.py
# python/PIL/__init__.py
```

**해결:**
```bash
# 올바른 구조로 다시 생성
mkdir -p python
pip install PyPDF2 -t python/
zip -r layer.zip python/
```

### 문제 2: "ImportError: libmagic.so.1"

**원인:** python-magic이 시스템 라이브러리 필요

**해결:**
```bash
# Option A: python-magic-bin 사용 (권장)
pip install python-magic-bin -t python/

# Option B: 프론트엔드에서 처리 (더 권장)
# - MIME type은 브라우저가 자동으로 감지
```

### 문제 3: "OSError: cannot load library"

**원인:** macOS/Windows에서 빌드한 바이너리를 Lambda(Linux)에서 실행

**해결:**
```bash
# 반드시 Docker 사용하여 Linux 환경에서 빌드
docker run --rm -v $(pwd):/var/task \
  public.ecr.aws/lambda/python:3.11 \
  pip install Pillow -t /var/task/python/
```

### 문제 4: Layer 용량 초과 (250MB)

**원인:** 불필요한 파일 포함

**해결:**
```bash
# 테스트 파일, 문서 제거
find python -type d -name "tests" -exec rm -rf {} +
find python -type d -name "docs" -exec rm -rf {} +
find python -type d -name "__pycache__" -exec rm -rf {} +
find python -name "*.pyc" -delete
find python -name "*.pyo" -delete

# 개발 의존성 제외
pip install --no-deps PyPDF2 -t python/
```

---

## 📊 비교: 프론트엔드 vs 백엔드 처리

| 항목 | 프론트엔드 (권장) | 백엔드 (Lambda) |
|------|------------------|----------------|
| **구현 난이도** | ⭐⭐ (쉬움) | ⭐⭐⭐⭐ (어려움) |
| **Layer 문제** | ❌ 없음 | ✅ 있음 |
| **서버 비용** | 💰 무료 | 💰💰 추가 비용 |
| **처리 속도** | ⚡ 빠름 | 🐢 느림 (업로드 시간) |
| **파일 크기 제한** | 브라우저 메모리 | Lambda 500MB |
| **보안** | ✅ 파일이 서버에 안감 | ⚠️ 파일 업로드 필요 |
| **유지보수** | ✅ 간단 | ⚠️ 복잡 |

---

## 🎯 추천 방식

### 현재 프로젝트 방식 (프론트엔드)
```javascript
// ✅ 간단하고 효율적
import * as pdfjsLib from 'pdfjs-dist';

const text = await extractTextFromPDF(file);
await sendToBackend(text);
```

### Lambda Layer 필요한 경우
```bash
# ✅ Docker로 올바르게 빌드
./create-lambda-layer.sh
```

---

## 📚 참고 자료

- [AWS Lambda Layers 공식 문서](https://docs.aws.amazon.com/lambda/latest/dg/configuration-layers.html)
- [Lambda Python 런타임](https://docs.aws.amazon.com/lambda/latest/dg/lambda-python.html)
- [PDF.js 프론트엔드 처리](../frontend/PDF_UPLOAD_GUIDE.md)
- [Docker Lambda Python 이미지](https://gallery.ecr.aws/lambda/python)

---

## ✅ 체크리스트

Lambda Layer 생성 전:

- [ ] Docker 설치됨
- [ ] AWS CLI 설정됨
- [ ] requirements.txt 준비됨
- [ ] Lambda 함수 Python 버전 확인 (3.11? 3.10? 3.9?)
- [ ] Lambda 함수 아키텍처 확인 (x86_64? arm64?)

Layer 생성 후:

- [ ] ZIP 파일 구조 확인 (`python/` 디렉토리 있음)
- [ ] Layer ARN 저장
- [ ] Lambda 함수에 Layer 연결
- [ ] 테스트 코드로 import 확인

---

**마지막 업데이트:** 2025-10-16

**권장 사항:** 가능하면 프론트엔드에서 PDF 처리 (현재 프로젝트 방식)
