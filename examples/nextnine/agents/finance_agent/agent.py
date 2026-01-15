"""
Finance Agent - Budget management and financial analysis
"""

from core.base_agent import BaseAgent
from typing import Dict, List


class FinanceAgent(BaseAgent):
    """Finance Agent for budget and financial management"""
    
    def get_tool_definitions(self) -> List[Dict]:
        """Finance Agent specific tools"""
        return [
            {
                "name": "check_budget",
                "description": "현재 예산 사용률 확인",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "category": {"type": "string", "description": "예산 카테고리"}
                    }
                }
            },
            {
                "name": "record_expense",
                "description": "지출 기록",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "amount": {"type": "number", "description": "금액"},
                        "category": {"type": "string", "description": "카테고리"},
                        "description": {"type": "string", "description": "설명"}
                    },
                    "required": ["amount", "category"]
                }
            },
            {
                "name": "generate_financial_report",
                "description": "재무 리포트 생성",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "period": {"type": "string", "enum": ["monthly", "quarterly", "yearly"]},
                        "include_forecast": {"type": "boolean"}
                    },
                    "required": ["period"]
                }
            },
            {
                "name": "calculate_roi",
                "description": "ROI 계산",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "investment": {"type": "number"},
                        "return": {"type": "number"}
                    },
                    "required": ["investment", "return"]
                }
            }
        ]
