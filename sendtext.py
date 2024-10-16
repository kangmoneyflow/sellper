import time
import pyperclip
import pyautogui
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
import util as UTIL
from util import *

logger = setup_logger(__name__)

class MessageSender:
    def __init__(self, user_data_path, text_edit=None):
        """
        사용자 데이터 경로를 받아 크롬 드라이버를 초기화합니다.
        """
        self.text_edit = text_edit  # QTextEdit 인스턴스 저장
        template_path = "./문자발송양식.txt"
        self.template = self.load_template(template_path)
        self.driver = UTIL.open_chrome_driver("https://messages.google.com/web/authentication", user_data_path, ismin=True)
    
    def _log_to_gui(self, message):
        """로그 메시지를 GUI의 QTextEdit에 출력"""
        if self.text_edit:
            self.text_edit.append(message)

    def load_template(self, template_path):
        """
        주어진 경로에서 메시지 템플릿을 로드합니다.
        """
        try:
            with open(template_path, "r", encoding="UTF-8") as f:
                template = f.read()
            self._log_to_gui("메세지 템플릿 읽기 성공")
            logger.info("메세지 템플릿 읽기 성공")
            return template
        except FileNotFoundError:
            error_message = f"Error: {template_path} 파일을 찾을 수 없습니다."
            logger.info(error_message)
            return ""
        
    def get_selector(self, css_selector, timeout=10):
        """CSS 선택자로 요소를 기다린 후 반환하는 함수."""
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, css_selector))
        )

    def get_xpath(self, xpath, timeout=10):
        """XPath 선택자로 요소를 기다린 후 반환하는 함수."""
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )
    
    def wait_for_xpath(self, xpath, timeout=180):
        """특정 XPath가 나타날 때까지 반복 검사"""
        start_time = time.time()
        while True:
            try:
                # 요소가 있는지 확인
                element = self.driver.find_element(By.XPATH, xpath)
                print(f"요소 발견: {xpath}")
                return True  # 발견 시 True 반환
            except Exception as e:  # 모든 예외 처리
                # 타임아웃 검사
                if time.time() - start_time > timeout:
                    print(f"타임아웃: 요소를 찾을 수 없습니다. 예외: {e}")
                    return False  # 타임아웃 시 False 반환
                print(f"요소가 아직 없습니다. 예외: {e} - 다시 시도합니다...")
                time.sleep(1)  # 1초 대기 후 재시도

    def send_message(self, phone, templete):
        """
        주어진 전화번호와 템플릿을 사용해 메시지를 전송합니다.
        """
        for i in range(10):
            try:
                xpath = '/html/body/mw-app/mw-bootstrap/div/main/mw-main-container/div/mw-main-nav/div/mw-fab-link/a/span[2]/div/div'
                self.get_xpath(xpath).click()

                xpath = '/html/body/mw-app/mw-bootstrap/div/main/mw-main-container/div/mw-new-conversation-container/mw-new-conversation-sub-header/div/div[2]/mw-contact-chips-input/div/div/input'
                elm = self.get_xpath(xpath)
                elm.click()
                pyperclip.copy(phone)
                elm.send_keys(Keys.CONTROL, 'v') #번호 입력

                xpath = '/html/body/mw-app/mw-bootstrap/div/main/mw-main-container/div/mw-new-conversation-container/div/mw-contact-selector-button/button/span[4]'
                self.get_xpath(xpath).click()

                xpath = '/html/body/mw-app/mw-bootstrap/div/main/mw-main-container/div/mw-conversation-container/div/div[1]/div/mws-message-compose/div/div[2]/div/div/mws-autosize-textarea/textarea'
                elm = self.get_xpath(xpath)
                elm.click()#문자 창 클릭
                pyperclip.copy(templete)
                elm.send_keys(Keys.CONTROL, 'v') #문자 입력
                elm.send_keys(Keys.ENTER) # 문자 보내기
                logger.info(f"{phone} 메시지 전송 성공")
                self._log_to_gui(f"{phone} 메시지 전송 성공")
                break
            except Exception as e:
                logger.info(f"오류 발생: {e} - {phone}")
                time.sleep(2)

    def send_messages_to_all(self, data_dict):
        """
        딕셔너리에 있는 모든 사용자에게 메시지를 전송합니다.
        """
        time.sleep(1)
        current_url = self.driver.current_url
        if "authentication" in current_url:
            i = 0
            while True:
                try:
                    self.driver.find_element(By.XPATH, '//*[@id="mat-mdc-slide-toggle-1-button"]/span[2]/span/span[3]').click() # 이 컴퓨터에 저장 버튼 누르기
                    break
                except:
                    if i > 15 : 
                        assert 0
                    time.sleep(0.5)
                    i = i+1
            self.driver.maximize_window()
            self._log_to_gui("로그인 필요, QR 코드를 입력하세요")
            logger.info("로그인 필요, QR 코드를 입력하세요")
            xpath = '/html/body/mw-app/mw-bootstrap/div/main/mw-main-container/div/mw-main-nav/div/mw-fab-link/a/span[2]/div/div'
            self.wait_for_xpath(xpath)
        else:
            logger.info("자동 로그인 완료.")
            self._log_to_gui("자동 로그인 완료")
            
        i = 0
        for phone, details in data_dict.items():
            market, name, item = details
            market  = market.split('.')[1]
            message = self.template.replace("[고객명]", name).replace("[마켓]", market).replace("[상품명]", item)
            self._log_to_gui(f"[{i+1}] {name} {market} {phone}")
            logger.info(f"[{i+1}] {name} {market} {phone}")
            self.send_message(phone, message)
            i = i + 1

        logger.info(f"문자 {i}건 발송 완료")
        self._log_to_gui(f"문자 {i}건 발송 완료")
        self.driver.quit()
