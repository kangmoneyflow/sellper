import logging
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime

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
