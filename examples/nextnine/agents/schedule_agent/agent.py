"""
Schedule Agent - Calendar and deadline management
"""

from core.base_agent import BaseAgent
from typing import Dict, List


class ScheduleAgent(BaseAgent):
    """Schedule Agent for calendar and deadline management"""
    
    def get_tool_definitions(self) -> List[Dict]:
        """Schedule Agent specific tools"""
        return [
            {
                "name": "add_event",
                "description": "일정 추가",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string", "description": "일정 제목"},
                        "date": {"type": "string", "description": "날짜 (YYYY-MM-DD)"},
                        "time": {"type": "string", "description": "시간 (HH:MM)"},
                        "duration": {"type": "number", "description": "소요 시간 (분)"}
                    },
                    "required": ["title", "date"]
                }
            },
            {
                "name": "check_schedule",
                "description": "일정 확인",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "date": {"type": "string", "description": "날짜 (YYYY-MM-DD)"},
                        "agent_id": {"type": "string", "description": "특정 에이전트 일정"}
                    }
                }
            },
            {
                "name": "send_reminder",
                "description": "리마인더 전송",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "event_id": {"type": "string"},
                        "advance_minutes": {"type": "number", "description": "몇 분 전에 알림"}
                    },
                    "required": ["event_id"]
                }
            },
            {
                "name": "resolve_conflict",
                "description": "일정 충돌 해결",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "event_ids": {"type": "array", "items": {"type": "string"}},
                        "resolution": {"type": "string", "enum": ["reschedule", "cancel", "merge"]}
                    },
                    "required": ["event_ids", "resolution"]
                }
            }
        ]
