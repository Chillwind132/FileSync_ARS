import json
import jsonpickle
import os
import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from dirsync import sync
from pathlib import Path
from PyQt5.QtCore import QSize
from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):

    def __init__(self):
        self.text_s = ""
        self.text_t = ""
        self.auto_flag = "0"
        self.adv_text = ""
        self.text_g = ""

    def _open_file_dialog_source(self):  # function to open the dialog window
        source_path = str(QtWidgets.QFileDialog.getExistingDirectory())
        self.lineEdit.setText('{}'.format(source_path))
        print(source_path)
        self.text_s = source_path

        if os.path.isdir(self.text_t) == True and os.path.isdir(self.text_s) == True:
            self.toolButtonOpenDialog_3.setDisabled(False)
            self.toolButtonOpenDialog_4.setDisabled(False)

    def _open_file_dialog_target(self):
        target_path = str(QtWidgets.QFileDialog.getExistingDirectory())
        self.lineEdit_2.setText('{}'.format(target_path))
        print(target_path)
        self.text_t = target_path

        if os.path.isdir(self.text_t) == True and os.path.isdir(self.text_s) == True:
            self.toolButtonOpenDialog_3.setDisabled(False)
            self.toolButtonOpenDialog_4.setDisabled(False)
        
    def _sync_directory(self):
        source_path = self.text_s
        target_path = self.text_t
        print("Source_path:", source_path)
        print("Target_path:", target_path)
        sync(source_path, target_path, 'sync', create=True)

    def _enable_auto_flag(self):

        _translate = QtCore.QCoreApplication.translate
        check = self.auto_flag
        if check == "1":
            self.auto_flag = "0"
            self.toolButtonOpenDialog_4.setText(_translate("TestQFileDialog", "Manual Mode"))
            self.textEdit.setText('{}'.format("Manual Mode enabled. Run the generated file to change the set configuration through CMD "))
        else:
            self.auto_flag = "1"
            self.toolButtonOpenDialog_4.setText(_translate("TestQFileDialog", "Auto = ON"))
            self.textEdit.setText('{}'.format("Automode Enabled. You can fild the generated script in PATH. Feel free to add it to your task schedular or etc... "))
        print("Autoflag set to:", self.auto_flag)

    def _generate_auto_py(self):
        filename_py = "scripts/exec.py"
        file_name_conf = "scripts/config.json"
        self.txt_g = Path("py_data").read_text()

        os.makedirs(os.path.dirname(filename_py), exist_ok=True)
        with open(filename_py, "w") as f:
            f.write(self.txt_g)

        data = {
            r"source_path": self.text_s,
            r"target_path": self.text_t,
            r'Automation Flag': self.auto_flag,

        }
        json_string = json.dumps(data)
        with open(file_name_conf, "w") as jsonfile:
            json.dump(data, jsonfile)

        
    def _text_Edited(self):
    
        self.text_s = self.lineEdit.text()
        self.text_t = self.lineEdit_2.text()
        
        if os.path.isdir(self.text_t) == False or os.path.isdir(self.text_s) == False:
            self.toolButtonOpenDialog_3.setDisabled(True)
            self.toolButtonOpenDialog_4.setDisabled(True)
            print("ONE OFF")
        elif os.path.isdir(self.text_t) == True and os.path.isdir(self.text_t) == True:
            self.toolButtonOpenDialog_3.setDisabled(False)
            self.toolButtonOpenDialog_4.setDisabled(False)
            print("ALL GOOD")

        

    def setupUi(self, TestQFileDialog):

        TestQFileDialog.setObjectName("TestQFileDialog")
        TestQFileDialog.resize(295, 389)
        self.Widget = QtWidgets.QWidget(TestQFileDialog)
        self.Widget.setObjectName("Widget")
        self.widget = QtWidgets.QWidget(self.Widget)
        self.widget.setGeometry(QtCore.QRect(10, 10, 211, 301))
        self.widget.setObjectName("widget")
        self.formLayout_4 = QtWidgets.QFormLayout(self.widget)
        self.formLayout_4.setContentsMargins(0, 0, 0, 0)
        self.formLayout_4.setObjectName("formLayout_4")

        
        self.lineEdit = QtWidgets.QLineEdit(self.widget)
        self.lineEdit.setObjectName("lineEdit")
        self.lineEdit.textEdited.connect(self._text_Edited)


        self.formLayout_4.setWidget(0, QtWidgets.QFormLayout.SpanningRole, self.lineEdit)
        self.toolButtonOpenDialog = QtWidgets.QPushButton(self.widget)
        self.toolButtonOpenDialog.setObjectName("toolButtonOpenDialog")
        directory_source = self.toolButtonOpenDialog.clicked.connect(
        self._open_file_dialog_source)


        self.formLayout_4.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.toolButtonOpenDialog)
        self.lineEdit_2 = QtWidgets.QLineEdit(self.widget)
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.formLayout_4.setWidget(2, QtWidgets.QFormLayout.SpanningRole, self.lineEdit_2)
        self.toolButtonOpenDialog_2 = QtWidgets.QPushButton(self.widget)
        self.toolButtonOpenDialog_2.setObjectName("toolButtonOpenDialog_2")
        directory_target = self.toolButtonOpenDialog_2.clicked.connect(
        self._open_file_dialog_target)

        self.lineEdit_2.textEdited.connect(self._text_Edited)
        

        self.formLayout_4.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.toolButtonOpenDialog_2)
        self.textEdit = QtWidgets.QTextEdit(self.widget)
        self.textEdit.setObjectName("textEdit")
        self.formLayout_4.setWidget(4, QtWidgets.QFormLayout.SpanningRole, self.textEdit)
        self.toolButtonOpenDialog_3 = QtWidgets.QPushButton(self.widget)
        self.toolButtonOpenDialog_3.setObjectName("toolButtonOpenDialog_3")
        self.toolButtonOpenDialog_3.clicked.connect(
        self._sync_directory)


        self.formLayout_4.setWidget(6, QtWidgets.QFormLayout.LabelRole, self.toolButtonOpenDialog_3)
        self.toolButtonOpenDialog_4 = QtWidgets.QPushButton(self.widget)
        self.toolButtonOpenDialog_4.setObjectName("toolButtonOpenDialog_4")
        
        self.toolButtonOpenDialog_4.clicked.connect(
            self._enable_auto_flag)
        self.toolButtonOpenDialog_4.clicked.connect(
        self._generate_auto_py)


        self.formLayout_4.setWidget(6, QtWidgets.QFormLayout.FieldRole, self.toolButtonOpenDialog_4)
        self.toolButtonOpenDialog_5 = QtWidgets.QPushButton(self.widget)
        self.toolButtonOpenDialog_5.setObjectName("toolButtonOpenDialog_5")
        self.formLayout_4.setWidget(7, QtWidgets.QFormLayout.FieldRole, self.toolButtonOpenDialog_5)
        self.pushButton_6 = QtWidgets.QPushButton(self.widget)
        self.pushButton_6.setObjectName("pushButton_6")
        self.formLayout_4.setWidget(7, QtWidgets.QFormLayout.LabelRole, self.pushButton_6)
        TestQFileDialog.setCentralWidget(self.Widget)
        self.menubar = QtWidgets.QMenuBar(TestQFileDialog)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 295, 21))
        self.menubar.setObjectName("menubar")
        TestQFileDialog.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(TestQFileDialog)
        self.statusbar.setObjectName("statusbar")
        TestQFileDialog.setStatusBar(self.statusbar)

        self.retranslateUi(TestQFileDialog)
        QtCore.QMetaObject.connectSlotsByName(TestQFileDialog)

    def retranslateUi(self, TestQFileDialog):
        _translate = QtCore.QCoreApplication.translate
        TestQFileDialog.setWindowTitle(_translate("TestQFileDialog", "MainWindow"))
        self.toolButtonOpenDialog.setText(_translate("TestQFileDialog", "..."))
        self.toolButtonOpenDialog_2.setText(_translate("TestQFileDialog", "..."))
        self.toolButtonOpenDialog_3.setText(_translate("TestQFileDialog", "Sync"))
        self.toolButtonOpenDialog_3.setDisabled(True) ## Gray out the button

        self.toolButtonOpenDialog_4.setText(_translate("TestQFileDialog", "Generate Monitor Script"))
        self.toolButtonOpenDialog_4.setDisabled(True)
        self.toolButtonOpenDialog_5.setText(_translate("TestQFileDialog", "Button_2"))
        self.pushButton_6.setText(_translate("TestQFileDialog", "Button_1"))


if __name__ == "__main__":
    
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    MainWindow.setFixedSize(QSize(232, 332))  # setFixedSize(QSize)

    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
