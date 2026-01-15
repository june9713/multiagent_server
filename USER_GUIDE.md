# 사용자 운영 가이드 (User Operations Guide)

본 문서는 `multiagent_server`의 핵심 기능을 실제로 활용하는 방법을 설명합니다. 현재 시스템은 단순한 Mock 상태를 벗어나 실제 구글 서비스(Gmail, Sheets, Calendar) 및 로컬 데이터 관리와 연동되어 있습니다.

## 1. 전제 조건
-   프로젝트 루트(`multiagent_server/`)에 `token.json` 파일이 있어야 합니다.
-   `.env` 파일에 `GEMINI_API_KEY`가 올바르게 설정되어 있어야 합니다.

## 2. 핵심 에이전트 및 도구 사용법

### 👑 Master Agent (총괄 및 조정)
-   **`notify_user_email`**: 사용자에게 실제로 Gmail을 발송합니다.
    -   *매개변수*: `subject` (제목), `body` (본문), `is_emergency` (긴급 여부)
-   **`generate_report`**: 에이전트들의 작업 로그(`data/work_docs/*/work_log.json`)를 취합하여 마크다운 리포트를 생성합니다.
    -   *저장소*: `data/reports/report_*.md`
-   **`approve_decision`**: 주요 의사결정 사항을 기록합니다.
    -   *저장소*: `data/logs/decisions.json`

### 📒 Finance Agent (재무 관리)
-   **`record_expense`**: 구글 스프레드시트에 지출 내역을 기록합니다.
    -   *매개변수*: `amount`, `category`, `description`
-   **`check_budget`**: 스프레드시트에서 예산 데이터를 읽어옵니다.

### 🗓️ Schedule Agent (일정 관리)
-   **`add_event`**: 구글 캘린더에 일정을 추가합니다.
    -   *매개변수*: `title`, `date` (YYYY-MM-DD), `time` (HH:MM)
-   **`check_schedule`**: 특정 날짜의 일정을 조회합니다.

### 📄 Executive Secretary Agent (행정 지원)
-   **`create_google_spreadsheet` / `create_google_document`**: 새 구글 시트나 문서를 생성하고 `data/project_resources.json`에 자동으로 등록합니다.

## 3. 실행 방법 (CLI)

에이전트 명령은 `cli/agent_cli.py`를 통해 내릴 수 있습니다.

```bash
# 리포트 생성 요청
python cli/agent_cli.py invoke master_agent "주간 업무 리포트를 생성해줘."

# 일정 추가 요청
python cli/agent_cli.py invoke schedule_agent "내일 오후 3시에 팀 미팅 일정 추가해줘."
```

## 4. 데이터 저장 구조
-   `data/work_docs/`: 에이전트별 개별 작업 로그 및 문서
-   `data/logs/`: 시스템 로그 및 의사결정 기록
-   `data/reports/`: 생성된 통합 리포트
-   `data/project_resources.json`: 생성된 구글 파일 ID 관리 리스트
