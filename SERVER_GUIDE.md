# MCP 멀티 에이전트 서버 실행 가이드

## ✅ 준비 완료 사항

- [x] 프로젝트 구조 생성
- [x] 핵심 인프라 구현
- [x] 3개 우선순위 에이전트 구현
- [x] FastAPI MCP 서버 구현
- [x] CLI 도구 구현
- [x] Google Calendar/Sheets 연동 설정
- [x] 의존성 설치 (Python 3.11 환경)

## 🚀 서버 실행 방법

### 1. 가상환경 활성화 (필수!)

```bash
cd /home/june9713/workspace/NEXTNINE/multiagent_server
source /home/june9713/workspace/NEXTNINE/.venv/bin/activate
```

### 2. 환경 변수 확인

`.env` 파일에서 `GEMINI_API_KEY`가 설정되어 있는지 확인:

```bash
nano .env
# GEMINI_API_KEY=실제_API_키_입력
```

### 3. 서버 실행

```bash
python3 run_server.py
```

또는

```bash
python3 server/main.py
```

서버가 실행되면:
- URL: `http://localhost:8000`
- API 문서: `http://localhost:8000/docs`

## 🧪 CLI 테스트

새 터미널을 열어서:

```bash
cd /home/june9713/workspace/NEXTNINE/multiagent_server
source /home/june9713/workspace/NEXTNINE/.venv/bin/activate

# 에이전트 목록
python3 cli/agent_cli.py list

# Master Agent 호출
python3 cli/agent_cli.py ask master_agent "안녕하세요"

# Finance Agent 호출
python3 cli/agent_cli.py ask finance_agent "현재 예산 상태를 알려주세요"
```

## ⚠️ 주의사항

1. **반드시 가상환경 활성화**: Python 3.11 환경 필요
2. **GEMINI_API_KEY 설정**: 실제 API 키 입력 필요
3. **포트 충돌 시**: `pkill -f uvicorn` 으로 기존 서버 종료

## 📝 다음 단계

서버가 정상 실행되면:
1. 웹 브라우저에서 `http://localhost:8000/docs` 접속
2. API 문서 확인
3. CLI로 에이전트 테스트
4. 필요시 추가 에이전트 구현

---

**서버 실행은 사용자가 직접 진행합니다!** 🎉
