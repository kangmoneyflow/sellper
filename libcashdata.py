import os
import time
import pyautogui
import pyperclip
from pywinauto import findwindows, application
from config import Config
from util import setup_logger

logger = setup_logger(__name__)

TIME_DELAY_1 = 1
TIME_DELAY_2 = 2
TIME_DELAY_5 = 5
TIME_DELAY_10 = 10

class CashData:
    def __init__(self):
        self.config = Config()
        self.run_path = self.config.config_data['cashdata']['path']
        self.app = None

    def run_cashdata(self):
        logger.info(f"Cashdata 실행: {self.run_path}")
        os.system(self.run_path)
        time.sleep(TIME_DELAY_2)

        proc_pid = self._get_pid()
        logger.info(f"Cashdata PID: {proc_pid}")
        if not proc_pid:
            raise Exception("Cashdata 프로세스를 찾을 수 없습니다.")
        
        logger.info("Cashdata Login 버튼 클릭")
        self._login_click(proc_pid)

        proc_name = self._find_procname_with_pid(proc_pid)
        logger.info(f"Cashdata 프로세스 이름: {proc_name}")
        if not proc_name:
            raise Exception("프로세스 이름을 찾을 수 없습니다.")

        self.app = self._connect_app(proc_pid, proc_name)
        return self.app

    def _get_curr_process(self):
        return findwindows.find_elements()

    def _get_pid(self):
        for _ in range(10):
            time.sleep(TIME_DELAY_2)
            procs = self._get_curr_process()
            for proc in procs:
                if "로그인" in proc.name:
                    return proc.process_id
        return None

    def _login_click(self, pid):
        app = application.Application(backend="uia")
        app.connect(process=pid)
        dlg = app['로그인']
        login_wrap = dlg.child_window(title="로그인", control_type="Button").wrapper_object()
        login_wrap.click()
        time.sleep(TIME_DELAY_5)

    def _find_procname_with_pid(self, pid):
        for _ in range(10):
            time.sleep(TIME_DELAY_2)
            procs = self._get_curr_process()
            for proc in procs:
                if pid == proc.process_id and str(pid) in proc.name:
                    logger.info(f"프로세스 이름: {proc.name}")
                    return proc.name
        return None
    
    def _connect_app(self, proc_pid, proc_name):
        app = application.Application(backend="uia")
        app.connect(process=proc_pid)
        dlg = app[proc_name]
        dlg.child_window(auto_id="base", control_type="Custom").wrapper_object().type_keys("{ESC}")
        time.sleep(TIME_DELAY_2)
        try:
            dlg.child_window(title="", control_type="Button").wrapper_object().click_input()
            time.sleep(TIME_DELAY_2)
        except Exception:
            pass
        return app

    
    def click_menu(self, num):
        logger.info(f"Click menu num : {num}")
        obj = self.app.dlg.child_window(
            title="CashData.Client.MVVM.ModelMenuItem",
            control_type="MenuItem",
            found_index=num  
            # 인덱스로 정확한 항목을 지정, 0=사이트이동, 1=사이트설정, 2=리스트관리, 3=도구
            # 인덱스로 정확한 항목을 지정, 0=상품수집, 1=상품대기, 2=상품관리, 3=카테고리설정
            # 인덱스로 정확한 항목을 지정, 0=업로드리스트, 1=업로드API, 2=단어관리
        ).wrapper_object()
        obj.click_input()
        time.sleep(TIME_DELAY_2)

    def click_scrapping_list(self):
        logger.info("Click 상품수집")
        self.click_menu(2) # 메인화면 리스트관리 클릭(2)
        self.click_menu(0) # 메인화면 리스트관리 클릭(2) -> 상품수집 클릭(0)

    def click_wait_list(self):
        logger.info("Click 상품대기")
        pyautogui.press('esc')
        self.click_menu(2) # 메인화면 리스트관리 클릭(2)
        self.click_menu(1) # 메인화면 리스트관리 클릭(2) -> 상품대기 클릭(1)

    def click_prod_mgmt(self):
        logger.info("Click 상품관리")
        self.click_menu(2) # 메인화면 리스트관리 클릭(2)
        self.click_menu(2) # 메인화면 리스트관리 클릭(2) -> 상품관리 클릭(2)

    def click_upload_list(self):
        logger.info("Click 업로드리스트")
        self.click_menu(2) # 메인화면 리스트관리 클릭(2)
        self.click_menu(2) # 메인화면 리스트관리 클릭(2) -> 상품관리 클릭(2)
        self.click_menu(0) # 메인화면 리스트관리 클릭(2) -> 상품관리 클릭(2) -> 업로드리스트 클릭(0)
    
    def click_login_list(self):
        logger.info("Click 로그인리스트")
        self.click_menu(1) #사이트설정
        self.click_menu(1) #업로드사이트
        self.click_menu(0) #로그인        
    
    def click_check_box(self, type):
        if type == 0: # True -> False
            try:
                #체크 박스 클릭해서 전체 수집리스트 True -> False로 변경
                self.app.dlg.child_window(title="System.Windows.Controls.CheckBox Content: IsChecked:True", control_type="HeaderItem").wrapper_object().click_input()
            except:
                try:
                    #체크 박스 클릭해서 전체 수집리스트 True -> False로 변경
                    self.app.dlg.child_window(title="System.Windows.Controls.CheckBox Content: IsChecked:null", control_type="HeaderItem").wrapper_object().click_input() 
                except:
                    pass
        else: #False -> True
            try:
                self.app.dlg.child_window(title="System.Windows.Controls.CheckBox Content: IsChecked:False", control_type="HeaderItem").wrapper_object().click_input()
            except:
                pass                    

    def click_login_row_checkbox(self, num, is_click=False):
        obj = self.app.dlg.child_window(
            title="항목: CashData.Client.MVVM.EMain.ModelUploadMarketSetting, 열 표시 인덱스: 0", #0=체크박스 1=메뉴 2=승인 3=마켓 4=메모 5=아이디 6=메시지
            control_type="Custom",
            found_index=0
        ).wrapper_object() #로그인 버튼 누르는 것임 
        obj.set_focus()
        if is_click is True:
            obj.click_input()        
        pyautogui.press('tab', num)
        pyautogui.press('space')   
        time.sleep(TIME_DELAY_2)     

    def click_list_row_checkbox(self, num, is_click=False):
        obj = self.app.dlg.child_window(
            title="항목: CashData.Client.MVVM.EMain.ModelMemberCategoryRegistration, 열 표시 인덱스: 0",
            control_type="Custom",
            found_index=0
        ).wrapper_object() #로그인 버튼 누르는 것임 
        obj.set_focus()
        if is_click is True:
            obj.click_input()        
        pyautogui.press('tab', num)
        pyautogui.press('space')   
        time.sleep(TIME_DELAY_2)     

    def click_category_title(self, num, is_double_click=False):
        obj = self.app.dlg.child_window(
            title="항목: CashData.Client.MVVM.EMain.ModelMemberCategoryRegistration, 열 표시 인덱스: 2", 
            control_type="Custom",
            found_index=0
        ).wrapper_object()
        if  is_double_click is True:
            obj.double_click_input() 
        else:        
            obj.click_input()
            for i in range(int(num)):
                pyautogui.hotkey('shift','tab')
        time.sleep(TIME_DELAY_2)

    def click_search_text(self):
        logger.info("Click 검색 탭")
        obj = self.app.dlg.child_window(auto_id="Filter", control_type="Edit").wrapper_object() #검색란 클릭
        obj.click_input()
        time.sleep(TIME_DELAY_2)
    
    def click_search_button(self):
        logger.info("Click 검색 버튼")
        obj = self.app.dlg.child_window(title="검색", control_type="Button").wrapper_object() #검색 버튼 누르기
        obj.click_input()
        time.sleep(TIME_DELAY_2)

    def click_scrap_button(self):
        logger.info("Click 선택 수집")
        obj = self.app.dlg.child_window(title=" 선택 수집", control_type="Text").wrapper_object()
        obj.click_input() #선택 수집 클릭
        time.sleep(TIME_DELAY_2)        

    def click_start(self):
        logger.info("Click 시작")
        obj = self.app.dlg.child_window(title="시작", control_type="Text").wrapper_object()
        obj.click_input()    
        time.sleep(TIME_DELAY_2)
    
    def click_apply(self):
        logger.info("Click 적용")
        self.app.dlg.child_window(title="적용", auto_id="buttonApply", control_type="Button").wrapper_object().click_input()            

    def click_sccuess(self):
        logger.info("Click 완료")
        self.app.dlg.child_window(title="완료", control_type="Text").wrapper_object().click_input()

    def update_market_pw(self, pw):
        self.app.dlg.child_window(title="비밀번호를 입력해주세요.", control_type="Text").wrapper_object().click_input()
        pyperclip.copy(pw)
        time.sleep(TIME_DELAY_1)
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(TIME_DELAY_1)
        self.app.dlg.child_window(title="비밀번호 확인을 입력해주세요.", control_type="Text").wrapper_object().click_input()
        pyperclip.copy(pw)
        time.sleep(TIME_DELAY_1)
        pyautogui.hotkey('ctrl', 'v')            
        time.sleep(TIME_DELAY_1)
        self.click_apply()
        time.sleep(TIME_DELAY_10)

    def change_item_num(self, num=5):
        #보기 상품 개수 1개 -> 1만개로 수정
        obj = self.app.dlg.child_window(auto_id="comboBox", control_type="ComboBox").wrapper_object()
        obj.click_input()
        time.sleep(TIME_DELAY_1)
        obj.click_input()
        time.sleep(TIME_DELAY_1)
        pyautogui.press('tab')
        pyautogui.press('down', num)
        time.sleep(TIME_DELAY_1)        

    def remove_curr_text(self):
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(TIME_DELAY_1)
        pyautogui.hotkey('backspace')
        time.sleep(TIME_DELAY_1)

    def copy_and_paste(self, text):
        text = text.strip()
        pyperclip.copy(text)
        time.sleep(TIME_DELAY_1)
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(TIME_DELAY_1)

    def run_market_login(self, target_name):
        self.click_login_list() #로그인창 누르기
        self.click_check_box(0) #로그인 체크박스 전체 해제        
        self.click_search_text()
        self.remove_curr_text()
        self.copy_and_paste(target_name)
        self.click_search_button()              
        self.click_login_row_checkbox(0, True) #앞에 로그인할 대상 클릭
        self.click_login_row_checkbox(2) #로그인 버튼 클릭
        time.sleep(TIME_DELAY_5)
        self.click_sccuess()
        time.sleep(TIME_DELAY_1)

    def run_update_market_info(self, target_name, pw):
        self.click_login_list() #로그인창 누르기
        self.click_check_box(0) #로그인 체크박스 전체 해제
        self.click_search_text()
        self.remove_curr_text()
        self.copy_and_paste(target_name)
        self.click_search_button()        
        time.sleep(TIME_DELAY_2)
        self.click_login_row_checkbox(2) #로그인 비번 넣는 곳 클릭
        self.update_market_pw(pw)
        time.sleep(TIME_DELAY_2)
        pyautogui.press('esc')
        time.sleep(TIME_DELAY_1)

    def run_create_list(self, create_option):
        logger.info(f"run_create_list : {create_option}")
        self.click_scrapping_list() #수집 리스트로 이동
        time.sleep(TIME_DELAY_2)
        self.click_search_text()
        self.remove_curr_text()
        self.copy_and_paste("샘플")
        self.click_search_button()              
        self.click_list_row_checkbox(3) #복사 버튼 누르기 
        time.sleep(TIME_DELAY_2)

        pyautogui.press('tab', 11) #11번 tab 이동하면, 수집 url 입니다. 창 시작함
        self.remove_curr_text()
        url = create_option['url']
        if create_option['price_type'] == "주문":
            url = f"{url}?g=y&sortType=total_tranpro_desc"
        self.copy_and_paste(url)

        self.app.dlg.child_window(title="수집 이름을 설정해주세요.", control_type="Text").wrapper_object().click_input()
        self.remove_curr_text()
        list_name = create_option['list_name']
        tmp = create_option['price_filter']
        list_name = f"{list_name}{tmp}/{create_option['price_type']}"
        self.copy_and_paste(list_name)

        pyautogui.press('tab', 1) #통합 카테고리 (업로드 시 적용)
        pyautogui.press('space') #카테고리 검색
        time.sleep(TIME_DELAY_1)
        self.click_category_title(num=11, is_double_click=False) #검색창으로 이동
        self.remove_curr_text()
        self.copy_and_paste(create_option['category_name'])
        pyautogui.press('enter') #검색 버튼 대신 엔터로 검색 진행
        time.sleep(TIME_DELAY_1)
        self.click_category_title(num=0, is_double_click=True) #최상단에 검색된 카테고리 더블클릭 

        page_start = create_option['page_start']
        page_end = create_option['page_end']
        limit_num = create_option['num_scrap']
        self.app.dlg.child_window(title="시작 페이지 입력 바랍니다.", control_type="Text").wrapper_object().click_input()
        self.remove_curr_text()
        self.copy_and_paste(page_start)
        self.app.dlg.child_window(title="마지막 페이지 입력 바랍니다.", control_type="Text").wrapper_object().click_input()
        self.remove_curr_text()
        self.copy_and_paste(page_end)        
        #수량옵션
        obj = self.app.dlg.child_window(title="수집 될 상품의 수량을 입력 바랍니다.(입력을 안할 시 페이지 수만큼 수집)", control_type="Text").wrapper_object()
        obj.click_input()
        self.remove_curr_text()
        self.copy_and_paste(limit_num)         

        # Step 5-1. 가격필터
        pyautogui.press('tab', 2) #가격 필터 부분으로 이동
        price_row = ""
        price_high = ""
        price_interval = ""
        if create_option['price_filter'] != "-": 
            price_row, price_high = create_option['price_filter'].split('to')
            price_interval = int((int(price_high)-int(price_row)))//2
        self.remove_curr_text()
        self.copy_and_paste(price_row)         
        pyautogui.press('tab', 1)
        self.remove_curr_text()
        self.copy_and_paste(price_high)         
        pyautogui.press('tab', 1)
        self.remove_curr_text()
        self.copy_and_paste(str(price_interval))

        # Step 6. 환율 설정 (전체 적용) # 적용하지 않음. 기본 셋팅 됨
        pyautogui.press('tab', 1) #환율 탭으로 이동
        self.remove_curr_text()
        self.copy_and_paste(create_option['exchange_rate']) #환율 입력 

        pyautogui.press('tab', 1) #추가금액비율으로 이동
        self.remove_curr_text()
        self.copy_and_paste("1."+create_option['plus_rate']) #환율 입력 

        pyautogui.press('tab', 1) #추가금액으로 이동
        self.remove_curr_text()
        self.copy_and_paste(create_option['plus_money']) #환율 입력 


        # Step 7. 배송 (업로드 시 적용) # 적용하지 않음. 기본 셋팅 됨
        pyautogui.press('tab', 20) #맨 밑으로 이동
        
        #태그 입력
        self.app.dlg.child_window(title="키워드를 입력해주세요.키워는 (,)구분 합니다.", control_type="Text").wrapper_object().click_input()
        self.remove_curr_text()
        self.copy_and_paste(create_option['tag_name']) #태그 입력

        # Step 8-2 제목 앞 추가 단어를 입력하세요.
        pyautogui.press('tab', 2) 
        # self.remove_curr_text()
        # self.copy_and_paste(create_option['tag_name']) #태그 입력

        #수집리스트 복사 완료 버튼
        self.app.dlg.child_window(title="복사", control_type="Text").wrapper_object().click_input()
        time.sleep(TIME_DELAY_2)

    def run_scrap(self, target_list_name):
        self.click_scrapping_list()
        time.sleep(TIME_DELAY_2)
        self.click_check_box(0) # 체크박스 전체 해제 
        time.sleep(TIME_DELAY_2)
        self.click_search_text()
        pyperclip.copy(target_list_name)
        logger.info(f"검색어 {target_list_name}")
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(TIME_DELAY_2)
        self.click_search_button()
        self.click_check_box(1) # 체크박스 전체 선택
        self.click_scrap_button()
        try:
            obj = self.app.dlg.child_window(title="아니요(N)", auto_id="7", control_type="Button").wrapper_object()
            obj.click_input()
        except: 
            pass # 처음 수집하는 경우일 수 있음
        time.sleep(TIME_DELAY_2)
        self.click_start()
        time.sleep(TIME_DELAY_2)
        

    def run_delete(self, market):
        pass

    def run_upload(self, target_list_name):
        self.click_wait_list()
        time.sleep(TIME_DELAY_2)
        self.change_item_num()
        self.click_search_text()
        pyperclip.copy(target_list_name)
        logger.info(f"검색어 {target_list_name}")
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(TIME_DELAY_2)        
        self.click_search_button()