import os
import json
from pathlib import Path
from typing import Dict, List
from core.base_agent import BaseAgent
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

class CorporateFinanceAgent(BaseAgent):
    """넥스트나인 본사 재무 및 회계 관리 에이전트"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Root path of the project (one level up from multiagent_server)
        self.root_path = Path(__file__).parent.parent.parent.parent
        self.token_path = self.root_path / "token.json"
        self.creds_path = self.root_path / "credentials.json"

    def get_tool_definitions(self) -> List[Dict]:
        return [
            {
                "name": "update_budget_to_sheets",
                "description": "구글 시트의 [전체사업비] 시트에 예산 내역을 업데이트합니다.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "spreadsheet_id": {"type": "string", "description": "구글 시트 ID"},
                        "sheet_name": {"type": "string", "description": "시트 탭 이름 (예: Capex, Opex)"},
                        "headers": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "시트 헤더 (예: ['항목', '금액', '비고'])"
                        },
                        "budget_data": {
                            "type": "array",
                            "items": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "데이터 행"
                            },
                            "description": "업데이트할 데이터 행 목록"
                        }
                    },
                    "required": ["spreadsheet_id", "budget_data"]
                }
            },
            {
                "name": "create_budget_sheet",
                "description": "새로운 예산 관리용 구글 스프레드시트를 생성하고 리소스에 등록합니다.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string", "description": "시트 제목"},
                        "reason": {"type": "string", "description": "신규 생성 사유"}
                    },
                    "required": ["title", "reason"]
                }
            },
            {
                "name": "backup_budget_sheet",
                "description": "기존 예산 시트를 복사하여 백업본을 생성합니다.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "spreadsheet_id": {"type": "string", "description": "원본 시트 ID"},
                        "backup_title": {"type": "string", "description": "백업본 제목"}
                    },
                    "required": ["spreadsheet_id", "backup_title"]
                }
            },
            {
                "name": "delete_budget_sheet",
                "description": "프로젝트 리소스에서 더 이상 필요 없는 예산 시트를 삭제합니다. (주의: 실제 파일 삭제가 아닌 리소스 맵에서의 제거 및 주석 처리)",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "spreadsheet_name": {"type": "string", "description": "리소스 맵에서의 이름"}
                    },
                    "required": ["spreadsheet_name"]
                }
            },
            {
                "name": "update_worklog",
                "description": "에이전트작업일지 시트에 업무 수행 내역을 기록합니다.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "spreadsheet_id": {"type": "string", "description": "에이전트작업일지 시트 ID"},
                        "log_data": {
                            "type": "array",
                            "items": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "[날짜, 에이전트명, 업무내용, 비고] 리스트"
                            },
                            "description": "기록할 데이터 행 목록"
                        }
                    },
                    "required": ["spreadsheet_id", "log_data"]
                }
            }
        ]

    async def execute_tool(self, tool_name: str, parameters: Dict) -> Dict:
        if tool_name == "update_budget_to_sheets":
            try:
                # Get credentials
                creds = None
                if self.token_path.exists():
                    creds = Credentials.from_authorized_user_file(str(self.token_path), ['https://www.googleapis.com/auth/spreadsheets'])
                
                if not creds or not creds.valid:
                    return {"status": "error", "message": "Google Sheets 권한이 없습니다. token.json을 갱신해 주세요."}

                service = build('sheets', 'v4', credentials=creds)
                spreadsheet_id = parameters['spreadsheet_id']
                budget_data = parameters['budget_data']
                sheet_name = parameters.get('sheet_name', '전체사업비')
                headers = parameters.get('headers', ["항목", "예상금액", "비고"])

                # 1. Check if sheet exists, if not create it
                spreadsheet = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
                sheets = [s.get('properties').get('title') for s in spreadsheet.get('sheets')]
                
                if sheet_name not in sheets:
                    batch_update_request_body = {
                        'requests': [
                            {
                                'addSheet': {
                                    'properties': {
                                        'title': sheet_name
                                    }
                                }
                            }
                        ]
                    }
                    service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body=batch_update_request_body).execute()

                # 2. Update data
                # Header + Data
                values = [headers] + budget_data
                body = {
                    'values': values
                }
                range_name = f"'{sheet_name}'!A1"
                service.spreadsheets().values().update(
                    spreadsheetId=spreadsheet_id, range=range_name,
                    valueInputOption='RAW', body=body).execute()

                return {"status": "success", "message": f"'{sheet_name}' 시트에 {len(budget_data)}개의 항목이 업데이트되었습니다."}
            except Exception as e:
                return {"status": "error", "message": str(e)}

        elif tool_name == "create_budget_sheet":
            try:
                creds = Credentials.from_authorized_user_file(str(self.token_path), ['https://www.googleapis.com/auth/spreadsheets'])
                service = build('sheets', 'v4', credentials=creds)
                
                spreadsheet = {'properties': {'title': parameters['title']}}
                spreadsheet = service.spreadsheets().create(body=spreadsheet, fields='spreadsheetId').execute()
                ss_id = spreadsheet.get('spreadsheetId')
                
                # 리소스 맵에 등록 (데이터 디렉토리는 root_path 기준)
                res_path = self.root_path / "data" / "project_resources.json"
                if not res_path.parent.exists(): res_path.parent.mkdir(parents=True)
                
                data = {"resources": {}}
                if res_path.exists():
                    data = json.loads(res_path.read_text(encoding='utf-8'))
                
                from datetime import datetime
                data["resources"][parameters['title']] = {
                    "id": ss_id,
                    "type": "spreadsheet",
                    "purpose": f"Budget: {parameters['reason']}",
                    "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                res_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
                
                return {"status": "success", "spreadsheet_id": ss_id, "url": f"https://docs.google.com/spreadsheets/d/{ss_id}"}
            except Exception as e:
                return {"status": "error", "message": str(e)}

        elif tool_name == "backup_budget_sheet":
            try:
                creds = Credentials.from_authorized_user_file(str(self.token_path), ['https://www.googleapis.com/auth/drive'])
                drive_service = build('drive', 'v3', credentials=creds)
                
                copy_body = {'name': parameters['backup_title']}
                drive_response = drive_service.files().copy(fileId=parameters['spreadsheet_id'], body=copy_body).execute()
                backup_id = drive_response.get('id')
                
                return {"status": "success", "backup_id": backup_id, "message": f"백업본 '{parameters['backup_title']}'이 생성되었습니다."}
            except Exception as e:
                return {"status": "error", "message": str(e)}

        elif tool_name == "delete_budget_sheet":
            try:
                res_path = self.root_path / "data" / "project_resources.json"
                if res_path.exists():
                    data = json.loads(res_path.read_text(encoding='utf-8'))
                    if parameters['spreadsheet_name'] in data.get("resources", {}):
                        del data["resources"][parameters['spreadsheet_name']]
                        res_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
                        return {"status": "success", "message": f"'{parameters['spreadsheet_name']}' 리소스가 맵에서 제거되었습니다."}
                return {"status": "error", "message": "해당 리소스를 찾을 수 없습니다."}
            except Exception as e:
                return {"status": "error", "message": str(e)}

        elif tool_name == "update_worklog":
            try:
                creds = Credentials.from_authorized_user_file(str(self.token_path), ['https://www.googleapis.com/auth/spreadsheets'])
                service = build('sheets', 'v4', credentials=creds)
                
                spreadsheet_id = parameters['spreadsheet_id']
                log_data = parameters['log_data']
                
                # Check if headers exist, if not add them
                res = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range="A1:D1").execute()
                if not res.get('values'):
                    header = [["날짜", "에이전트명", "업무내용", "비고"]]
                    service.spreadsheets().values().update(
                        spreadsheetId=spreadsheet_id, range="A1",
                        valueInputOption='RAW', body={'values': header}).execute()
                
                # Append data
                body = {'values': log_data}
                service.spreadsheets().values().append(
                    spreadsheetId=spreadsheet_id, range="A2",
                    valueInputOption='RAW', body=body).execute()
                
                return {"status": "success", "message": f"{len(log_data)}건의 작업 기록이 업데이트되었습니다."}
            except Exception as e:
                return {"status": "error", "message": str(e)}
        
        return {"status": "not_implemented", "tool": tool_name}
