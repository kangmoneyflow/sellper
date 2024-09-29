import json
import os
from oauth2client.service_account import ServiceAccountCredentials
import gspread
import pandas as pd

class Config:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(base_dir, "config.json")
    config_data = None
    market_login_dict = None

    def __new__(cls, *args, **kwargs):
        if cls.config_data is None:
            cls._initialize()
        return super(Config, cls).__new__(cls)

    @classmethod
    def _initialize(cls):
        try:
            with open(cls.config_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
                config_data['cashdata']['path'] = config_data['cashdata']['path'].replace('home_path', os.path.expanduser('~'))
                cls.config_data = config_data  # 클래스 변수에 설정 데이터를 저장
                cls.config_data['google']['path'] = os.path.join(cls.base_dir, "google_auth.json")
        except FileNotFoundError:
            print(f"Error: {cls.config_path} / config.json 파일을 찾을 수 없습니다.")
            cls.config_data = None
        except json.JSONDecodeError:
            print(f"Error: {cls.config_path} / JSON 파일 형식이 올바르지 않습니다.")
            cls.config_data = None

    @classmethod
    def get_all_config(cls):
        return cls.config_data
    @classmethod
    def get_cash_ocnfig(cls):
        return cls.config_data['cashdata']
    @classmethod
    def get_google_config(cls):
        return cls.config_data['google']

    @classmethod
    def get_market_login_info(cls):
        if cls.market_login_dict is None:
            google_auth_json_path  = cls.config_data['google']['path']
            market_login_sheet_url = cls.config_data['google']['market_login_url']
            scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
            credential = ServiceAccountCredentials.from_json_keyfile_name(google_auth_json_path, scope)
            gc = gspread.authorize(credential)
            doc = gc.open_by_url(market_login_sheet_url)
            login_sheet = doc.worksheet("종합")
            df = pd.DataFrame(login_sheet.get_all_values())   
            first_row_as_keys = df.iloc[0]
            remaining_data = df.iloc[1:]
            cls.market_login_dict = {first_row_as_keys[col]: list(remaining_data[col]) for col in df.columns}            
        return cls.market_login_dict