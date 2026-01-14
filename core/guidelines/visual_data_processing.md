# 비정형 데이터(이미지 및 이미지 기반 PDF) 처리 지침서

## 1. 개요
본 지침서는 텍스트 추출이 불가능한 스캔본 PDF나 이미지 파일을 Gemini Vision API를 사용하여 분석하고 정보를 추출하는 표준 절차를 정의합니다.

## 2. 처리 프로세스 (Standard Operating Procedure)

### Step 1: PDF의 이미지 변환
일반적인 PDF 파싱 라이브러리(`PyPDF2`, `pdfminer` 등)로 텍스트가 읽히지 않는 경우, `PyMuPDF (fitz)`를 사용하여 각 페이지를 고해상도 이미지(PNG)로 변환합니다.

```python
import fitz
doc = fitz.open('input.pdf')
for i, page in enumerate(doc):
    pix = page.get_pixmap(dpi=300) # 고해상도 설정
    pix.save(f'page_{i+1}.png')
```

### Step 2: Gemini API 업로드 및 상태 확인
`google-generativeai` 라이브러리를 통해 이미지를 업로드하고, 서버 측에서 처리가 완료될 때까지 대기(Polling)해야 합니다.

```python
import google.generativeai as genai
import time

img = genai.upload_file('page_1.png')
while img.state.name == 'PROCESSING':
    time.sleep(1)
    img = genai.get_file(img.name)
```

### Step 3: 멀티모달 프롬프팅
업로드된 파일들과 함께 구체적인 추출 대상을 명시한 프롬프트를 전달합니다.
- **모델**: `gemini-1.5-flash` 또는 `gemini-3-flash-preview` 권장.
- **프롬프트 전략**: 표 데이터는 JSON/Markdown 형식으로, 그림은 설명 형식으로 요청.

## 3. 주의 사항
- **용량 제한**: 한 번에 너무 많은 이미지를 전달하면 컨텍스트 제한에 걸릴 수 있으므로 중요 페이지(Table of Contents, Conclusion 등)를 우선 선정합니다.
- **보안**: 민감한 정보가 포함된 이미지는 분석 후 즉시 로컬/임시 저장소에서 삭제합니다.
- **인증**: `token.json`에 `drive` 또는 `cloud-platform` 권장 스코프가 포함되어야 안정적인 파일 관리가 가능합니다.

## 4. 실제 적용 사례 (2026-01-15)
- `로봇카페제안서 (1).pdf` 및 `SunnySmart 사업계획서`를 위 방식으로 분석하여 핵심 AI 전략과 예산 데이터를 성공적으로 추출함.
