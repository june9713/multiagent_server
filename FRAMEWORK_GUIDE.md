# MCP Multi-Agent System Framework Guide

본 프레임워크는 여러 독립적인 에이전트들이 협력하여 복잡한 과업을 수행할 수 있도록 설계된 확장 가능한 멀티 에이전트 시스템입니다.

## 🚀 빠른 시작 (Quick Start)

1. **환경 설정**:
   - `venv` 가상환경 생성 및 활성화: `python -m venv .venv && source .venv/bin/activate`
   - 의존성 설치: `pip install -r requirements.txt`
   - 환경 변수 설정: `.env.template`을 `.env`로 복사하고 `GEMINI_API_KEY`와 `PROJECT_NAME`을 입력합니다.

2. **에이전트 구성**:
   - `agentconfig.json.template`을 `agentconfig.json`으로 복사합니다.
   - 필요한 에이전트 정의를 추가하거나 수정합니다.

3. **서버 실행**:
   - `python run_server.py`

## 🏗️ 에이전트 생성 방법

모든 에이전트는 `core.base_agent.BaseAgent` 클래스를 상속받아야 합니다.

### 1. 에이전트 디렉토리 생성
`agents/my_new_agent/` 폴더를 만들고 `agent.py` 파일을 생성합니다.

### 2. 에이전트 클래스 구현
```python
from core.base_agent import BaseAgent
from typing import List, Dict

class MyNewAgent(BaseAgent):
    def get_tool_definitions(self) -> List[Dict]:
        return [
            {
                "name": "my_custom_tool",
                "description": "설명...",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "param1": {"type": "string"}
                    }
                }
            }
        ]

    async def execute_tool(self, tool_name: str, parameters: Dict) -> str:
        if tool_name == "my_custom_tool":
            return f"안녕, {parameters.get('param1')}!"
        return "Unknown tool"
```

### 3. `agentconfig.json` 등록
```json
{
  "id": "my_new_agent",
  "name": "나의 신규 에이전트",
  "module": "agents.my_new_agent.agent",
  "class": "MyNewAgent",
  "tools": ["my_custom_tool"]
}
```

## 🛠️ 기본 탑재 도구 (Core Capabilities - Git 유지)
모든 에이전트는 별도의 구현 없이도 다음의 강력한 공통 도구들을 즉시 사용할 수 있으며, 이 기능들은 프레임워크 코어(`core/base_agent.py`)에 포함되어 Git으로 영구 유지됩니다:

- **파일 시스템 접근 (`read_local_file`, `write_local_file`, `list_files`)**:
  - 에이전트별 독립된 작업 디렉토리(`/data/work_docs/{agent_id}`)에 안전하게 데이터를 기록하고 관리합니다.
  - `data/`로 시작하는 경로를 통해 공용 리소스 공유가 가능합니다.
- **인터넷 정보 추출 (`fetch_web_content`)**:
  - `httpx`를 통해 실제 웹 페이지의 콘텐츠를 가져옵니다. 단순 IP 확인을 넘어 실제 URL의 HTML/Text 데이터를 분석할 수 있습니다.
- **상태 관리 (`update_agent_status`)**:
  - 에이전트의 현재 작업 상황을 `current_status.md`에 실시간으로 기록하여 투명성을 확보합니다.

## 👑 마스터 에이전트의 지휘 체계 (MCP Commander Protocol)
본 프레임워크는 단순히 에이전트들을 나열하는 것이 아니라, 마스터 에이전트를 중심으로 한 명확한 지휘 체계를 가지고 있습니다. 

이는 **[MCP 지휘관 규약](core/guidelines/master_commander_protocol.md)**에 상세히 명시되어 있으며, 마스터 에이전트의 6대 업무 수칙을 기반으로 시스템이 운영됩니다:
1. **업무 정립**: 서브 에이전트의 역할을 정의함.
2. **자료 배포/수집**: 필요한 데이터를 전달하고 결과를 취합함.
3. **재지원**: 부족한 자료를 즉각 보충함.
4. **가교**: 에이전트 간 데이터 전달 통로가 됨.
5. **총지휘**: 전체 프로젝트의 오케스트레이션 수행.
6. **유저 리포트**: 런타임 상황을 유저에게 이메일로 통보함.

## ➕ 런타임 에이전트 동적 추가
서버 중단 없이 새로운 기능을 가진 에이전트를 즉시 추가할 수 있습니다:
- **방법**: 마스터 에이전트에게 `register_subagent` 도구 호출을 지시하거나, `/api/v1/admin/register_agent` API를 호출합니다.
- **결과**: `agentconfig.json`에 자동으로 기록되며, 시스템 재시작 없이 즉시 해당 에이전트를 호출하여 사용할 수 있습니다.

## 📂 프로젝트 구조
- `core/`: 시스템 핵심 로직 (에이전트 로더, 컨텍스트 매니저 등)
- `agents/`: 프로젝트별 커스텀 에이전트가 위치하는 곳
- `data/`: 테스트 결과, 로그, 작업 문서가 저장되는 곳 (Git 무시됨)
- `examples/`: 참고할 수 있는 기존 프로젝트(예: NEXTNINE)의 에이전트 구성 예시
