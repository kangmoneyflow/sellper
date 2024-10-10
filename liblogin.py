import json
import os
import tempfile
from oauth2client.service_account import ServiceAccountCredentials
import gspread
import pandas as pd
from util import setup_logger

logger = setup_logger(__name__)

class LOGIN:
    login_sheets_dict = None  # 클래스 변수로 설정

    def __new__(cls, *args, **kwargs):
        if cls.login_sheets_dict is None:
            logger.info("LOGIN Class Initialization")
            cls._initialize()
        return super(LOGIN, cls).__new__(cls)

    @classmethod
    def _initialize(cls):
        cls._get_login_sheet("계정관리")

    @classmethod
    def _get_google_sheet(cls, sheet_url, sheet_name):
        # 임시 JSON 파일 생성
        google_auth_data = {
        }

        with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.json') as temp_file:
            json.dump(google_auth_data, temp_file)
            temp_file_path = temp_file.name

        try:
            # Google Sheets 인증
            scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
            credential = ServiceAccountCredentials.from_json_keyfile_name(temp_file_path, scope)
            gc = gspread.authorize(credential)
            doc = gc.open_by_url(sheet_url)
            sheet = doc.worksheet(sheet_name)
            df = pd.DataFrame(sheet.get_all_values())
            df.columns = df.iloc[0]  # 첫 번째 행을 컬럼 이름으로 설정
            df = df.iloc[1:].reset_index(drop=True)  # 첫 번째 행 제외하고 데이터프레임 갱신
            login_dict = df.set_index('아이디').to_dict(orient='index')  # '아이디' 열을 키로, 나머지 열을 값으로 하는 딕셔너리 생성
            return login_dict
        finally:
            # 임시 파일 삭제
            os.remove(temp_file_path)
    
    @classmethod
    def _get_login_sheet(cls, sheet_type):
        if cls.login_sheets_dict is None:
            cls.login_sheets_dict = {}
        if sheet_type not in cls.login_sheets_dict:
            login_sheet_url =  "https://docs.google.com/spreadsheets/d/1jki6UStOQj9Dq7ox3wSAAttL1NkeDSvTD5aDkVofVAA/edit?gid=0#gid=0"
            cls.login_sheets_dict[sheet_type] = cls._get_google_sheet(login_sheet_url, sheet_type)
            logger.info(f"{sheet_type} sheet loaded")
        return cls.login_sheets_dict[sheet_type]

    @classmethod
    def verify_login(cls, user_id, password):
        login_data = cls._get_login_sheet("계정관리")
        if (
            user_id in login_data
            and login_data[user_id]['비밀번호'] == password
            and login_data[user_id]['승인'].upper() == 'O'
        ):
            logger.info("Login successful")
            return True
        else:
            logger.warning("Login failed")
            return False