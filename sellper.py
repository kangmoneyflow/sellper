import sys, os
from PyQt5.QtWidgets import *
from PyQt5 import uic
from config import *
from enum import Enum
from libcashdata import *
from PyQt5.QtCore import QThread, pyqtSignal
from dataclasses import dataclass
from util import setup_logger
logger = setup_logger(__name__)
from sellper_ui import Ui_widget
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class TYPE(Enum):
    CASH = 1
    
class SELECT(Enum):
    OPEN_N = 1
    UPDATE_MARKET = 2
    CREATE_LIST = 3
    SCRAP = 4
    DELETE = 5
    UPLOAD = 6

@dataclass
class WOKER_PARAM:
    type_: TYPE
    select_: SELECT
    param_1 : int
    param_2 : int
    market_dict : dict

config = Config()

class Worker(QThread):
    # 스레드가 완료되면 신호를 보냄
    finished = pyqtSignal()

    def __init__(self, param: WOKER_PARAM):
        super().__init__()
        self.param = param
        self.menu = {"type":param.type_, "select":param.select_}

    def run(self):
        logger.info(f"Thread 생성 후 실행 type:{self.menu['type']} select:{self.menu['select']}")
        if self.menu["select"] is SELECT.OPEN_N:
            logger.info(f"캐시데이터 실행 반복: {self.param.param_1}")
            for i in range(self.param.param_1):
                logger.info(f"  실행: {i}")
                cashdata = CashData()
                cashdata.run_cashdata()
        elif self.menu["select"] is SELECT.UPDATE_MARKET:
            dict_ = config.get_market_login_info()
            start_ = self.param.param_1 - 1
            end_ = self.param.param_2 - 1
            logger.info(f"마켓 계정 업데이트 사업자 start {self.param.param_1} - end {self.param.param_2}")
            # cashdata = CashData()
            # cashdata.run_cashdata()
            for i in range(start_, end_ + 1):
                for market in self.param.market_dict:
                    if self.param.market_dict[market] is True:
                        nickname = dict_['계정정보'][i]
                        market_id = dict_[market][i].split('\n')[0]
                        market_pw = dict_[market][i].split('\n')[1]
                        target_name = f"{i+1}번_{market}_{nickname}"
                        logger.info(f"  마켓 계정 업데이트 {target_name}")
                        # cashdata.run_update_market_info(target_name, market_pw)
        elif self.menu["select"] is SELECT.CREATE_LIST:
            dict_ = config.get_cashdata_create_sheet()
            start_ = self.param.param_1 - 2
            end_ = self.param.param_2 - 2
            cashdata = CashData()
            cashdata.run_cashdata()            
            for i in range(start_, end_ + 1):
                logger.info(f"리스트명[{i+2}] {dict_['리스트명'][i]}")
                e = [dict_['주문'][i], dict_['일치'][i], dict_['가격'][i]]
                price_type = None
                for j in range(len(e)):
                    if   j == 0: price_type="주문"
                    elif j == 1: price_type="일치"
                    elif j == 2: price_type="가격"
                    if e[j].upper() == 'X': continue
                    for price_filter in [dict_['가격필터1'][i], dict_['가격필터2'][i]]:
                        create_option ={
                            'url': dict_['URL'][i],
                            'list_name': dict_['리스트명'][i],
                            'category_name': dict_['카테고리'][i],
                            'tag_name': dict_['검색태그'][i],
                            'price_type': price_type,
                            'price_filter': price_filter,
                            'page_start': dict_['시작페이지'][i],
                            'page_end': dict_['마지막페이지'][i],
                            'num_scrap': dict_['수집개수'][i],
                            'exchange_rate': dict_['환율'][i],
                            'plus_rate': dict_['추가금액비율'][i],
                            'plus_money': dict_['추가금액'][i] 
                        }
                        cashdata.run_create_list(create_option)
        elif self.menu["select"] is SELECT.SCRAP:
            dict_ = config.get_cashdata_scrap_sheet()
            start_ = self.param.param_1 - 2
            end_ = self.param.param_2 - 2
            logger.info(f"리스트 시트 인덱스 start {self.param.param_1} - end {self.param.param_2}")
            for i in range(start_, end_ + 1):
                logger.info(f"  리스트명[{i+2}] {dict_['리스트명'][i]}")
                cashdata = CashData()
                cashdata.run_cashdata()
                cashdata.run_scrap(dict_['리스트명'][i])
        elif self.menu['select'] is SELECT.DELETE:
            pass
        elif self.menu['select'] is SELECT.UPLOAD:
            dict_ = config.get_cashdata_upload_sheet()
            login_dict = config.get_market_login_info()
            start_ = self.param.param_1 - 2
            end_ = self.param.param_2 - 2
            logger.info(f"리스트 업로드 start {self.param.param_1} - end {self.param.param_2}")
            for i in range(start_, end_ + 1):
                logger.info(f"  리스트명[{i+2}] {dict_['리스트명'][i]}")            
                cashdata = CashData()
                cashdata.run_cashdata()
                #타겟 마켓 로그인
                target_name = f"  {dict_['사업자'][i]}번_{dict_['마켓'][i]}_{login_dict['계정정보'][int(dict_['사업자'][i])-1]}"
                logger.info(target_name)
                cashdata.run_market_login(target_name)
                #리스트 검색
                target_list_name = dict_['리스트명'][i]
                logger.info(target_list_name)
                cashdata.run_upload(target_list_name)

        # 스레드 완료 신호
        self.finished.emit()

