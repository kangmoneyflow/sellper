import json
import os
from oauth2client.service_account import ServiceAccountCredentials
import gspread
import pandas as pd
from util import setup_logger
import tempfile
import winreg

logger = setup_logger(__name__)

class Config:
    base_dir = "./"
    config_path = os.path.join(base_dir, "config.json")
    config_data = None
    
    # 각 데이터 시트에 대한 저장 변수
    cashdata_sheets_dict = {}

    def __new__(cls, *args, **kwargs):
        if cls.config_data is None:
            logger.info("Config Class Initialization")
            cls._initialize()
        return super(Config, cls).__new__(cls)
    
    @classmethod
    def get_desktop_path(cls):
        # 레지스트리에서 경로 가져오기 (OneDrive 여부 포함)
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders")
            desktop, _ = winreg.QueryValueEx(key, "Desktop")
            winreg.CloseKey(key)
            return os.path.expandvars(desktop)
        except Exception as e:
            print(f"에러 발생: {e}")
            # 기본 경로 시도
            return os.path.join(os.path.expanduser("~"), "Desktop")

    @classmethod
    def _initialize(cls):
        try:
            with open(cls.config_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
                desktop_path = cls.get_desktop_path()
                if 'cashdata' not in config_data:
                    config_data['cashdata'] = {}
                config_data['cashdata']['path'] = os.path.join(desktop_path, "캐시데이터3.appref-ms")
                cls.config_data = config_data
        except FileNotFoundError:
            logger.error(f"Error: {cls.config_path} / config.json 파일을 찾을 수 없습니다.")
        except json.JSONDecodeError:
            logger.error(f"Error: {cls.config_path} / JSON 파일 형식이 올바르지 않습니다.")

    @classmethod
    def get_all_config(cls):
        return cls.config_data

    @classmethod
    def get_cash_config(cls):
        return cls.config_data['cashdata']

    @classmethod
    def get_google_config(cls):
        return cls.config_data['google']

    @classmethod
    def _get_google_sheet(cls, sheet_url, sheet_name):
        google_auth_data = {
        }
        with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.json') as temp_file:
            json.dump(google_auth_data, temp_file)
            temp_file_path = temp_file.name

        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        credential = ServiceAccountCredentials.from_json_keyfile_name(temp_file_path, scope)
        gc = gspread.authorize(credential)
        doc = gc.open_by_url(sheet_url)
        sheet = doc.worksheet(sheet_name)
        df = pd.DataFrame(sheet.get_all_values())
        first_row_as_keys = df.iloc[0]
        remaining_data = df.iloc[1:]
        return {first_row_as_keys[col]: list(remaining_data[col]) for col in df.columns}
    
    @classmethod
    def _get_cashdata_sheet(cls, sheet_type):
        if sheet_type not in cls.cashdata_sheets_dict:
            cashdata_sheet_url = cls.config_data['google']['cashdata_sheet_url']
            cls.cashdata_sheets_dict[sheet_type] = cls._get_google_sheet(cashdata_sheet_url, sheet_type)
            logger.info(f"{sheet_type} sheet loaded")
        return cls.cashdata_sheets_dict[sheet_type]

    @classmethod
    def get_market_login_info(cls):
        return cls._get_cashdata_sheet("계정")        

    @classmethod
    def get_cashdata_create_sheet(cls):
        return cls._get_cashdata_sheet("생성")

    @classmethod
    def get_cashdata_scrap_sheet(cls):
        return cls._get_cashdata_sheet("수집")

    @classmethod
    def get_cashdata_delete_sheet(cls):
        return cls._get_cashdata_sheet("삭제")

    @classmethod
    def get_cashdata_upload_sheet(cls):
        return cls._get_cashdata_sheet("업로드")