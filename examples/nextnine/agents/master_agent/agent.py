"""
Master Agent - Project orchestration and agent coordination
"""

from core.base_agent import BaseAgent
from typing import Dict, List


class MasterAgent(BaseAgent):
    """Master Agent for project orchestration"""
    
    def get_tool_definitions(self) -> List[Dict]:
        """Master Agent specific tools"""
        return [
            {
                "name": "delegate_task",
                "description": "다른 에이전트에게 작업 위임",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "target_agent": {"type": "string", "description": "대상 에이전트 ID"},
                        "task_description": {"type": "string", "description": "작업 설명"},
                        "context": {"type": "object", "description": "컨텍스트 정보"}
                    },
                    "required": ["target_agent", "task_description"]
                }
            },
            {
                "name": "generate_report",
                "description": "프로젝트 리포트 생성",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "report_type": {"type": "string", "enum": ["daily", "weekly", "monthly"]},
                        "include_agents": {"type": "array", "items": {"type": "string"}}
                    },
                    "required": ["report_type"]
                }
            },
            {
                "name": "approve_decision",
                "description": "주요 의사결정 승인",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "decision": {"type": "string", "description": "의사결정 내용"},
                        "approved": {"type": "boolean"},
                        "notes": {"type": "string"}
                    },
                    "required": ["decision", "approved"]
                }
            },
            {
                "name": "create_context_package",
                "description": "서브 에이전트에게 전달할 컨텍스트 패키지 생성",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "target_agent": {"type": "string"},
                        "global_context": {"type": "object"},
                        "instructions": {"type": "object"},
                        "expected_output": {"type": "object"}
                    },
                    "required": ["target_agent", "instructions"]
                }
            }
        ]

    async def execute_tool(self, tool_name: str, parameters: Dict) -> Dict:
        """Execute Master Agent specific tools"""
        import httpx
        import os
        
        host = os.getenv("MCP_HOST", "localhost")
        port = os.getenv("MCP_PORT", "8000")
        base_url = f"http://{host}:{port}/api/v1"

        if tool_name == "delegate_task":
            try:
                target_agent = parameters['target_agent']
                task_description = parameters['task_description']
                context = parameters.get('context', {})
                
                print(f"👑 Master Delegating to [{target_agent}]: {task_description[:50]}...")
                
                async with httpx.AsyncClient(timeout=60.0) as client:
                    response = await client.post(
                        f"{base_url}/agent/invoke",
                        json={
                            "agent_id": target_agent,
                            "message": task_description,
                            "context_package": context
                        }
                    )
                    response.raise_for_status()
                    result = response.json()
                    return {"status": "success", "agent_id": target_agent, "response": result['response']}
            except Exception as e:
                return {"status": "error", "message": f"Delegation failed: {str(e)}"}

        elif tool_name == "generate_report":
            # This is a mock internal report generator
            return {"status": "success", "message": f"{parameters['report_type']} 리포트가 생성 대기 중입니다."}

        elif tool_name == "approve_decision":
            return {"status": "success", "decision": parameters['decision'], "approved": parameters['approved']}

        elif tool_name == "create_context_package":
            return {"status": "success", "package": parameters}

        return {"status": "not_implemented", "tool": tool_name}
