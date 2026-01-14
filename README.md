# MCP Multi-Agent Server

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

재사용 가능한 MCP(Model Context Protocol) 기반 멀티 에이전트 시스템입니다.

## 🌟 주요 기능

- **자동 에이전트 검색**: `agentconfig.json`을 통한 동적 에이전트 로딩
- **작업 연속성**: 각 에이전트의 상세한 작업 문서 관리 (`work_docs/`)
- **컨텍스트 전파**: Master Agent가 서브 에이전트에게 충분한 컨텍스트 제공
- **히스토리 관리**: SQLite 기반 대화 히스토리 영구 저장
- **FastAPI 서버**: RESTful API를 통한 에이전트 호출
- **Rich CLI**: 사용자 친화적인 명령줄 인터페이스

## 📦 설치

```bash
# 1. 저장소 클론
git clone git@github.com:june9713/multiagent_server.git
cd multiagent_server

# 2. 가상환경 생성 (선택사항)
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate  # Windows

# 3. 의존성 설치
pip install -r requirements.txt

# 4. 환경 변수 설정
cp config/.env.example .env
# .env 파일을 열어 GEMINI_API_KEY 설정
```

## 🚀 빠른 시작

### 1. MCP 서버 실행

```bash
python server/main.py
```

서버가 `http://localhost:8000`에서 실행됩니다.
API 문서는 `http://localhost:8000/docs`에서 확인할 수 있습니다.

### 2. CLI로 에이전트 사용

```bash
# 사용 가능한 에이전트 목록
python cli/agent_cli.py list

# 에이전트에게 질문
python cli/agent_cli.py ask master_agent "프로젝트 현황을 알려주세요"

# Finance Agent에게 예산 확인
python cli/agent_cli.py ask finance_agent "현재 예산 사용률을 알려주세요"

# 에이전트 상태 확인
python cli/agent_cli.py status finance_agent

# 세션 목록
python cli/agent_cli.py sessions

# 대화 히스토리
python cli/agent_cli.py history <session_id>
```

## 🏗️ 프로젝트 구조

```
multiagent_server/
├── core/                    # 핵심 인프라
│   ├── base_agent.py       # 베이스 에이전트 클래스
│   ├── agent_loader.py     # 에이전트 동적 로딩
│   ├── history_manager.py  # 대화 히스토리 관리
│   └── context_manager.py  # 컨텍스트 전파 관리
├── server/                  # FastAPI MCP 서버
│   └── main.py
├── agents/                  # 에이전트 구현
│   ├── master_agent/
│   ├── finance_agent/
│   └── schedule_agent/
├── cli/                     # CLI 도구
│   └── agent_cli.py
├── data/                    # 런타임 데이터 (gitignore)
│   ├── history.db          # 대화 히스토리
│   ├── logs/               # 일일 로그
│   └── work_docs/          # 에이전트 작업 문서
├── config/                  # 설정
│   └── .env.example
├── agentconfig.json        # 에이전트 설정
└── requirements.txt
```

## 🤖 에이전트

### Master Agent
- **역할**: 프로젝트 총괄 및 에이전트 조율
- **도구**: 작업 위임, 리포트 생성, 의사결정 승인, 컨텍스트 패키지 생성

### Finance Agent
- **역할**: 예산 관리 및 재무 분석
- **도구**: 예산 확인, 지출 기록, 재무 리포트, ROI 계산

### Schedule Agent
- **역할**: 일정 관리 및 마감일 추적
- **도구**: 일정 추가, 일정 확인, 리마인더, 충돌 해결

## 🔧 API 엔드포인트

- `GET /` - 서버 상태
- `GET /api/v1/agents` - 에이전트 목록
- `POST /api/v1/agent/invoke` - 에이전트 호출
- `GET /api/v1/agent/{agent_id}/status` - 에이전트 상태
- `GET /api/v1/sessions` - 세션 목록
- `GET /api/v1/session/{session_id}/history` - 대화 히스토리

## 📝 작업 문서 시스템

각 에이전트는 `data/work_docs/{agent_id}/`에 다음 파일들을 관리합니다:

- **current_status.md**: 현재 작업 상태, 대기 중인 작업, 차단 이슈
- **work_log.json**: 모든 작업 세션 이력, 컨텍스트, 의사결정
- **도메인별 문서**: 에이전트별 특화 문서 (예: budget_tracking.md)

## 🔄 Git 서브모듈로 사용

다른 프로젝트에서 서브모듈로 추가:

```bash
cd your-project
git submodule add git@github.com:june9713/multiagent_server.git mcp
git submodule update --init --recursive

# 환경 변수 설정
cp mcp/config/.env.example .env

# 서버 실행
cd mcp
python server/main.py
```

## 📄 라이선스

MIT License

## 🤝 기여

이슈와 PR을 환영합니다!

---

**Made with ❤️ by NEXTNINE Team**
