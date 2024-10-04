import json
import os
from oauth2client.service_account import ServiceAccountCredentials
import gspread
import pandas as pd
from util import setup_logger
logger = setup_logger(__name__)


class Config:
    base_dir = "./"
    # config_path = os.path.join(base_dir, "config.json")
    config_path = os.path.join(base_dir, "config.json")
    config_data = None
    market_login_dict = None
    cashdata_create_dict = None
    cashdata_scrap_dict = None
    cashdata_delete_dict = None
    cashdata_upload_dict = None

    def __new__(cls, *args, **kwargs):
        if cls.config_data is None:
            logger.info("Config Class Initialization")
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
                logger.info(cls.config_data)
        except FileNotFoundError:
            logger.info(f"Error: {cls.config_path} / config.json 파일을 찾을 수 없습니다.")
            cls.config_data = None
        except json.JSONDecodeError:
            logger.info(f"Error: {cls.config_path} / JSON 파일 형식이 올바르지 않습니다.")
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
            logger.info("get_market_login_info")
        return cls.market_login_dict
    
    @classmethod
    def get_cashdata_create_sheet(cls):
        if cls.cashdata_create_dict is None:
            google_auth_json_path  = cls.config_data['google']['path']
            cashdata_sheet_url = cls.config_data['google']['cashdata_sheet_url']
            scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
            credential = ServiceAccountCredentials.from_json_keyfile_name(google_auth_json_path, scope)
            gc = gspread.authorize(credential)
            doc = gc.open_by_url(cashdata_sheet_url)
            create_sheet = doc.worksheet("생성")

            df_create = pd.DataFrame(create_sheet.get_all_values())   

            first_row_as_keys = df_create.iloc[0]
            remaining_data = df_create.iloc[1:]
            cls.cashdata_create_dict = {first_row_as_keys[col]: list(remaining_data[col]) for col in df_create.columns}            
            logger.info("get_cashdata_create_sheet")
        return cls.cashdata_create_dict          
   
    @classmethod
    def get_cashdata_scrap_sheet(cls):
        if cls.cashdata_scrap_dict is None:
            google_auth_json_path  = cls.config_data['google']['path']
            cashdata_sheet_url = cls.config_data['google']['cashdata_sheet_url']
            scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
            credential = ServiceAccountCredentials.from_json_keyfile_name(google_auth_json_path, scope)
            gc = gspread.authorize(credential)
            doc = gc.open_by_url(cashdata_sheet_url)
            scrap_sheet = doc.worksheet("수집")
            df_scrap = pd.DataFrame(scrap_sheet.get_all_values())   
            first_row_as_keys = df_scrap.iloc[0]
            remaining_data = df_scrap.iloc[1:]
            cls.cashdata_scrap_dict = {first_row_as_keys[col]: list(remaining_data[col]) for col in df_scrap.columns}            
            logger.info("get_cashdata_scrap_sheet")
        return cls.cashdata_scrap_dict

    @classmethod
    def get_cashdata_delete_sheet(cls):
        if cls.cashdata_delete_dict is None:
            google_auth_json_path  = cls.config_data['google']['path']
            cashdata_sheet_url = cls.config_data['google']['cashdata_sheet_url']
            scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
            credential = ServiceAccountCredentials.from_json_keyfile_name(google_auth_json_path, scope)
            gc = gspread.authorize(credential)
            doc = gc.open_by_url(cashdata_sheet_url)
            delete_sheet = doc.worksheet("삭제")
            df_delete = pd.DataFrame(delete_sheet.get_all_values())   
            first_row_as_keys = df_delete.iloc[0]
            remaining_data = df_delete.iloc[1:]
            cls.cashdata_delete_dict = {first_row_as_keys[col]: list(remaining_data[col]) for col in df_delete.columns}            
            logger.info("get_cashdata_delete_sheet")
        return cls.cashdata_delete_dict          

    @classmethod
    def get_cashdata_upload_sheet(cls):
        if cls.cashdata_upload_dict is None:
            google_auth_json_path  = cls.config_data['google']['path']
            cashdata_sheet_url = cls.config_data['google']['cashdata_sheet_url']
            scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
            credential = ServiceAccountCredentials.from_json_keyfile_name(google_auth_json_path, scope)
            gc = gspread.authorize(credential)
            doc = gc.open_by_url(cashdata_sheet_url)
            upload_sheet = doc.worksheet("업로드")
            df_upload = pd.DataFrame(upload_sheet.get_all_values())   
            first_row_as_keys = df_upload.iloc[0]
            remaining_data = df_upload.iloc[1:]
            cls.cashdata_upload_dict = {first_row_as_keys[col]: list(remaining_data[col]) for col in df_upload.columns}            
            logger.info("get_cashdata_upload_sheet")
        return cls.cashdata_upload_dict                      