"""
Agent Loader - Dynamically loads agents from agentconfig.json
"""

import json
import importlib
from pathlib import Path
from typing import Dict, List, Optional
from core.base_agent import BaseAgent


class AgentLoader:
    """Loads and manages agents from agentconfig.json"""
    
    def __init__(self, config_path: Path, gemini_api_key: str, work_docs_dir: Path):
        self.config_path = config_path
        self.gemini_api_key = gemini_api_key
        self.work_docs_dir = work_docs_dir
        self.config = None
        self.agents: Dict[str, BaseAgent] = {}
    
    def load_config(self) -> Dict:
        """Load agentconfig.json"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        return self.config
    
    def validate_config(self) -> bool:
        """Validate configuration structure"""
        if not self.config:
            return False
        
        required_fields = ['project', 'mcp_server', 'llm_provider', 'agents']
        for field in required_fields:
            if field not in self.config:
                print(f"Missing required field: {field}")
                return False
        
        return True
    
    def load_agents(self) -> Dict[str, BaseAgent]:
        """Dynamically load all enabled agents"""
        if not self.config:
            self.load_config()
        
        if not self.validate_config():
            raise ValueError("Invalid configuration")
        
        for agent_config in self.config['agents']:
            if not agent_config.get('enabled', True):
                continue
            
            try:
                # Import agent module
                module_path = agent_config['module']
                class_name = agent_config['class']
                
                module = importlib.import_module(module_path)
                AgentClass = getattr(module, class_name)
                
                # Instantiate agent
                agent = AgentClass(
                    agent_id=agent_config['id'],
                    agent_name=agent_config['name'],
                    role=agent_config['role'],
                    tone=agent_config['tone'],
                    keywords=agent_config['keywords'],
                    gemini_api_key=self.gemini_api_key,
                    work_docs_dir=self.work_docs_dir,
                    job_category=agent_config.get('job_category'),
                    scope=agent_config.get('scope'),
                    tools=agent_config.get('tools'),
                    integrations=agent_config.get('integrations')
                )
                
                self.agents[agent_config['id']] = agent
                print(f"✓ Loaded agent: {agent_config['name']}")
                
            except Exception as e:
                print(f"✗ Failed to load agent {agent_config['id']}: {str(e)}")
        
        return self.agents
    
    def get_agent(self, agent_id: str) -> Optional[BaseAgent]:
        """Get agent by ID"""
        return self.agents.get(agent_id)
    
    def list_agents(self) -> List[Dict]:
        """List all loaded agents"""
        return [
            {
                "id": agent.agent_id,
                "name": agent.agent_name,
                "role": agent.role,
                "tone": agent.tone
            }
            for agent in self.agents.values()
        ]
    def add_agent_dynamic(self, agent_config: Dict) -> BaseAgent:
        """Add a new agent at runtime and persist to config"""
        # 'id' 또는 'agent_id' 모두 지원 (유연성 확보)
        agent_id = agent_config.get('id') or agent_config.get('agent_id')
        if not agent_id:
            raise ValueError("Agent ID is required (key: 'id' or 'agent_id')")
            
        if agent_id in self.agents:
            raise ValueError(f"Agent {agent_id} already exists")
            
        try:
            # 1. Import and Instantiate
            # 명시적으로 'id' 키로 통일 (config 저장용)
            agent_config['id'] = agent_id
            
            module_path = agent_config['module']
            class_name = agent_config['class']
            module = importlib.import_module(module_path)
            AgentClass = getattr(module, class_name)
            
            print(f"🛠️ Instantiating dynamic agent: {agent_id} using {class_name}")
            
            agent = AgentClass(
                agent_id=agent_id,
                agent_name=agent_config.get('name') or agent_config.get('agent_name', agent_id),
                role=agent_config['role'],
                tone=agent_config.get('tone', 'Professional'),
                keywords=agent_config.get('keywords', []),
                gemini_api_key=self.gemini_api_key,
                work_docs_dir=self.work_docs_dir,
                job_category=agent_config.get('job_category'),
                scope=agent_config.get('scope'),
                tools=agent_config.get('tools', [])
            )
            
            # 2. Add to active agents
            self.agents[agent_id] = agent
            
            # 3. Persist to agentconfig.json
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Update only if not already present in the list
            if not any(a['id'] == agent_id for a in config['agents']):
                config['agents'].append(agent_config)
                with open(self.config_path, 'w', encoding='utf-8') as f:
                    json.dump(config, f, ensure_ascii=False, indent=2)
            
            print(f"✨ Dynamically added agent: {agent_config['name']}")
            return agent
            
        except Exception as e:
            print(f"✗ Failed to add dynamic agent {agent_id}: {str(e)}")
            raise
