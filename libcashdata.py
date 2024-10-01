from pywinauto import findwindows
from pywinauto import application
import pyautogui
import time
# for data processing
import pandas as pd
# information
import os
import datetime
import logging
import sys
import pyperclip

import json
from oauth2client.service_account import ServiceAccountCredentials
import gspread
import pandas as pd

from config import *

TIME_DELAY_2 = 2
TIME_DELAY_5 = 5

class CashData():
    def __init__(self):
        self.config = Config()
        self.run_path = self.config.config_data['cashdata']['path']
        self.open_num = 1
        self.app = None

    def run_cashdata(self):
        #프로그램 실행
        os.system(self.run_path)
        time.sleep(TIME_DELAY_2)
        #process pid 값 가져오기
        proc_pid = self.get_pid()
        if proc_pid is None:
            assert 0
        #로그인 버튼 누르기 
        self.login_click(proc_pid)
        #pid <-> proc name 연결
        proc_name = self.find_procname_with_pid(proc_pid)
        if proc_name is None:
            assert 0
        #app 연결
        self.app = self.connect_app(proc_pid, proc_name)
        return self.app

    def get_curr_process(self):
        return findwindows.find_elements()

    def get_pid(self):
        i=0
        while True:
            if i == 10:
                break
            i = i + 1
            time.sleep(TIME_DELAY_2)
            procs = self.get_curr_process()
            for proc in procs:
                if "로그인" in proc.name:
                    pid = proc.process_id
                    print(f"캐시데이터 pid={pid}")
                    return pid
        return None

    def login_click(self, pid):
        app = application.Application(backend="uia")
        app.connect(process=pid)
        dlg = app['로그인']
        login_wrap = dlg.child_window(title="로그인", control_type="Button").wrapper_object()
        login_wrap.click()
        time.sleep(TIME_DELAY_5)

    def find_procname_with_pid(self, pid):
        # 로그인 되어 있는 캐시 창에서 메뉴 창 보고 pid와 id 매칭 dict 만들기 
        i=0 
        while True:
            if i == 10:
                break
            i = i + 1
            time.sleep(TIME_DELAY_2)
            procs = self.get_curr_process()
            for proc in procs:
                if pid == proc.process_id and str(pid) in proc.name:            
                    a = "{} / {}".format(proc.name, proc.process_id)
                    print(a)
                    return proc.name
        return None

    def connect_app(self, proc_pid, proc_name):
        app = application.Application(backend="uia")
        app.connect(process = proc_pid)
        dlg = app[proc_name] #다이얼로그 접속

        obj = dlg.child_window(auto_id="base", control_type="Custom").wrapper_object() #처음에 로그인하면, 뜨는 업로드 마켓 로그인 obj
        obj.type_keys("{ESC}") #esc 누르면 꺼짐
        time.sleep(TIME_DELAY_2)
        try:
            obj = dlg.child_window(title="", control_type="Button").wrapper_object() # 캐시창 최대화 버튼, # ['\ue922Button', 'Button4', '\ue922', '\ue9220', '\ue9221']
            obj.click_input() #캐시창 최대화
            time.sleep(TIME_DELAY_2)
        except:
            pass
        return app
    
    def click_menu(self, num):
        obj_dlg_management = self.app.dlg.child_window(
            title="CashData.Client.MVVM.ModelMenuItem",
            control_type="MenuItem",
            found_index=num  
            # 인덱스로 정확한 항목을 지정, 0=사이트이동, 1=사이트설정, 2=리스트관리, 3=도구
            # 인덱스로 정확한 항목을 지정, 0=상품수집, 1=상품대기, 2=상품관리, 3=카테고리설정
            # 인덱스로 정확한 항목을 지정, 0=업로드리스트, 1=업로드API, 2=단어관리
        ).wrapper_object()
        obj_dlg_management.click_input()
        time.sleep(TIME_DELAY_2)

    def click_scrapping_list(self):
        self.click_menu(2) # 메인화면 리스트관리 클릭(2)
        self.click_menu(0) # 메인화면 리스트관리 클릭(2) -> 상품수집 클릭(0)

    def click_wait_list(self):
        self.click_menu(2) # 메인화면 리스트관리 클릭(2)
        self.click_menu(1) # 메인화면 리스트관리 클릭(2) -> 상품대기 클릭(1)

    def click_prod_mgmt(self):
        self.click_menu(2) # 메인화면 리스트관리 클릭(2)
        self.click_menu(2) # 메인화면 리스트관리 클릭(2) -> 상품관리 클릭(2)

    def click_upload_list(self):
        self.click_menu(2) # 메인화면 리스트관리 클릭(2)
        self.click_menu(2) # 메인화면 리스트관리 클릭(2) -> 상품관리 클릭(2)
        self.click_menu(0) # 메인화면 리스트관리 클릭(2) -> 상품관리 클릭(2) -> 업로드리스트 클릭(0)
    
    def click_check_box(self, type):
        if type == 0: # True -> False
            try:
                obj_dlg_all_click = self.app.dlg.child_window(title="System.Windows.Controls.CheckBox Content: IsChecked:True", control_type="HeaderItem").wrapper_object()
                obj_dlg_all_click.click_input() #체크 박스 클릭해서 전체 수집리스트 True -> False로 변경
            except:
                try:
                    obj_dlg_all_click = self.app.dlg.child_window(title="System.Windows.Controls.CheckBox Content: IsChecked:null", control_type="HeaderItem").wrapper_object()
                    obj_dlg_all_click.click_input() #체크 박스 클릭해서 전체 수집리스트 True -> False로 변경
                except:
                    pass
        else: #False -> True
            try:
                obj_dlg_all_click = self.app.dlg.child_window(title="System.Windows.Controls.CheckBox Content: IsChecked:False", control_type="HeaderItem").wrapper_object()
                obj_dlg_all_click.click_input() #체크 박스 클릭해서 전체 수집리스트 클릭 Falst -> True로 변경
            except:
                pass                    

    def click_search_text(self):
        obj = self.app.dlg.child_window(auto_id="Filter", control_type="Edit").wrapper_object() #검색란 클릭
        obj.click_input()
        time.sleep(TIME_DELAY_2)
    
    def click_search_button(self):
        obj = self.app.dlg.child_window(title="검색", control_type="Button").wrapper_object() #검색 버튼 누르기
        obj.click_input()
        time.sleep(TIME_DELAY_2)

    def click_scrap_button(self):
        obj = self.app.dlg.child_window(title=" 선택 수집", control_type="Text").wrapper_object()
        obj.click_input() #선택 수집 클릭
        time.sleep(TIME_DELAY_2)        

    def click_start(self):
        obj = self.app.dlg.child_window(title="시작", control_type="Text").wrapper_object()
        obj.click_input()    
        time.sleep(TIME_DELAY_2)

    def run_scrap(self, target_list_name):
        self.click_scrapping_list()
        time.sleep(TIME_DELAY_2)
        self.click_check_box(0) # 체크박스 전체 해제 
        time.sleep(TIME_DELAY_2)
        self.click_search_text()
        pyperclip.copy(target_list_name)
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
        

    def run_upload(self, target_list_name):
        self.click_upload_list()
        time.sleep(TIME_DELAY_2)