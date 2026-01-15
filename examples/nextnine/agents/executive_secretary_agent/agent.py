import json
from datetime import datetime
from pathlib import Path
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from core.base_agent import BaseAgent
from typing import Dict, List

class ExecutiveSecretaryAgent(BaseAgent):
    """넥스트나인 임원 일정 및 행정 지원 에이전트 서비스"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.resource_file = Path("data/project_resources.json")
        self.token_path = Path("token.json")

    def get_tool_definitions(self) -> List[Dict]:
        return [
            {
                "name": "create_google_spreadsheet",
                "description": "새로운 구글 스프레드시트를 생성하고 프로젝트 리소스에 등록합니다.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string", "description": "시트 제목"},
                        "purpose": {"type": "string", "description": "사용 용도"}
                    },
                    "required": ["title", "purpose"]
                }
            },
            {
                "name": "create_google_document",
                "description": "새로운 구글 문서(Docs)를 생성하고 프로젝트 리소스에 등록합니다.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "purpose": {"type": "string"}
                    },
                    "required": ["title", "purpose"]
                }
            },
            {
                "name": "create_google_slides",
                "description": "새로운 구글 슬라이드(Slides)를 생성하고 프로젝트 리소스에 등록합니다.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "purpose": {"type": "string"}
                    },
                    "required": ["title", "purpose"]
                }
            },
            {
                "name": "send_email",
                "description": "Gmail을 사용하여 이메일을 발송합니다.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "to": {"type": "string", "description": "수신자 이메일 주소"},
                        "subject": {"type": "string", "description": "이메일 제목"},
                        "body": {"type": "string", "description": "이메일 본문 (텍스트)"}
                    },
                    "required": ["to", "subject", "body"]
                }
            },
            {
                "name": "register_resource",
                "description": "생성된 파일 ID나 링크를 프로젝트 공유 리소스 파일에 기록합니다.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "리소스 이름 (예: 전체예산시트)"},
                        "id": {"type": "string", "description": "파일 ID"},
                        "type": {"type": "string", "enum": ["spreadsheet", "document", "slides", "other"]},
                        "purpose": {"type": "string"}
                    },
                    "required": ["name", "id", "type"]
                }
            }
        ]

    async def execute_tool(self, tool_name: str, parameters: Dict) -> Dict:
        if tool_name == "create_google_spreadsheet":
            try:
                creds = Credentials.from_authorized_user_file(str(self.token_path), ['https://www.googleapis.com/auth/spreadsheets'])
                service = build('sheets', 'v4', credentials=creds)
                
                spreadsheet = {
                    'properties': {
                        'title': parameters['title']
                    }
                }
                spreadsheet = service.spreadsheets().create(body=spreadsheet, fields='spreadsheetId').execute()
                ss_id = spreadsheet.get('spreadsheetId')
                
                # 자동 등록
                await self.execute_tool("register_resource", {
                    "name": parameters['title'],
                    "id": ss_id,
                    "type": "spreadsheet",
                    "purpose": parameters['purpose']
                })
                
                return {"status": "success", "spreadsheet_id": ss_id, "url": f"https://docs.google.com/spreadsheets/d/{ss_id}"}
            except Exception as e:
                return {"status": "error", "message": str(e)}

        elif tool_name == "create_google_document":
            try:
                creds = Credentials.from_authorized_user_file(str(self.token_path), ['https://www.googleapis.com/auth/documents'])
                service = build('docs', 'v1', credentials=creds)
                
                doc = {'title': parameters['title']}
                doc = service.documents().create(body=doc).execute()
                doc_id = doc.get('documentId')
                
                await self.execute_tool("register_resource", {
                    "name": parameters['title'],
                    "id": doc_id,
                    "type": "document",
                    "purpose": parameters['purpose']
                })
                
                return {"status": "success", "document_id": doc_id, "url": f"https://docs.google.com/document/d/{doc_id}"}
            except Exception as e:
                return {"status": "error", "message": str(e)}

        elif tool_name == "create_google_slides":
            try:
                creds = Credentials.from_authorized_user_file(str(self.token_path), ['https://www.googleapis.com/auth/presentations'])
                service = build('slides', 'v1', credentials=creds)
                
                presentation = {'title': parameters['title']}
                presentation = service.presentations().create(body=presentation).execute()
                presentation_id = presentation.get('presentationId')
                
                await self.execute_tool("register_resource", {
                    "name": parameters['title'],
                    "id": presentation_id,
                    "type": "slides",
                    "purpose": parameters['purpose']
                })
                
                return {"status": "success", "presentation_id": presentation_id, "url": f"https://docs.google.com/presentation/d/{presentation_id}"}
            except Exception as e:
                return {"status": "error", "message": str(e)}

        elif tool_name == "send_email":
            try:
                import base64
                from email.message import EmailMessage
                
                creds = Credentials.from_authorized_user_file(str(self.token_path), ['https://www.googleapis.com/auth/gmail.send'])
                service = build('gmail', 'v1', credentials=creds)
                
                message = EmailMessage()
                message.set_content(parameters['body'])
                message['To'] = parameters['to']
                message['From'] = 'me'
                message['Subject'] = parameters['subject']
                
                encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
                create_message = {'raw': encoded_message}
                
                send_message = (service.users().messages().send(userId="me", body=create_message).execute())
                return {"status": "success", "message_id": send_message['id']}
            except Exception as e:
                return {"status": "error", "message": str(e)}

        elif tool_name == "register_resource":
            try:
                if not self.resource_file.exists():
                    data = {"resources": {}}
                else:
                    data = json.loads(self.resource_file.read_text(encoding='utf-8'))
                
                data["resources"][parameters['name']] = {
                    "id": parameters['id'],
                    "type": parameters['type'],
                    "purpose": parameters.get('purpose', ""),
                    "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                
                self.resource_file.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
                return {"status": "success", "message": f"'{parameters['name']}' 리소스가 등록되었습니다."}
            except Exception as e:
                return {"status": "error", "message": str(e)}

        return {"status": "not_implemented", "tool": tool_name}
