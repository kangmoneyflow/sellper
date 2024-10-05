import sys, os
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QThread, pyqtSignal
from config import Config
from enum import Enum
from libcashdata import *
from dataclasses import dataclass
from util import setup_logger
from sellper_ui import Ui_widget

logger = setup_logger(__name__)
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
class WORKER_PARAM:
    type_: TYPE
    select_: SELECT
    param_1: int
    param_2: int
    market_dict: dict

config = Config()

class Worker(QThread):
    finished = pyqtSignal()

    def __init__(self, param: WORKER_PARAM):
        super().__init__()
        self.param = param
        self.menu = {"type": param.type_, "select": param.select_}

    def run(self):
        logger.info(f"Thread 실행: type:{self.menu['type']} select:{self.menu['select']}")
        if self.menu["select"] is SELECT.OPEN_N:
            self._run_open_n()
        elif self.menu["select"] is SELECT.UPDATE_MARKET:
            self._update_market_info()
        elif self.menu["select"] is SELECT.CREATE_LIST:
            self._create_list()
        elif self.menu["select"] is SELECT.SCRAP:
            self._run_scrap()
        elif self.menu['select'] is SELECT.DELETE:
            self._delete()
        elif self.menu["select"] is SELECT.UPLOAD:
            self._upload_list()
        self.finished.emit()

    def _run_open_n(self):
        logger.info(f"캐시데이터 실행 반복: {self.param.param_1}")
        for i in range(self.param.param_1):
            logger.info(f"  실행: {i}")
            cashdata = CashData()
            cashdata.run_cashdata()

    def _update_market_info(self):
        dict_ = config.get_market_login_info()
        start_ = self.param.param_1 - 1
        end_ = self.param.param_2 - 1
        logger.info(f"마켓 계정 업데이트 사업자 시작: {self.param.param_1} - 종료: {self.param.param_2}")
        cashdata = CashData()
        cashdata.run_cashdata()        
        for i in range(start_, end_ + 1):
            for market in self.param.market_dict:
                if self.param.market_dict[market]:
                    nickname = dict_['계정정보'][i]
                    market_id, market_pw = dict_[market][i].split('\n')
                    target_name = f"{i+1}번_{market}_{nickname}"
                    logger.info(f"  마켓 계정 업데이트: {target_name} {market_id} {market_pw}")
                    cashdata.run_update_market_info(target_name, market_pw)

    def _create_list(self):
        dict_ = config.get_cashdata_create_sheet()
        start_ = self.param.param_1 - 2
        end_ = self.param.param_2 - 2
        cashdata = CashData()
        cashdata.run_cashdata()           
        logger.info(f"수집리스트 생성 시작: {self.param.param_1} - 종료: {self.param.param_2}")
        for i in range(start_, end_ + 1):
            logger.info(f"  [{i+2}] {dict_['리스트명'][i]}")
            price_types = ['주문', '일치', '가격']
            for j in range(len(price_types)):
                price_type = price_types[j]
                if dict_[price_type][i].upper() == 'X': continue
                create_option = {
                    'url': dict_['URL'][i],
                    'list_name': dict_['리스트명'][i],
                    'category_name': dict_['카테고리'][i],
                    'tag_name': dict_['검색태그'][i],
                    'price_type': price_type,
                    'price_filter': dict_['가격필터'][i],
                    'page_start': dict_['시작페이지'][i],
                    'page_end': dict_['마지막페이지'][i],
                    'num_scrap': dict_['수집개수'][i],
                    'exchange_rate': dict_['환율'][i],
                    'plus_rate': dict_['추가금액비율'][i],
                    'plus_money': dict_['추가금액'][i]
                }
                logger.info(f"  생성옵션: {create_option}")
                cashdata.run_create_list(create_option)

    def _run_scrap(self):
        dict_ = config.get_cashdata_scrap_sheet()
        start_ = self.param.param_1 - 2
        end_ = self.param.param_2 - 2
        logger.info(f"자동수집 시작: {start_} - 종료: {end_}")
        for i in range(start_, end_ + 1):
            logger.info(f"  스프레드시트[{i+2}] {dict_['리스트명'][i]}")
            cashdata = CashData()
            cashdata.run_cashdata()
            cashdata.run_scrap(dict_['리스트명'][i])

    def _delete(self):
        logger.info("삭제: 현재 제공하지 않는 기능")

    def _upload_list(self):
        dict_ = config.get_cashdata_upload_sheet()
        login_dict = config.get_market_login_info()
        start_ = self.param.param_1 - 2
        end_ = self.param.param_2 - 2
        logger.info(f"자동 업로드 시작: {self.param.param_1} - 종료: {self.param.param_2}")
        for i in range(start_, end_ + 1):
            cashdata = CashData()
            cashdata.run_cashdata()
            target_name = f"{dict_['사업자'][i]}번_{dict_['마켓'][i]}_{login_dict['계정정보'][int(dict_['사업자'][i])-1]}"
            logger.info(f"  로그인: {target_name}")            
            cashdata.run_market_login(target_name)
            target_list_name = f"{dict_['리스트명'][i]}"
            logger.info(f"  스프레드시트[{i+2}] {target_list_name}")                        
            cashdata.run_upload(target_list_name)

