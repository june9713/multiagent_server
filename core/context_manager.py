"""
Context Manager - Master Agent context propagation to sub-agents
"""

import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime


class ContextManager:
    """Manages global context and Master Agent context propagation"""
    
    def __init__(self, work_docs_dir: Path):
        self.work_docs_dir = work_docs_dir
        self.master_context_file = work_docs_dir / "master_agent" / "context_history.json"
        self.master_context_file.parent.mkdir(parents=True, exist_ok=True)
    
    def load_global_context(self) -> Dict:
        """Load global project context"""
        if not self.master_context_file.exists():
            return {
                "project": "NEXTNINE",
                "last_updated": datetime.now().isoformat(),
                "global_context": {
                    "current_phase": "",
                    "overall_progress": "0%",
                    "critical_deadlines": [],
                    "blocking_issues": []
                },
                "agent_contexts": {}
            }
        
        with open(self.master_context_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def update_global_context(self, updates: Dict) -> None:
        """Update global project context"""
        context = self.load_global_context()
        
        # Merge updates
        if 'global_context' in updates:
            context['global_context'].update(updates['global_context'])
        
        if 'agent_contexts' in updates:
            for agent_id, agent_context in updates['agent_contexts'].items():
                context['agent_contexts'][agent_id] = agent_context
        
        context['last_updated'] = datetime.now().isoformat()
        
        # Save
        with open(self.master_context_file, 'w', encoding='utf-8') as f:
            json.dump(context, f, ensure_ascii=False, indent=2)
    
    def create_context_package(
        self,
        target_agent: str,
        task_id: str,
        task_description: str,
        global_context: Dict,
        instructions: Dict,
        related_info: Optional[Dict] = None,
        expected_output: Optional[Dict] = None,
        collaboration: Optional[Dict] = None
    ) -> Dict:
        """Create context package for sub-agent"""
        
        package = {
            "task_id": task_id,
            "task_description": task_description,
            "created_at": datetime.now().isoformat(),
            "target_agent": target_agent,
            
            # 1. Big Picture
            "global_context": global_context,
            
            # 2. Specific Instructions
            "instructions": instructions,
            
            # 3. Related Information
            "related_info": related_info or {},
            
            # 4. Expected Output
            "expected_output": expected_output or {},
            
            # 5. Collaboration Info
            "collaboration": collaboration or {}
        }
        
        return package
    
    def load_agent_context(self, agent_id: str) -> Dict:
        """Load agent's current context from work_docs"""
        agent_dir = self.work_docs_dir / agent_id
        
        if not agent_dir.exists():
            return {}
        
        # Load current_status.md
        status_file = agent_dir / "current_status.md"
        status_content = ""
        if status_file.exists():
            status_content = status_file.read_text(encoding='utf-8')
        
        # Load work_log.json
        log_file = agent_dir / "work_log.json"
        work_log = {}
        if log_file.exists():
            with open(log_file, 'r', encoding='utf-8') as f:
                work_log = json.load(f)
        
        return {
            "current_status": status_content,
            "work_log": work_log,
            "last_updated": work_log.get('last_updated', '')
        }
    
    def get_agent_context_for_delegation(self, agent_id: str) -> Optional[Dict]:
        """Get context to provide when delegating to this agent"""
        global_context = self.load_global_context()
        return global_context.get('agent_contexts', {}).get(agent_id)
