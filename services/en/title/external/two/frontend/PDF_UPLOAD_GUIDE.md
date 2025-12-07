# PDF 업로드 기능 구현 가이드

## 📚 목차

1. [개요](#개요)
2. [필요한 패키지](#필요한-패키지)
3. [PDF Worker 파일 준비](#pdf-worker-파일-준비)
4. [컴포넌트 구현](#컴포넌트-구현)
5. [사용 예제](#사용-예제)
6. [트러블슈팅](#트러블슈팅)

---

## 개요

이 프로젝트는 **클라이언트 사이드**에서 PDF 텍스트를 추출하는 방식을 사용합니다.

- 서버로 파일을 업로드하지 않음 (보안성 향상)
- 브라우저에서 직접 PDF 파싱
- Mozilla의 `pdfjs-dist` 라이브러리 사용

---

## 필요한 패키지

### 1. PDF.js 설치 (이미 설치됨)

```bash
npm install pdfjs-dist@5.4.149
```

### 2. 아이콘 라이브러리 (이미 설치됨)

```bash
npm install @heroicons/react
```

### 현재 설치된 버전

- `pdfjs-dist`: 5.4.149
- `@heroicons/react`: 설치됨

---

## PDF Worker 파일 준비

### 1. Worker 파일 위치

PDF.js가 작동하려면 Worker 파일이 필요합니다.

**위치:**

```
/public/pdf.worker.min.js  (개발 환경)
/dist/pdf.worker.min.js    (프로덕션 환경)
```

### 2. Worker 파일 복사 방법

#### Option A: node_modules에서 복사

```bash
cp node_modules/pdfjs-dist/build/pdf.worker.min.js public/
```

#### Option B: CDN 사용 (권장하지 않음)

```javascript
pdfjsLib.GlobalWorkerOptions.workerSrc =
  "https://cdnjs.cloudflare.com/ajax/libs/pdf.js/5.4.149/pdf.worker.min.js";
```

### 3. 현재 상태 확인

```bash
# Worker 파일이 있는지 확인
ls -lah public/pdf.worker.min.js
ls -lah dist/pdf.worker.min.js

# 파일 크기 확인 (약 1MB)
# -rw-r--r-- 1.0M pdf.worker.min.js
```

**✅ 현재 프로젝트에는 이미 설치되어 있음**

---

## 컴포넌트 구현

### 1. FileUploadButton 컴포넌트

**파일 위치:**

```
src/features/chat/components/FileUploadButton.jsx
src/pages/ChatPage/FileUploadButton.jsx  (또 다른 위치)
```

### 2. 핵심 코드 구조

```javascript
import * as pdfjsLib from "pdfjs-dist";

// 1️⃣ PDF Worker 초기화
const initPdfWorker = () => {
  const workerUrl =
    window.location.hostname === "localhost"
      ? "/pdf.worker.min.js"
      : `${window.location.origin}/pdf.worker.min.js`;

  pdfjsLib.GlobalWorkerOptions.workerSrc = workerUrl;
  console.log("PDF.js Worker initialized:", workerUrl);
};

// 2️⃣ PDF 텍스트 추출 함수
const handlePdfFile = async (file) => {
  try {
    // ArrayBuffer로 변환
    const arrayBuffer = await file.arrayBuffer();

    // PDF 문서 로드
    const pdf = await pdfjsLib.getDocument({ data: arrayBuffer }).promise;

    let fullText = "";
    const numPages = pdf.numPages;

    // 각 페이지에서 텍스트 추출
    for (let pageNum = 1; pageNum <= numPages; pageNum++) {
      const page = await pdf.getPage(pageNum);
      const textContent = await page.getTextContent();
      const pageText = textContent.items.map((item) => item.str).join(" ");
      fullText += pageText + "\n\n";
    }

    // 텍스트가 비어있는지 확인 (스캔 PDF 감지)
    if (!fullText.trim()) {
      alert("텍스트 추출 실패: 스캔된 이미지 PDF일 수 있습니다.");
      return null;
    }

    return {
      text: fullText.trim(),
      pageCount: numPages,
    };
  } catch (error) {
    console.error("PDF 처리 오류:", error);
    alert("PDF 파일 처리 중 오류가 발생했습니다.");
    return null;
  }
};

// 3️⃣ 파일 처리 함수
const processFile = async (file) => {
  if (file.type === "application/pdf" || file.name.endsWith(".pdf")) {
    const result = await handlePdfFile(file);
    if (result) {
      // 추출된 텍스트 사용
      console.log("추출된 텍스트:", result.text);
      console.log("페이지 수:", result.pageCount);
    }
  }
};
```

### 3. 전체 컴포넌트 예제

```javascript
import React, { useRef, useState, useEffect } from "react";
import { PaperClipIcon } from "@heroicons/react/24/outline";
import * as pdfjsLib from "pdfjs-dist";

// PDF Worker 초기화
const initPdfWorker = () => {
  if (typeof window !== "undefined" && pdfjsLib) {
    const workerUrl =
      window.location.hostname === "localhost"
        ? "/pdf.worker.min.js"
        : `${window.location.origin}/pdf.worker.min.js`;
    pdfjsLib.GlobalWorkerOptions.workerSrc = workerUrl;
    console.log("PDF.js Worker initialized:", workerUrl);
  }
};

const FileUploadButton = ({ onFileContent, disabled }) => {
  const fileInputRef = useRef(null);
  const [isProcessing, setIsProcessing] = useState(false);

  // 컴포넌트 마운트 시 Worker 초기화
  useEffect(() => {
    initPdfWorker();
  }, []);

  // PDF 처리 함수
  const handlePdfFile = async (file) => {
    try {
      console.log("PDF 처리 시작:", file.name);

      const arrayBuffer = await file.arrayBuffer();
      const pdf = await pdfjsLib.getDocument({ data: arrayBuffer }).promise;

      let fullText = "";
      const numPages = pdf.numPages;

      for (let pageNum = 1; pageNum <= numPages; pageNum++) {
        const page = await pdf.getPage(pageNum);
        const textContent = await page.getTextContent();
        const pageText = textContent.items.map((item) => item.str).join(" ");
        fullText += pageText + "\n\n";
      }

      if (!fullText.trim()) {
        alert("텍스트를 추출할 수 없습니다. 스캔된 이미지 PDF일 수 있습니다.");
        return null;
      }

      return {
        text: fullText.trim(),
        pageCount: numPages,
      };
    } catch (error) {
      console.error("PDF 처리 오류:", error);
      alert("PDF 파일 처리 중 오류가 발생했습니다.");
      return null;
    }
  };

  // 파일 선택 핸들러
  const handleFileSelect = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setIsProcessing(true);

    try {
      if (file.type === "application/pdf" || file.name.endsWith(".pdf")) {
        const result = await handlePdfFile(file);
        if (result) {
          // 콜백으로 텍스트 전달
          onFileContent(result.text, {
            fileName: file.name,
            fileType: "pdf",
            fileSize: file.size,
            pageCount: result.pageCount,
          });
        }
      } else {
        alert("PDF 파일만 업로드 가능합니다.");
      }
    } catch (error) {
      console.error("파일 처리 오류:", error);
    } finally {
      setIsProcessing(false);
      event.target.value = ""; // 같은 파일 재선택 가능하도록
    }
  };

  return (
    <div>
      <input
        ref={fileInputRef}
        type="file"
        accept=".pdf"
        onChange={handleFileSelect}
        className="hidden"
        disabled={disabled || isProcessing}
      />

      <button
        onClick={() => fileInputRef.current?.click()}
        disabled={disabled || isProcessing}
        className="p-2 bg-blue-500 text-white rounded hover:bg-blue-600"
      >
        {isProcessing ? (
          <div className="animate-spin h-5 w-5 border-2 border-white border-t-transparent rounded-full" />
        ) : (
          <PaperClipIcon className="h-5 w-5" />
        )}
      </button>
    </div>
  );
};

export default FileUploadButton;
```

---

## 사용 예제

### 1. 기본 사용법

```javascript
import FileUploadButton from "./FileUploadButton";

function MyComponent() {
  const handleFileContent = (text, metadata) => {
    console.log("추출된 텍스트:", text);
    console.log("파일 이름:", metadata.fileName);
    console.log("페이지 수:", metadata.pageCount);

    // 텍스트를 채팅 입력창에 자동으로 넣기
    setInputText(text);
  };

  return (
    <FileUploadButton onFileContent={handleFileContent} disabled={false} />
  );
}
```

### 2. ChatInput과 통합

```javascript
const ChatInput = () => {
  const [inputText, setInputText] = useState("");

  const handleFileUpload = (text, metadata) => {
    // 파일 내용을 입력창에 추가
    setInputText((prev) => prev + `\n\n--- ${metadata.fileName} ---\n${text}`);
  };

  return (
    <div>
      <textarea
        value={inputText}
        onChange={(e) => setInputText(e.target.value)}
      />
      <FileUploadButton onFileContent={handleFileUpload} />
      <button onClick={() => sendMessage(inputText)}>전송</button>
    </div>
  );
};
```

---

## 트러블슈팅

### 문제 1: "Setting up fake worker failed"

**원인:** Worker 파일을 찾을 수 없음

**해결책:**

```bash
# Worker 파일이 있는지 확인
ls public/pdf.worker.min.js

# 없으면 복사
cp node_modules/pdfjs-dist/build/pdf.worker.min.js public/

# 빌드 후 dist 폴더에도 복사되는지 확인
npm run build
ls dist/pdf.worker.min.js
```

### 문제 2: "Unable to extract text from PDF"

**원인:** 스캔된 이미지 PDF (텍스트 레이어 없음)

**해결책:**

- OCR 라이브러리 사용 (예: Tesseract.js)
- 또는 사용자에게 안내: "복사 가능한 텍스트 PDF만 지원됩니다"

### 문제 3: CORS 에러

**원인:** CloudFront/S3에서 Worker 파일 로드 시 CORS 문제

**해결책:**

```javascript
// 동일 출처에서 로드하도록 수정
pdfjsLib.GlobalWorkerOptions.workerSrc = `${window.location.origin}/pdf.worker.min.js`;
```

### 문제 4: 큰 PDF 파일에서 브라우저 느려짐

**원인:** 메모리 부족

**해결책:**

```javascript
// 파일 크기 제한
if (file.size > 50 * 1024 * 1024) {
  // 50MB
  alert("파일 크기가 너무 큽니다. 50MB 이하의 파일만 업로드 가능합니다.");
  return;
}
```

### 문제 5: 프로덕션에서만 작동하지 않음

**원인:** Worker 파일이 배포되지 않음

**해결책:**

```bash
# vite.config.js 또는 빌드 스크립트 확인
# public 폴더의 파일이 dist로 복사되는지 확인

# 수동 복사
npm run build
cp public/pdf.worker.min.js dist/
```

---

## 체크리스트

구현 전 확인사항:

- [ ] `pdfjs-dist` 패키지 설치됨
- [ ] `public/pdf.worker.min.js` 파일 존재
- [ ] Worker 초기화 코드 추가됨
- [ ] PDF 처리 함수 구현됨
- [ ] 에러 핸들링 추가됨
- [ ] 로딩 상태 표시 추가됨
- [ ] 파일 크기 제한 설정됨
- [ ] 스캔 PDF 안내 메시지 추가됨
- [ ] 브라우저 콘솔에서 테스트 완료
- [ ] 프로덕션 배포 후 테스트 완료

---

## 참고 자료

- [PDF.js 공식 문서](https://mozilla.github.io/pdf.js/)
- [pdfjs-dist npm 패키지](https://www.npmjs.com/package/pdfjs-dist)
- [현재 프로젝트 구현](src/features/chat/components/FileUploadButton.jsx)

---

## 추가 기능 구현 아이디어

### 1. 드래그 앤 드롭

```javascript
const handleDrop = async (e) => {
  e.preventDefault();
  const files = Array.from(e.dataTransfer.files);
  const pdfFiles = files.filter((f) => f.type === "application/pdf");

  for (const file of pdfFiles) {
    await processFile(file);
  }
};
```

### 2. 다중 파일 업로드

```javascript
<input
  type="file"
  accept=".pdf"
  multiple // 다중 선택 활성화
  onChange={handleMultipleFiles}
/>
```

### 3. 진행률 표시

```javascript
for (let pageNum = 1; pageNum <= numPages; pageNum++) {
  const progress = Math.round((pageNum / numPages) * 100);
  setProgress(progress);
  // ...
}
```

### 4. PDF 미리보기

```javascript
const page = await pdf.getPage(1);
const viewport = page.getViewport({ scale: 1.5 });
const canvas = canvasRef.current;
const context = canvas.getContext("2d");
await page.render({ canvasContext: context, viewport }).promise;
```

---

**마지막 업데이트:** 2025-10-16
