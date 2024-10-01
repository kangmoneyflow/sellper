import sys, os
from PyQt5.QtWidgets import *
from PyQt5 import uic
from config import *
from enum import Enum
from libcashdata import *
from PyQt5.QtCore import QThread, pyqtSignal
from dataclasses import dataclass

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

# Config 및 UI 경로 설정
config = Config()
QT_SELLPER_PATH = os.path.join(config.base_dir, "sellper.ui")

form_class = uic.loadUiType(QT_SELLPER_PATH)[0]

# 오래 걸리는 작업을 백그라운드에서 실행하는 스레드 클래스
class Worker(QThread):
    # 스레드가 완료되면 신호를 보냄
    finished = pyqtSignal()

    def __init__(self, param: WOKER_PARAM):
        super().__init__()
        self.param = param
        self.menu = {"type":param.type_, "select":param.select_}

    def run(self):
        print(f"Thread 생성 후 실행 type:{self.menu['type']} select:{self.menu['select']}")
        if self.menu["select"] is SELECT.OPEN_N:
            loop = max(1, self.param.param_1)
            for i in range(loop):
                print(f"Run cashdata iteration {i+1}")
                cashdata = CashData()
                app = cashdata.run_cashdata()
        elif self.menu["select"] is SELECT.UPDATE_MARKET:
            print("계정 업데이트 로직 실행 중...")
        elif self.menu["select"] is SELECT.CREATE_LIST:
            print("수집 리스트 생성 실행 중...")
        elif self.menu["select"] is SELECT.SCRAP:
            dict_ = config.get_cashdata_scrap_sheet()
            start_ = self.param.param_1 - 2
            end_ = self.param.param_2 - 2
            print(f"start {start_} end {end_}")
            for i in range(start_, end_ + 1):  # end 값을 포함하려면 end + 1
                print(f"리스트명[{i+2}] {dict_['리스트명'][i]}")
                cashdata = CashData()
                cashdata.run_cashdata()
                cashdata.run_scrap(dict_['리스트명'][i])

        # 스레드 완료 신호
        self.finished.emit()

class WindowClass(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        
        self.menu = {"type": None, "select": None}

        # group box
        self.radioButton_open_n.clicked.connect(self.choose_menu)
        self.radioButton_update_market.clicked.connect(self.choose_menu)
        self.radioButton_create_list.clicked.connect(self.choose_menu)
        self.radioButton_run_scrap.clicked.connect(self.choose_menu)

        # 메인 실행 버튼
        self.pushButton_run.clicked.connect(self.run_main)

        # 백그라운드 스레드 완료 시 호출될 메서드
        self.worker = None

    def choose_menu(self):
        if self.radioButton_open_n.isChecked():
            print("자동 N개 실행 선택")
            self.menu = {"type": TYPE.CASH, "select": SELECT.OPEN_N}
            self.tabWidget.setCurrentIndex(1)
        elif self.radioButton_update_market.isChecked():
            print("계정 업데이트 선택")
            self.menu = {"type": TYPE.CASH, "select": SELECT.UPDATE_MARKET}
            self.tabWidget.setCurrentIndex(2)
        elif self.radioButton_create_list.isChecked():
            print("수집 리스트 생성 선택")
            self.menu = {"type": TYPE.CASH, "select": SELECT.CREATE_LIST}
            self.tabWidget.setCurrentIndex(3)
        elif self.radioButton_run_scrap.isChecked():
            print("수집 실행 선택")
            self.menu = {"type": TYPE.CASH, "select": SELECT.SCRAP}
            self.tabWidget.setCurrentIndex(4)
        elif self.radioButton_delete_market.isChecked():
            print("연동 삭제 선택")
            self.menu = {"type": TYPE.CASH, "select": SELECT.DELETE}
            self.tabWidget.setCurrentIndex(5)
        elif self.radioButton_upload_market.isChecked():
            print("연동 삭제 선택")
            self.menu = {"type": TYPE.CASH, "select": SELECT.UPLOAD}
            self.tabWidget.setCurrentIndex(6)            

    def run_main(self):
        if not self.menu["select"] or not self.menu['type']:
            print(f"작업을 선택해 주세요.: type:{self.menu['type']} select:{self.menu['select']}")
            return
        print(f"실행버튼 클릭: type:{self.menu['type']} select:{self.menu['select']}")
        
        # 기존의 실행 중인 스레드가 있으면 처리하지 않음
        if self.worker is not None and self.worker.isRunning():
            print("이미 실행 중인 작업이 있습니다.")
            return

        #Param 설정
        param = WOKER_PARAM(
            type_=self.menu['type'], 
            select_=self.menu['select'],
            param_1 = 1,
            param_2 = 2
        )
        
        if self.menu['type'] is TYPE.CASH and self.menu["select"] is SELECT.OPEN_N:
            param.param_1 = self.sel_1_num.value()
        elif self.menu['type'] is TYPE.CASH and self.menu["select"] is SELECT.SCRAP:
            param.param_1 = self.sel_4_start.value()
            param.param_2 = self.sel_4_end.value()
            print(f"param1 {param.param_1} param2 {param.param_2}")

        # 새로운 스레드를 시작하여 작업 실행
        self.worker = Worker(param)
        self.worker.finished.connect(self.on_worker_finished)
        self.worker.start()

    def on_worker_finished(self):
        print("작업이 완료되었습니다.")
        QMessageBox.information(self, "작업 완료", "작업이 성공적으로 완료되었습니다.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = WindowClass()
    myWindow.show()
    app.exec_()
