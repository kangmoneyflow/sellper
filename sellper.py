
import sys, os
from typing import Optional
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import *
from config import Config
from enum import Enum
from libcashdata import CashData
from dataclasses import dataclass
from util import setup_logger
from sellper_ui import Ui_widget
from liblogin import LOGIN
from utilfile import ExcelHandler
from sendtext import MessageSender
import resources_rc

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
    TEXT = 7
    FAKE = 8
    POST = 9

@dataclass
class WORKER_PARAM:
    type_: TYPE
    select_: SELECT
    param_1: int = 0
    param_2: int = 0
    market_dict: dict = None
    file_path: str = None
    text_edit_log: Optional[QTextEdit] = None  # QTextEdit 타입 지정

config = Config()

class Worker(QThread):
    finished = pyqtSignal()

    def __init__(self, param: WORKER_PARAM):
        super().__init__()
        self.param = param
        self.menu = {"type": param.type_, "select": param.select_}

    def run(self):
        logger.info(f"Thread 실행: type:{self.menu['type']} select:{self.menu['select']}")
        select_action = {
            SELECT.OPEN_N: self._run_open_n,
            SELECT.UPDATE_MARKET: self._update_market_info,
            SELECT.CREATE_LIST: self._create_list,
            SELECT.SCRAP: self._run_scrap,
            SELECT.DELETE: self._delete,
            SELECT.UPLOAD: self._upload_list,
            SELECT.TEXT: self._send_text
        }
        action = select_action.get(self.menu["select"])
        if action: action()
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
                    target_name = f"{market}_{nickname}"
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
            # price_types = ['주문', '일치', '가격']
            # for j in range(len(price_types)):
                # price_type = price_types[j]
                # if dict_[price_type][i].upper() == 'X': continue
            create_option = {
                'url': dict_['URL'][i],
                'list_name': dict_['리스트명'][i],
                'category_name': dict_['카테고리'][i],
                'tag_name': dict_['검색태그'][i],
                # 'price_type': price_type,
                'price_filter_isuse': dict_['가격필터사용'][i],
                'price_filter_start': dict_['가격필터-시작'][i],
                'price_filter_end': dict_['가격필터-끝'][i],
                'price_filter_inc': dict_['가격필터-증가'][i],
                'page_start': dict_['시작페이지'][i],
                'page_end': dict_['마지막페이지'][i],
                'num_scrap': dict_['수량옵션'][i],
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
        dict_ = config.get_market_login_info()
        start_ = self.param.param_1 - 1
        end_ = self.param.param_2 - 1
        logger.info(f"연동 삭제 사업자 시작: {self.param.param_1} - 종료: {self.param.param_2}")
        
        for i in range(start_, end_ + 1):
            for market in self.param.market_dict:
                if self.param.market_dict[market]:
                    cashdata = CashData()
                    cashdata.run_cashdata()
                    nickname = dict_['계정정보'][i]
                    market_id, market_pw = dict_[market][i].split('\n')
                    target_name = f"{market}_{nickname}"
                    logger.info(f"  로그인: {target_name}") 
                    cashdata.run_market_login(target_name)
                    cashdata.run_delete(market, market_id)

    def _upload_list(self):
        dict_ = config.get_cashdata_upload_sheet()
        login_dict = config.get_market_login_info()
        start_ = self.param.param_1 - 2
        end_ = self.param.param_2 - 2
        logger.info(f"자동 업로드 시작: {self.param.param_1} - 종료: {self.param.param_2}")
        for i in range(start_, end_ + 1):
            cashdata = CashData()
            cashdata.run_cashdata()
            nicknmae = login_dict['계정정보'][int(dict_['사업자'][i])-1]
            market = dict_['마켓'][i]
            target_name = f"{market}_{nicknmae}"
            logger.info(f"  로그인: {target_name}")            
            cashdata.run_market_login(target_name)
            target_list_name = f"{dict_['리스트명'][i]}"
            logger.info(f"  스프레드시트[{i+2}] {target_list_name}")                        
            cashdata.run_upload(target_list_name)
    
    def _send_text(self):
        logger.info(f"파일 경로: {self.param.file_path}")
        excel_handler = ExcelHandler(filepath=self.param.file_path)
        if not excel_handler.ws:
            logger.info("워크북 로드 실패 또는 시트가 존재하지 않습니다.")
            return
        data_dict = {}
        for row in excel_handler.ws.iter_rows(min_row=2, values_only=True):  # 첫 행은 헤더로 처리
            logger.info(f"{row}")
            passport, mall, setter, setter_phone, getter, getter_phone, item = row
            if passport != "": continue
            if setter_phone not in data_dict:
                data_dict[setter_phone] = [mall, setter, item]
            if getter_phone not in data_dict:
                data_dict[getter_phone] = [mall, getter, item]

        user_data_path = "./message"
        user_data_path = os.path.abspath(user_data_path)
        sender = MessageSender(user_data_path, self.param.text_edit_log)
        sender.send_messages_to_all(data_dict)   


class WindowClass(QMainWindow, Ui_widget):
    def __init__(self):
        super().__init__()
        self.clslogin = LOGIN()
        self.setupUi(self)
        self.menu = {"type": None, "select": None}
        self.login = {"id":None, "pw":None, "success":False}
        self.worker = None
        self.file_path = None
        # self.label_cashimg.setPixmap(self.pixmap)
        self._connect_events()

        self.text_edit_log = self.findChild(QTextEdit, "textEdit_log")

    def _connect_events(self):
        self.pushButton_main.clicked.connect(self.gotomain)
        self.pushButton_login.clicked.connect(self.handle_login)
        self.pushButton_run.clicked.connect(self.run_main)
        self.pushButton_open_file.clicked.connect(self.open_file_dialog)
        self._connect_radio_buttons()
    
    def gotomain(self):
        self.stackedWidget.setCurrentIndex(0)
        
    def handle_login(self):
        user_id, user_pw = self.lineEdit_id.text(), self.lineEdit_pw.text()
        self.login["success"] = self.clslogin.verify_login(user_id, user_pw)
        QMessageBox.information(self, "로그인", "로그인 성공" if self.login["success"] else "로그인 실패")


    def _connect_radio_buttons(self):
        self.radioButton_open_n.clicked.connect(self.choose_menu)
        self.radioButton_update_market.clicked.connect(self.choose_menu)
        self.radioButton_create_list.clicked.connect(self.choose_menu)
        self.radioButton_run_scrap.clicked.connect(self.choose_menu)
        self.radioButton_delete_market.clicked.connect(self.choose_menu)
        self.radioButton_upload_market.clicked.connect(self.choose_menu)
        self.radioButton_send_text.clicked.connect(self.choose_menu)
        self.radioButton_check_post.clicked.connect(self.choose_menu)
        
    def choose_menu(self):
        if not self.login["success"]:
            QMessageBox.information(self, "로그인", "로그인이 필요합니다.")
            return
        if self.radioButton_open_n.isChecked():
            logger.info("자동 N개 실행 선택")
            self.menu = {"type": TYPE.CASH, "select": SELECT.OPEN_N}
            self.stackedWidget.setCurrentIndex(1)
        elif self.radioButton_update_market.isChecked():
            logger.info("계정 업데이트 선택")
            self.menu = {"type": TYPE.CASH, "select": SELECT.UPDATE_MARKET}
            self.stackedWidget.setCurrentIndex(2)
        elif self.radioButton_create_list.isChecked():
            logger.info("수집 리스트 생성 선택")
            self.menu = {"type": TYPE.CASH, "select": SELECT.CREATE_LIST}
            self.stackedWidget.setCurrentIndex(3)
        elif self.radioButton_run_scrap.isChecked():
            logger.info("수집 실행 선택")
            self.menu = {"type": TYPE.CASH, "select": SELECT.SCRAP}
            self.stackedWidget.setCurrentIndex(4)
        elif self.radioButton_delete_market.isChecked():
            logger.info("마켓 연동 삭제 선택")
            self.menu = {"type": TYPE.CASH, "select": SELECT.DELETE}
            self.stackedWidget.setCurrentIndex(5)
        elif self.radioButton_upload_market.isChecked():
            logger.info("마켓 업로드 선택")
            self.menu = {"type": TYPE.CASH, "select": SELECT.UPLOAD}
            self.stackedWidget.setCurrentIndex(6)
        elif self.radioButton_send_text.isChecked():
            logger.info("대량 문자 발송 선택")
            self.menu = {"type": TYPE.CASH, "select": SELECT.TEXT}
            self.stackedWidget.setCurrentIndex(7)
        elif self.radioButton_check_post.isChecked():
            QMessageBox.information(self, "미지원", "제한된 기능 입니다.")
            return
            logger.info("배송 점검 선택")
            self.menu = {"type": TYPE.CASH, "select": SELECT.FAKE}
            self.stackedWidget.setCurrentIndex(8) 
            
    def open_file_dialog(self):
        try:
            options = QFileDialog.Options()
            options = QFileDialog.Options()
            options |= QFileDialog.DontUseNativeDialog  # 네이티브 다이얼로그 비활성화
            fname, _ = QFileDialog.getOpenFileName(
                self,
                "Open File",
                ".",
                "All Files (*);;Text Files (*.txt)",
                options=options
            )
            if fname:
                self.file_path = fname
                logger.info(f"open file 경로: {fname}")
            else:
                logger.info("파일이 선택되지 않았습니다. 다시 파일을 선택해 주세요.")
        except Exception as e:
            logger.info(f"오류 발생: {str(e)}")

    def run_main(self):
        if not self.login["success"]:
            QMessageBox.information(self, "로그인", "로그인이 필요합니다.")
            return        
        if not self.menu["select"] or not self.menu['type']:
            logger.info(f"작업을 선택해 주세요.: type:{self.menu['type']} select:{self.menu['select']}")
            return
        if self.worker is not None and self.worker.isRunning():
            logger.info("이미 실행 중인 작업이 있습니다.")
            return

        param = self._create_param()
        logger.info(f"실행 준비: param1 {param.param_1}, param2 {param.param_2}, market_dict {param.market_dict}, file_path {param.file_path}")
        self.worker = Worker(param)
        self.worker.finished.connect(self.on_worker_finished)
        self.worker.start()

    def _create_param(self):
        param = WORKER_PARAM(
            type_=self.menu['type'],
            select_=self.menu['select'],
            param_1=99,
            param_2=99,
            market_dict={"스마트스토어": False, "쿠팡": False, "지마켓": False, "옥션": False, "11번가": False, "롯데온": False},
            file_path=None,
            text_edit_log=None
        )
        
        if self.menu["select"] in {SELECT.OPEN_N, SELECT.CREATE_LIST, SELECT.SCRAP, SELECT.UPLOAD, SELECT.UPDATE_MARKET, SELECT.DELETE}:
            param.param_1 = getattr(self, f"sel_{self.menu['select'].value}_start").value()
            if self.menu["select"] is not SELECT.OPEN_N:
                param.param_2 = getattr(self, f"sel_{self.menu['select'].value}_end").value()

        if self.menu["select"] in {SELECT.UPDATE_MARKET, SELECT.DELETE}:
            self._update_market_dict(param)

        if self.menu["select"] in {SELECT.TEXT} and self.file_path:
            param.file_path = self.file_path
            param.text_edit_log = self.text_edit_log

        return param

    def _update_market_dict(self, param):
        markets = {
            "스마트스토어": "ss",
            "쿠팡": "cp",
            "지마켓": "g",
            "옥션": "a",
            "11번가": "st11",
            "롯데온": "l"
        }
        for market_name, suffix in markets.items():
            checkbox_name = f"checkBox_{self.menu['select'].value}_{suffix}"
            param.market_dict[market_name] = getattr(self, checkbox_name).isChecked()        

    def on_worker_finished(self):
        logger.info("작업이 완료되었습니다.")
        QMessageBox.information(self, "작업 완료", "작업이 성공적으로 완료되었습니다.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    myWindow = WindowClass()
    myWindow.show()
    sys.exit(app.exec_())