class WindowClass(QMainWindow, Ui_widget):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        
        self.menu = {"type": None, "select": None}

        # group box
        self.radioButton_open_n.clicked.connect(self.choose_menu)
        self.radioButton_update_market.clicked.connect(self.choose_menu)
        self.radioButton_create_list.clicked.connect(self.choose_menu)
        self.radioButton_run_scrap.clicked.connect(self.choose_menu)
        self.radioButton_delete_market.clicked.connect(self.choose_menu)
        self.radioButton_upload_market.clicked.connect(self.choose_menu)

        # 메인 실행 버튼
        self.pushButton_run.clicked.connect(self.run_main)

        # 백그라운드 스레드 완료 시 호출될 메서드
        self.worker = None

    def choose_menu(self):
        if self.radioButton_open_n.isChecked():
            logger.info("자동 N개 실행 선택")
            self.menu = {"type": TYPE.CASH, "select": SELECT.OPEN_N}
            self.tabWidget.setCurrentIndex(1)
        elif self.radioButton_update_market.isChecked():
            logger.info("계정 업데이트 선택")
            self.menu = {"type": TYPE.CASH, "select": SELECT.UPDATE_MARKET}
            self.tabWidget.setCurrentIndex(2)
        elif self.radioButton_create_list.isChecked():
            logger.info("수집 리스트 생성 선택")
            self.menu = {"type": TYPE.CASH, "select": SELECT.CREATE_LIST}
            self.tabWidget.setCurrentIndex(3)
        elif self.radioButton_run_scrap.isChecked():
            logger.info("수집 실행 선택")
            self.menu = {"type": TYPE.CASH, "select": SELECT.SCRAP}
            self.tabWidget.setCurrentIndex(4)
        elif self.radioButton_delete_market.isChecked():
            logger.info("연동 삭제 선택")
            self.menu = {"type": TYPE.CASH, "select": SELECT.DELETE}
            self.tabWidget.setCurrentIndex(5)
        elif self.radioButton_upload_market.isChecked():
            logger.info("업로드 선택")
            self.menu = {"type": TYPE.CASH, "select": SELECT.UPLOAD}
            self.tabWidget.setCurrentIndex(6)            

    def run_main(self):
        if not self.menu["select"] or not self.menu['type']:
            logger.info(f"작업을 선택해 주세요.: type:{self.menu['type']} select:{self.menu['select']}")
            return
        logger.info(f"실행버튼 클릭: type:{self.menu['type']} select:{self.menu['select']}")
        
        # 기존의 실행 중인 스레드가 있으면 처리하지 않음
        if self.worker is not None and self.worker.isRunning():
            logger.info("이미 실행 중인 작업이 있습니다.")
            return

        #Param 설정
        param = WOKER_PARAM(
            type_=self.menu['type'], 
            select_=self.menu['select'],
            param_1 = 99,
            param_2 = 99,
            market_dict = {"스마트스토어":False, "쿠팡":False, "지마켓":False, "옥션":False, "11번가":False, "롯데온":False}
        )
        
        if self.menu['type'] is TYPE.CASH and self.menu["select"] is SELECT.OPEN_N:
            param.param_1 = self.sel_1_num.value()
        elif self.menu['type'] is TYPE.CASH and self.menu["select"] is SELECT.UPDATE_MARKET:    
            param.param_1 = self.sel_2_start.value()
            param.param_2 = self.sel_2_end.value()
            if self.checkBox_ss.isChecked():
                param.market_dict["스마트스토어"] = True
            if self.checkBox_cp.isChecked():
                param.market_dict["쿠팡"] = True
            if self.checkBox_g.isChecked():
                param.market_dict["지마켓"] = True
            if self.checkBox_a.isChecked():
                param.market_dict["옥션"] = True
            if self.checkBox_st11.isChecked():
                param.market_dict["11번가"] = True                                                
            if self.checkBox_l.isChecked():
                param.market_dict["롯데온"] = True                 
        elif self.menu['type'] is TYPE.CASH and self.menu["select"] is SELECT.CREATE_LIST:   
            param.param_1 = self.sel_3_start.value()
            param.param_2 = self.sel_3_end.value()                                                            
        elif self.menu['type'] is TYPE.CASH and self.menu["select"] is SELECT.SCRAP:
            param.param_1 = self.sel_4_start.value()
            param.param_2 = self.sel_4_end.value()
        elif self.menu['type'] is TYPE.CASH and self.menu["select"] is SELECT.UPLOAD:
            param.param_1 = self.sel_6_start.value()
            param.param_2 = self.sel_6_end.value()

        logger.info(f"param1 {param.param_1} param2 {param.param_2} market_dict {param.market_dict}")

        # 새로운 스레드를 시작하여 작업 실행
        self.worker = Worker(param)
        self.worker.finished.connect(self.on_worker_finished)
        self.worker.start()

    def on_worker_finished(self):
        logger.info("작업이 완료되었습니다.")
        QMessageBox.information(self, "작업 완료", "작업이 성공적으로 완료되었습니다.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = WindowClass()
    myWindow.show()
    app.exec_()
