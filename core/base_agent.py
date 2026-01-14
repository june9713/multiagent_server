"""
Base Agent Class - Foundation for all MCP agents
"""

from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import json
import asyncio
import warnings
import google.generativeai as genai

# Suppress FutureWarning for google.generativeai
warnings.filterwarnings('ignore', category=FutureWarning, module='google.generativeai')


class BaseAgent(ABC):
    """Base class for all MCP agents"""
    
    def __init__(
        self,
        agent_id: str,
        agent_name: str,
        role: str,
        tone: str,
        keywords: List[str],
        gemini_api_key: str,
        work_docs_dir: Path,
        job_category: Optional[str] = None,
        scope: Optional[Dict] = None,
        tools: Optional[List[str]] = None,
        integrations: Optional[List[Dict]] = None
    ):
        self.agent_id = agent_id
        self.agent_name = agent_name
        self.role = role
        self.tone = tone
        self.keywords = keywords
        self.job_category = job_category or "common"
        self.scope = scope or {}
        self.tools = tools or []
        self.integrations = integrations or []
        
        # Work documentation
        self.work_docs_dir = work_docs_dir / agent_id
        self.work_docs_dir.mkdir(parents=True, exist_ok=True)
        
        # Gemini setup (legacy API for 0.1.0rc1)
        genai.configure(api_key=gemini_api_key)
        # Note: Using legacy API - GenerativeModel not available in 0.1.0rc1
        self.gemini_api_key = gemini_api_key
        
        # System prompt
        self.system_prompt = self._build_system_prompt()
        
        # Conversation history
        self.conversation_history = []
    
    def _build_system_prompt(self) -> str:
        """Build agent persona-based system prompt"""
        responsibilities = "\n".join([f"- {r}" for r in self.scope.get('responsibilities', [])])
        
        return f"""당신은 MCP 멀티 에이전트 시스템의 {self.agent_name}입니다.

**역할**: {self.role}
**말투**: {self.tone}
**핵심 키워드**: {', '.join(self.keywords)}

**담당 업무**:
{responsibilities}

**중요 지침**:
1. 모든 작업은 상세하게 문서화하여 다음 작업 시 컨텍스트를 완벽히 복원할 수 있도록 합니다.
2. 작업 시작 전 current_status.md를 읽고, 작업 후 업데이트합니다.
3. 모든 작업 세션은 work_log.json에 기록합니다.
4. Master Agent로부터 받은 컨텍스트를 정확히 이해하고 따릅니다.
5. 다른 에이전트에게 작업을 위임할 때는 충분한 컨텍스트를 제공합니다.
"""
    
    @abstractmethod
    def get_tool_definitions(self) -> List[Dict]:
        """Return agent-specific tool definitions"""
        pass
    
    def load_current_status(self) -> Dict:
        """Load current work status from current_status.md"""
        status_file = self.work_docs_dir / "current_status.md"
        
        if not status_file.exists():
            return {
                "in_progress": [],
                "waiting": [],
                "blocking_issues": [],
                "next_steps": []
            }
        
        # Simple parsing - in production, use proper markdown parser
        content = status_file.read_text(encoding='utf-8')
        return {"raw_content": content}
    
    def update_current_status(
        self,
        in_progress: List[str],
        waiting: List[str],
        blocking_issues: List[str],
        next_steps: List[str]
    ) -> None:
        """Update current_status.md"""
        status_file = self.work_docs_dir / "current_status.md"
        
        content = f"""# {self.agent_name} 현재 상태

**마지막 업데이트**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 진행 중인 작업
{chr(10).join([f'- [ ] {task}' for task in in_progress])}

## 대기 중인 작업
{chr(10).join([f'{i+1}. {task}' for i, task in enumerate(waiting)])}

## 차단 이슈
{chr(10).join([f'- {issue}' for issue in blocking_issues])}

## 다음 단계
{chr(10).join([f'{i+1}. {step}' for i, step in enumerate(next_steps)])}
"""
        
        status_file.write_text(content, encoding='utf-8')
    
    def log_work_session(
        self,
        session_id: str,
        tasks_completed: List[str],
        context_received: Optional[Dict] = None,
        delegated_to: Optional[List[Dict]] = None,
        decisions_made: Optional[List[str]] = None,
        files_modified: Optional[List[str]] = None
    ) -> None:
        """Log work session to work_log.json"""
        log_file = self.work_docs_dir / "work_log.json"
        
        # Load existing log
        if log_file.exists():
            log_data = json.loads(log_file.read_text(encoding='utf-8'))
        else:
            log_data = {
                "agent_id": self.agent_id,
                "last_updated": datetime.now().isoformat(),
                "work_sessions": []
            }
        
        # Add new session
        session = {
            "session_id": session_id,
            "started_at": datetime.now().isoformat(),
            "tasks_completed": tasks_completed,
        }
        
        if context_received:
            session["context_received"] = context_received
        if delegated_to:
            session["delegated_to"] = delegated_to
        if decisions_made:
            session["decisions_made"] = decisions_made
        if files_modified:
            session["files_modified"] = files_modified
        
        log_data["work_sessions"].append(session)
        log_data["last_updated"] = datetime.now().isoformat()
        
        # Save log
        log_file.write_text(json.dumps(log_data, ensure_ascii=False, indent=2), encoding='utf-8')
    
    def _proto_to_python_value(self, value: Any) -> Any:
        """Recursively convert proto values to standard Python types"""
        # Handle dict-like objects (Struct/Map)
        if hasattr(value, "items"):
            return {k: self._proto_to_python_value(v) for k, v in value.items()}
        # Handle list-like objects (Repeated)
        elif isinstance(value, (list, tuple)):
            return [self._proto_to_python_value(v) for v in value]
        # Handle RepeatedComposite/RepeatedScalar which are iterable but not list
        elif hasattr(value, "__iter__") and not isinstance(value, (str, bytes)):
            return [self._proto_to_python_value(v) for v in value]
        # Base case: primitive types
        return value

    def _load_project_resources(self) -> str:
        """Load project resources from data/project_resources.json"""
        resource_file = Path("data/project_resources.json")
        if not resource_file.exists():
            return "등록된 프로젝트 리소스가 없습니다."
        
        try:
            data = json.loads(resource_file.read_text(encoding='utf-8'))
            resources = data.get("resources", {})
            if not resources:
                return "등록된 프로젝트 리소스가 없습니다."
            
            lines = ["**공유 프로젝트 리소스** (파일 생성 시 여기에 자동 등록됨):"]
            for name, info in resources.items():
                lines.append(f"- {name} ({info['type']}): ID={info['id']}, 용도={info.get('purpose', 'N/A')}")
            return "\n".join(lines)
        except Exception:
            return "프로젝트 리소스를 불러오는 중 오류가 발생했습니다."

    async def process(
        self,
        user_message: str,
        session_id: str,
        context_package: Optional[Dict] = None
    ) -> str:
        """Process message and generate response (Supports tool calling)"""
        
        # Load current status
        current_status = self.load_current_status()
        
        # Build full prompt with context
        resources = self._load_project_resources()
        full_prompt = f"{self.system_prompt}\n\n{resources}\n\n"
        
        if context_package:
            full_prompt += f"""
**Master Agent로부터 받은 컨텍스트**:
- 전체 상황: {context_package.get('global_context', {})}
- 구체적 지침: {context_package.get('instructions', {})}
- 관련 정보: {context_package.get('related_info', {})}
- 기대 결과물: {context_package.get('expected_output', {})}

"""
        
        full_prompt += f"""
**현재 상태**: {current_status}

**사용자 요청**: {user_message}
"""
        
        try:
            # Get tools
            tools = self.get_tool_definitions()
            
            # Initialize model with tools if available
            # Gemini SDK expects tools in a specific list format
            if tools:
                model = genai.GenerativeModel(
                    'gemini-3-flash-preview',
                    tools=[{'function_declarations': tools}]
                )
            else:
                model = genai.GenerativeModel('gemini-3-flash-preview')
            
            chat = model.start_chat()
            response = chat.send_message(full_prompt)
            
            # Main response processing loop (handle tool calls)
            for _ in range(5): # Limit of 5 tool calls per turn
                content = response.candidates[0].content
                if not any(part.function_call for part in content.parts):
                    break
                
                # Collect all tool calls in the current turn
                tool_call_tasks = []
                tool_call_names = []
                for part in content.parts:
                    if part.function_call:
                        fc = part.function_call
                        tool_call_names.append(fc.name)
                        params = self._proto_to_python_value(fc.args)
                        tool_call_tasks.append(self.execute_tool(fc.name, params))
                
                if tool_call_tasks:
                    print(f"🛠️ Agent [{self.agent_id}] executing {len(tool_call_tasks)} tools in parallel: {tool_call_names}")
                    # Execute all tool calls in parallel
                    results = await asyncio.gather(*tool_call_tasks)
                    
                    tool_results = []
                    for name, result in zip(tool_call_names, results):
                        tool_results.append(
                            genai.protos.Part(
                                function_response=genai.protos.FunctionResponse(
                                    name=name,
                                    response={'result': result}
                                )
                            )
                        )
                    
                    # Send results back to model
                    response = chat.send_message(
                        genai.protos.Content(parts=tool_results)
                    )
            
            # After loop, extract final response text safely
            parts = response.candidates[0].content.parts
            response_text = "".join([part.text for part in parts if hasattr(part, 'text') and part.text])
            
            # If no text parts found (e.g. only tool calls left), use a fallback or the raw string
            if not response_text:
                if any(part.function_call for part in parts):
                    response_text = "[도구 호출 완료]"
                else:
                    response_text = str(response)
            
            # Update history
            self.conversation_history.append({"role": "user", "content": user_message})
            self.conversation_history.append({"role": "assistant", "content": response_text})
            
            return response_text
            
        except Exception as e:
            return f"Error processing request: {str(e)}"
