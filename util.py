import logging
import os
from datetime import datetime

# 로거 설정 함수
def setup_logger(name):
    # 프로그램 시작 시간으로 고유한 로그 파일 이름 생성
    start_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_dir = "./LOG/"

    # 로그 디렉토리 존재 여부 확인 후 생성
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    log_file_path = os.path.join(log_dir, f"sellper_{start_time}.log")  # 실행 시간 기반 고유 파일 이름 생성

    # 로거 생성
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # 파일 핸들러 설정
    file_handler = logging.FileHandler(log_file_path)
    file_handler.setLevel(logging.DEBUG)

    # 콘솔 핸들러 설정 (터미널 출력용)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)

    # 로그 포맷 설정 - [시간][파일명] 로그내용
    formatter = logging.Formatter('[%(asctime)s][%(name)s] %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # 핸들러가 없을 경우 추가 (중복 방지)
    if not logger.hasHandlers():
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger
