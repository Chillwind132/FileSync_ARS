import csv
import wmi
import pathlib
import os.path
from datetime import datetime
from tkinter import N
from pickle import FALSE, TRUE
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import json
import os
import sys
from dirsync import sync
from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from pathlib import Path

import threading


class Ui_MainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        
        super(Ui_MainWindow, self).__init__()
        uic.loadUi('ARS.ui', self)  # Load the .ui file

        self.auto_flag = "0"
        self.text_g = ""
        self.text_s = ""
        self.text_t = ""
        self.l = True

        global stop_threads
        stop_threads = "1"

        self.button_source = self.findChild(
            QtWidgets.QPushButton, "toolButtonOpenDialog")
        self.button_source.clicked.connect(self._open_file_dialog_source)

        self.button_target = self.findChild(
            QtWidgets.QPushButton, "toolButtonOpenDialog_2")
        self.button_target.clicked.connect(self._open_file_dialog_target)

        self.button_sync = self.findChild(
            QtWidgets.QPushButton, "toolButtonOpenDialog_3")
        self.button_sync.clicked.connect(self._sync_directory)
        self.button_sync.setDisabled(True)

        self.button_generate_mscript = self.findChild(
            QtWidgets.QPushButton, "toolButtonOpenDialog_4")
        self.button_generate_mscript.clicked.connect(self._enable_auto_flag)
        self.button_generate_mscript.clicked.connect(self._generate_auto_py)
        self.button_generate_mscript.setDisabled(True)

        self.button_launch_watchdog = self.findChild(
            QtWidgets.QPushButton, "toolButtonOpenDialog_5")
        self.button_launch_watchdog.clicked.connect(self._run_watchdog)
        self.button_launch_watchdog.setDisabled(True)


        self.button_select_drive = self.findChild(
            QtWidgets.QPushButton, "pushButton_6")
        self.button_select_drive.clicked.connect(self.show_new_window)

        self.lineEdit_source = self.findChild(QtWidgets.QLineEdit, "lineEdit")
        self.lineEdit_source.textEdited.connect(self._text_Edited)

        self.lineEdit_target = self.findChild(
            QtWidgets.QLineEdit, "lineEdit_2")
        self.lineEdit_target.textEdited.connect(self._text_Edited)

        self.textEdit_m = self.findChild(QtWidgets.QTextEdit, "textEdit")

        self.show()

    def _open_file_dialog_source(self):  # function to open the dialog window
        source_path = str(QtWidgets.QFileDialog.getExistingDirectory())
        self.lineEdit_source.setText('{}'.format(source_path))
        print(source_path)
        global text_s
        text_s = self.text_s = source_path

        if os.path.isdir(self.text_t) is True and os.path.isdir(self.text_s) is True:
            self.button_sync.setDisabled(False)
            self.button_generate_mscript.setDisabled(False)
            self.button_launch_watchdog.setDisabled(False)

    def _open_file_dialog_target(self):
        target_path = str(QtWidgets.QFileDialog.getExistingDirectory())
        self.lineEdit_target.setText('{}'.format(target_path))
        print(target_path)
        global text_t
        text_t = self.text_t = target_path

        if os.path.isdir(self.text_t) is True and os.path.isdir(self.text_s) is True:
            self.button_sync.setDisabled(False)
            self.button_generate_mscript.setDisabled(False)
            self.button_launch_watchdog.setDisabled(False)

    def _sync_directory(self):
        global text_s, text_t
        print("Source_path:", text_s)
        print("Target_path:", text_t)
        sync(text_s, text_t, 'sync', create=True)

    def _enable_auto_flag(self):

        _translate = QtCore.QCoreApplication.translate
        check = self.auto_flag
        if check == "1":
            self.auto_flag = "0"
            self.button_generate_mscript.setText(
                _translate("TestQFileDialog", "Manual Mode"))
            self.textEdit_m.setText('{}'.format(
                "Manual Mode enabled. Run the generated file to change the set configuration through CMD "))
        else:
            self.auto_flag = "1"
            self.button_generate_mscript.setText(
                _translate("TestQFileDialog", "Auto = ON"))
            self.textEdit_m.setText('{}'.format(
                "Automode Enabled. You can fild the generated script in PATH. Feel free to add it to your task schedular or etc... "))
        print("Autoflag set to:", self.auto_flag)

    def _generate_auto_py(self):
        global text_s, text_t, py_data
        filename_py = "scripts/exec.py"
        file_name_conf = "scripts/config.json"
        self.txt_g = Path("py_data").read_text()
        os.makedirs(os.path.dirname(filename_py), exist_ok=True)
        with open(filename_py, "w") as f:
            f.write(self.txt_g)

        data = {
            r"source_path": text_s,
            r"target_path": text_t,
            r'Automation Flag': self.auto_flag,

        }
        json_string = json.dumps(data)
        with open(file_name_conf, "w") as jsonfile:
            json.dump(data, jsonfile)

    def _text_Edited(self):
        global text_s, text_t
        text_s = self.text_s = self.lineEdit_source.text()
        text_t = self.text_t = self.lineEdit_target.text()
        if os.path.isdir(text_t) is False or os.path.isdir(text_s) is False:
            self.button_sync.setDisabled(True)
            self.button_generate_mscript.setDisabled(True)
            self.button_launch_watchdog.setDisabled(True)
            print("ONE OFF")
        elif os.path.isdir(self.text_t) is True and os.path.isdir(self.text_t) is True:
            self.button_sync.setDisabled(False)
            self.button_generate_mscript.setDisabled(False)
            self.button_launch_watchdog.setDisabled(False)
            print("ALL GOOD")

    def _run_watchdog(self):
        global stop_threads
        _translate = QtCore.QCoreApplication.translate
        thread1 = myThread(1, "Thread-1", 1)

        if stop_threads == "1":
            thread1.start()
            stop_threads = "0"
            self.button_launch_watchdog.setText(
                _translate("TestQFileDialog", "Watchdog running..."))
            self.textEdit_m.setText('{}'.format(
                "Watchdog is currently monitoring the target directory for changes and syncing any changes automatiicaly"))
        else:
            stop_threads = "1"

            self.button_launch_watchdog.setText(
                _translate("TestQFileDialog", "Watchdog disabled"))
            self.textEdit_m.setText('{}'.format(
                "Watchdog has been disabled - click the button again to re-activate"))

    def show_new_window(self, checked):
        if self.l is True:
            self.win = AnotherWindow()
            self.win.show()
        else:
            self.l.close()  # Close window.
            self.l = True


class AnotherWindow(QtWidgets.QDialog):
    def __init__(self):
        super(AnotherWindow, self).__init__()
        uic.loadUi('Dialog.ui', self)  # Load the .ui file

class Watcher(Ui_MainWindow):

    def __init__(self, directory=".", handler=FileSystemEventHandler()):
        self.observer = Observer()
        self.handler = handler
        global text_s
        self.directory = text_s

    def run(self):
        self.observer.schedule(self.handler, self.directory, recursive=True)
        self.observer.start()

        try:
            while True:
                print("\nWatcher Running in {}/\n".format(self.directory))
                time.sleep(1)
                global stop_threads
                if stop_threads == "1":
                    self.observer.stop()
                    self.observer.join()
                    return
        except:
            self.observer.stop()
            self.observer.join()
        print("\nWatcher Terminated\n")


class MyHandler(FileSystemEventHandler):

    def on_any_event(self, event):
        print("Files Changed")  # Code here
        global text_s, text_t, stop_threads

        sync(text_s, text_t, 'sync', create=True)


class myThread (threading.Thread):
   def __init__(self, threadID, name, counter):
      threading.Thread.__init__(self)
      self.threadID = threadID
      self.name = name
      self.counter = counter

   def run(self):
       print("Starting thread 1")
       while True:
           time.sleep(0.5)
           print("Working")
           print("Starting " + self.name)
           w = Watcher(".", MyHandler())
           w.run()
           print("Exiting " + self.name)
           global stop_threads
           if stop_threads:
               return


if __name__ == "__main__":

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = Ui_MainWindow()
    sys.exit(app.exec_())
