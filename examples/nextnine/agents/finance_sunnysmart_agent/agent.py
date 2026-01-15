"""
FinanceSunnySmartAgent - SunnySmart 전담 에이전트
"""

from core.base_agent import BaseAgent
from typing import Dict, List


class FinanceSunnySmartAgent(BaseAgent):
    """SunnySmart 업무 전담 에이전트"""
    
    def get_tool_definitions(self) -> List[Dict]:
        """Agent-specific tool definitions"""
        # TODO: Implement specific tools for this agent
        return []
    
    async def execute_tool(self, tool_name: str, parameters: Dict) -> Dict:
        """Execute agent-specific tools"""
        # TODO: Implement tool execution logic
        return {"status": "not_implemented", "tool": tool_name}
