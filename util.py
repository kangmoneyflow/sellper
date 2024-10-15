import logging
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service   
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys

def setup_logger(name, log_level=logging.DEBUG, max_bytes=10*1024*1024):
    # 이미 로거가 존재하는지 확인 후 반환
    logger = logging.getLogger(name)
    if logger.hasHandlers():
        return logger

    # 로그 파일 생성 경로 설정
    start_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_dir = "./LOG/"
    os.makedirs(log_dir, exist_ok=True)
    log_file_path = os.path.join(log_dir, f"sellper_{start_time}.log")

    # 로거 레벨 설정
    logger.setLevel(log_level)

    # 핸들러 생성 함수
    def create_handler(handler, level):
        handler.setLevel(level)
        formatter = logging.Formatter('[%(asctime)s][%(name)s][%(funcName)s] %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    # 파일 핸들러: UTF-8 인코딩 설정 및 RotatingFileHandler 사용
    file_handler = RotatingFileHandler(log_file_path, maxBytes=max_bytes, encoding='utf-8')
    create_handler(file_handler, log_level)

    # 콘솔 핸들러
    create_handler(logging.StreamHandler(), log_level)

    return logger

def chrome_driver(user_data_path):
    options = Options()
    options.add_argument(f"user-data-dir={user_data_path}")
    # service = Service(ChromeDriverManager().install())
    service = Service()
    driver = webdriver.Chrome(service=service, options=options)
    print("Create chrome driver and return driver")
    return driver

def open_chrome_driver(url, user_data_path):
    """
    주어진 URL을 열고 크롬 드라이버를 반환합니다.
    """
    driver = chrome_driver(user_data_path)  # 드라이버 생성
    driver.implicitly_wait(3)  # 암묵적 대기 설정
    driver.get(url)  # 지정된 URL로 이동
    driver.maximize_window()  # 창 최대화
    print(f"Opened URL: {url}")
    return driver

# options = webdriver.ChromeOptions()
# driver = webdriver.Chrome(options=options)
# driver.get("https://www.amazon.in/")
# print(driver.title)
# driver.quit()