class WindowClass(QMainWindow, Ui_widget):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.menu = {"type": None, "select": None}

        # 라디오 버튼 이벤트 연결
        self._connect_radio_buttons()
        self.pushButton_run.clicked.connect(self.run_main)
        self.worker = None

    def _connect_radio_buttons(self):
        self.radioButton_open_n.clicked.connect(self.choose_menu)
        self.radioButton_update_market.clicked.connect(self.choose_menu)
        self.radioButton_create_list.clicked.connect(self.choose_menu)
        self.radioButton_run_scrap.clicked.connect(self.choose_menu)
        self.radioButton_delete_market.clicked.connect(self.choose_menu)
        self.radioButton_upload_market.clicked.connect(self.choose_menu)

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

        if self.worker is not None and self.worker.isRunning():
            logger.info("이미 실행 중인 작업이 있습니다.")
            return

        param = self._create_param()
        logger.info(f"실행 준비: param1 {param.param_1}, param2 {param.param_2}, market_dict {param.market_dict}")
        self.worker = Worker(param)
        self.worker.finished.connect(self.on_worker_finished)
        self.worker.start()

    def _create_param(self):
        param = WORKER_PARAM(
            type_=self.menu['type'],
            select_=self.menu['select'],
            param_1=99,
            param_2=99,
            market_dict={"스마트스토어": False, "쿠팡": False, "지마켓": False, "옥션": False, "11번가": False, "롯데온": False}
        )

        if self.menu["select"] is SELECT.OPEN_N:
            param.param_1 = self.sel_1_num.value()
        elif self.menu["select"] is SELECT.UPDATE_MARKET:
            param.param_1 = self.sel_2_start.value()
            param.param_2 = self.sel_2_end.value()
            self._update_market_dict(param)
        elif self.menu["select"] in {SELECT.CREATE_LIST, SELECT.SCRAP, SELECT.UPLOAD}:
            param.param_1 = getattr(self, f"sel_{self.menu['select'].value}_start").value()
            param.param_2 = getattr(self, f"sel_{self.menu['select'].value}_end").value()

        return param

    def _update_market_dict(self, param):
        param.market_dict["스마트스토어"] = self.checkBox_ss.isChecked()
        param.market_dict["쿠팡"] = self.checkBox_cp.isChecked()
        param.market_dict["지마켓"] = self.checkBox_g.isChecked()
        param.market_dict["옥션"] = self.checkBox_a.isChecked()
        param.market_dict["11번가"] = self.checkBox_st11.isChecked()
        param.market_dict["롯데온"] = self.checkBox_l.isChecked()

    def on_worker_finished(self):
        logger.info("작업이 완료되었습니다.")
        QMessageBox.information(self, "작업 완료", "작업이 성공적으로 완료되었습니다.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = WindowClass()
    myWindow.show()
    app.exec_()
