import json
import os

class Config:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(base_dir, "config.json")
    config_data = None

    def __new__(cls, *args, **kwargs):
        if cls.config_data is None:
            cls._initialize()
        return super(Config, cls).__new__(cls)

    @classmethod
    def _initialize(cls):
        try:
            with open(cls.config_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
                config_data['cashdata']['run_path'] = config_data['cashdata']['run_path'].replace('home_path', os.path.expanduser('~'))
                cls.config_data = config_data  # 클래스 변수에 설정 데이터를 저장
        except FileNotFoundError:
            print(f"Error: {cls.config_path} / config.json 파일을 찾을 수 없습니다.")
            cls.config_data = None
        except json.JSONDecodeError:
            print(f"Error: {cls.config_path} / JSON 파일 형식이 올바르지 않습니다.")
            cls.config_data = None

    @classmethod
    def get_google_config(cls):
        # config_data가 None이면 구글 설정을 반환하지 않음
        if cls.config_data is None:
            print("Error: config_data가 로드되지 않았습니다.")
            return None
        if 'google' not in cls.config_data:
            print("Error: 'google' 설정이 config_data에 없습니다.")
            return None
        cls.config_data['google']['path'] = os.path.join(cls.base_dir, "google_auth.json")
        return cls.config_data['google']
