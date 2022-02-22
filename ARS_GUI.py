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
import jsonpickle
import os
import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from dirsync import sync
from pathlib import Path
from PyQt5.QtCore import QSize
from PyQt5 import QtCore, QtGui, QtWidgets

import threading
import time


class Ui_MainWindow(object):

    def __init__(self):
        self.auto_flag = "0"
        self.adv_text = ""
        self.text_g = ""
        self.text_s = ""
        self.text_t = ""

    def _open_file_dialog_source(self):  # function to open the dialog window
        source_path = str(QtWidgets.QFileDialog.getExistingDirectory())
        self.lineEdit.setText('{}'.format(source_path))
        print(source_path)
        global text_s
        text_s = self.text_s = source_path

        if os.path.isdir(self.text_t) == True and os.path.isdir(self.text_s) == True:
            self.toolButtonOpenDialog_3.setDisabled(False)
            self.toolButtonOpenDialog_4.setDisabled(False)
            self.toolButtonOpenDialog_5.setDisabled(False)

    def _open_file_dialog_target(self):
        target_path = str(QtWidgets.QFileDialog.getExistingDirectory())
        self.lineEdit_2.setText('{}'.format(target_path))
        print(target_path)
        global text_t
        text_t = self.text_t = target_path

        if os.path.isdir(self.text_t) == True and os.path.isdir(self.text_s) == True:
            self.toolButtonOpenDialog_3.setDisabled(False)
            self.toolButtonOpenDialog_4.setDisabled(False)
            self.toolButtonOpenDialog_5.setDisabled(False)

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
            self.toolButtonOpenDialog_4.setText(
                _translate("TestQFileDialog", "Manual Mode"))
            self.textEdit.setText('{}'.format(
                "Manual Mode enabled. Run the generated file to change the set configuration through CMD "))
        else:
            self.auto_flag = "1"
            self.toolButtonOpenDialog_4.setText(
                _translate("TestQFileDialog", "Auto = ON"))
            self.textEdit.setText('{}'.format(
                "Automode Enabled. You can fild the generated script in PATH. Feel free to add it to your task schedular or etc... "))
        print("Autoflag set to:", self.auto_flag)

    def _generate_auto_py(self):
        global text_s, text_t, py_data
        filename_py = "scripts/exec.py"
        file_name_conf = "scripts/config.json"

        os.makedirs(os.path.dirname(filename_py), exist_ok=True)
        with open(filename_py, "w") as f:
            f.write(py_data)

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
        text_s = self.text_s = self.lineEdit.text()
        text_t = self.text_t = self.lineEdit_2.text()
        if os.path.isdir(text_t) == False or os.path.isdir(text_s) == False:
            self.toolButtonOpenDialog_3.setDisabled(True)
            self.toolButtonOpenDialog_4.setDisabled(True)
            self.toolButtonOpenDialog_5.setDisabled(True)
            print("ONE OFF")
        elif os.path.isdir(self.text_t) == True and os.path.isdir(self.text_t) == True:
            self.toolButtonOpenDialog_3.setDisabled(False)
            self.toolButtonOpenDialog_4.setDisabled(False)
            self.toolButtonOpenDialog_5.setDisabled(False)
            print("ALL GOOD")

    def _run_watchdog(self):
        thread1 = myThread(1, "Thread-1", 1)
        thread1.start()

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

        self.formLayout_4.setWidget(
            0, QtWidgets.QFormLayout.SpanningRole, self.lineEdit)
        self.toolButtonOpenDialog = QtWidgets.QPushButton(self.widget)
        self.toolButtonOpenDialog.setObjectName("toolButtonOpenDialog")
        self.toolButtonOpenDialog.clicked.connect(
            self._open_file_dialog_source)

        self.formLayout_4.setWidget(
            1, QtWidgets.QFormLayout.LabelRole, self.toolButtonOpenDialog)
        self.lineEdit_2 = QtWidgets.QLineEdit(self.widget)
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.formLayout_4.setWidget(
            2, QtWidgets.QFormLayout.SpanningRole, self.lineEdit_2)
        self.toolButtonOpenDialog_2 = QtWidgets.QPushButton(self.widget)
        self.toolButtonOpenDialog_2.setObjectName("toolButtonOpenDialog_2")
        self.toolButtonOpenDialog_2.clicked.connect(
            self._open_file_dialog_target)

        self.lineEdit_2.textEdited.connect(self._text_Edited)

        self.formLayout_4.setWidget(
            3, QtWidgets.QFormLayout.LabelRole, self.toolButtonOpenDialog_2)
        self.textEdit = QtWidgets.QTextEdit(self.widget)
        self.textEdit.setObjectName("textEdit")
        self.formLayout_4.setWidget(
            4, QtWidgets.QFormLayout.SpanningRole, self.textEdit)
        self.toolButtonOpenDialog_3 = QtWidgets.QPushButton(self.widget)
        self.toolButtonOpenDialog_3.setObjectName("toolButtonOpenDialog_3")
        self.toolButtonOpenDialog_3.clicked.connect(
            self._sync_directory)

        self.formLayout_4.setWidget(
            6, QtWidgets.QFormLayout.LabelRole, self.toolButtonOpenDialog_3)
        self.toolButtonOpenDialog_4 = QtWidgets.QPushButton(self.widget)
        self.toolButtonOpenDialog_4.setObjectName("toolButtonOpenDialog_4")

        self.toolButtonOpenDialog_4.clicked.connect(
            self._enable_auto_flag)
        self.toolButtonOpenDialog_4.clicked.connect(
            self._generate_auto_py)

        self.formLayout_4.setWidget(
            6, QtWidgets.QFormLayout.FieldRole, self.toolButtonOpenDialog_4)
        self.toolButtonOpenDialog_5 = QtWidgets.QPushButton(self.widget)
        self.toolButtonOpenDialog_5.setObjectName("toolButtonOpenDialog_5")
        self.formLayout_4.setWidget(
            7, QtWidgets.QFormLayout.FieldRole, self.toolButtonOpenDialog_5)

        self.toolButtonOpenDialog_5.clicked.connect(
            self._run_watchdog)  # Watchdog button
        self.toolButtonOpenDialog_5.clicked.connect(self._sync_directory)

        self.label = QtWidgets.QLabel(self.widget)
        self.label.setObjectName("label")
        self.formLayout_4.setWidget(
            1, QtWidgets.QFormLayout.FieldRole, self.label)

        self.pushButton_6 = QtWidgets.QPushButton(self.widget)
        self.pushButton_6.setObjectName("pushButton_6")
        self.formLayout_4.setWidget(
            7, QtWidgets.QFormLayout.LabelRole, self.pushButton_6)

        self.label_2 = QtWidgets.QLabel(self.widget)
        self.label_2.setObjectName("label_2")
        self.formLayout_4.setWidget(
            3, QtWidgets.QFormLayout.FieldRole, self.label_2)

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
        TestQFileDialog.setWindowTitle(
            _translate("TestQFileDialog", "ARS Sync"))
        self.toolButtonOpenDialog.setText(_translate("TestQFileDialog", "..."))
        self.toolButtonOpenDialog_2.setText(
            _translate("TestQFileDialog", "..."))
        self.toolButtonOpenDialog_3.setText(
            _translate("TestQFileDialog", "Sync"))
        self.toolButtonOpenDialog_3.setDisabled(True)  # Gray out the button

        self.toolButtonOpenDialog_4.setText(_translate(
            "TestQFileDialog", "Generate Monitor Script"))
        self.toolButtonOpenDialog_4.setDisabled(True)

        self.toolButtonOpenDialog_5.setText(
            _translate("TestQFileDialog", "Launch Watchdog"))
        self.toolButtonOpenDialog_5.setDisabled(True)

        self.pushButton_6.setText(_translate("TestQFileDialog", "Button_1"))

        self.label.setText(_translate("TestQFileDialog", "Source Directory"))
        self.label_2.setText(_translate("TestQFileDialog", "Target Directory"))


class Watcher(Ui_MainWindow):

    def __init__(self, directory=".", handler=FileSystemEventHandler()):
        self.observer = Observer()
        self.handler = handler
        global text_s
        self.directory = text_s

    def run(self):

        self.observer.schedule(self.handler, self.directory, recursive=True)
        self.observer.start()
        print("\nWatcher Running in {}/\n".format(self.directory))
        try:
            while True:
                time.sleep(1)
        except:
            self.observer.stop()
        self.observer.join()
        print("\nWatcher Terminated\n")


class MyHandler(FileSystemEventHandler):

    def on_any_event(self, event):
        print("Files Changed")  # Code here
        global text_s, text_t

        sync(text_s, text_t, 'sync', create=True)


class myThread (threading.Thread):
   def __init__(self, threadID, name, counter):
      threading.Thread.__init__(self)
      self.threadID = threadID
      self.name = name
      self.counter = counter

   def run(self):
      print("Starting " + self.name)
      w = Watcher(".", MyHandler())
      w.run()
      print("Exiting " + self.name)


py_data = r"""
from ast import excepthandler
from pathlib import Path
from pickle import FALSE, TRUE
from tkinter import N
from dirsync import sync
from datetime import datetime
import os.path
import json
import pathlib
import jsonpickle
import time
import csv  
import wmi

def check_config_present():
    currentdir = Path(__file__).parent.absolute()
    fullpath = os.path.join(currentdir, 'config.json')
    if os.path.exists(fullpath):
        config_exists = True
        load_config()
    else:
        config_exists = False
    return config_exists


def check_data_present():
    currentdir = Path(__file__).parent.absolute()
    fullpath = os.path.join(currentdir, 'data.json')
    if os.path.exists(fullpath):
        config_exists = True
    else:
        config_exists = False
        save_current_files_to_data()
    return config_exists


def first_ran_func():
    print("Config not present. Initializing... ")


def user_input():
    global source_path
    global target_path
    source_path = input(r"Enter the sync source directory:").strip()
    print(source_path)

    my_file = Path(source_path)
    if my_file.is_dir():
        print("Dir exists")
    else:
        print("Dir does not exist, try again")

        isdir = os.path.isdir(source_path)
        while isdir == False:
            source_path = input(r"Enter the sync source directory::").strip()
            isdir = os.path.isdir(source_path)
            my_file = Path(source_path)
            if my_file.is_dir():
                print("Dir exists")
            else:
                print("Dir does not exist, try again")
    target_path = input(r"Enter the sync TARGET (folder):").strip()
    print(target_path)

    my_file = Path(target_path)
    if my_file.is_dir():
        print("Dir exists")
    else:
        print("Dir does not exist, try again")

        isdir = os.path.isdir(target_path)
        while isdir == False:
            target_path = input(r"Enter the sync target directory:").strip()
            isdir = os.path.isdir(target_path)
            my_file = Path(target_path)
            if my_file.is_dir():
                print("Dir exists")
            else:
                print("Dir does not exist, try again")


def config_save(auto_flag):
    data = {
        r"source_path": source_path,
        r"target_path": target_path,
        r'Automation Flag': auto_flag,
        r'Drive Volume': source_volume_name,
    }
    json_string = json.dumps(data)
    with open("config.json", "w") as jsonfile:
        json.dump(data, jsonfile)


def load_config():
    mypath = Path(__file__).parent.absolute()
    fullpath = os.path.join(mypath, 'config.json')
    if os.path.isfile(fullpath):
        print("Config.json loaded")
        with open('config.json', 'r') as f:
            config_loaded = json.load(f)

            global source_path
            global target_path
            source_path = config_loaded["source_path"]
            target_path = config_loaded["target_path"]
    return source_path, target_path


def load_data():
    mypath = Path(__file__).parent.absolute()
    fullpath = os.path.join(mypath, 'data.json')
    if os.path.isfile(fullpath):
        print("Data.json loaded")
        with open('data.json', 'r') as f:
            global file_history_snapshot_set
            file_history_snapshot = json.load(f)
            file_history_snapshot_set = jsonpickle.decode(
                file_history_snapshot)


def ask_user_sync():
    global ask_user_sync_anwser
    ask_user_sync_anwser = input(
        "Would you like to sync now? Or edit current properties? Type y to sync, n to edit\n").strip()
    while ask_user_sync_anwser != 'y' and ask_user_sync_anwser != 'n':
        print('Invalid input')
        ask_user_sync_anwser = input("Type y to sync, n to edit\n").strip()
    return ask_user_sync_anwser


def populate_data():
    nameSet = set()
    for file in os.listdir(source_path):
        fullpath = os.path.join(source_path, file)
        if os.path.isfile(fullpath):
            nameSet.add(file)
        if os.path.isfile(fullpath):
            nameSet.add(file)
        else:
            os.path.isdir(fullpath)
            nameSet.add(file)
    retrievedSet = set()
    for name in nameSet:
        stat = os.stat(os.path.join(source_path, name))
        time = os.path.getmtime(os.path.join(source_path, name))
        size = os.path.getsize(os.path.join(source_path, name))
        time_str = str(time)
        size_str = str(size)
        retrievedSet.add((name, time_str, size_str))
    sampleJson = jsonpickle.encode(retrievedSet)

    global new_files_set
    global deleted__files_set
    global Directory_change_bool

    new_files_set = retrievedSet - file_history_snapshot_set
    deleted__files_set = file_history_snapshot_set - retrievedSet

    global new_files_list
    new_files_list = list(new_files_set)

    with open("data.json", "w") as jsonfile:
        json.dump(sampleJson, jsonfile)


def save_current_files_to_data():
    nameSet = set()
    for file in os.listdir(source_path):
        fullpath = os.path.join(source_path, file)
        if os.path.isfile(fullpath):
            nameSet.add(file)
        if os.path.isfile(fullpath):
            nameSet.add(file)
        else:
            os.path.isdir(fullpath)
            nameSet.add(file)
    retrievedSet = set()
    for name in nameSet:
        stat = os.stat(os.path.join(source_path, name))
        time = os.path.getmtime(os.path.join(source_path, name))
        size = os.path.getsize(os.path.join(source_path, name))
        time_str = str(time)
        size_str = str(size)
        retrievedSet.add((name, time_str, size_str))
    sampleJson = jsonpickle.encode(retrievedSet)
    with open("data.json", "w") as jsonfile:
        json.dump(sampleJson, jsonfile)


def ask_user_automation():
    ask_user_automation_anwser = input(
        "Would you like to convert this script to monitor mode and set auto_flag = 1. Type y/n\n").strip()
    while ask_user_automation_anwser != 'y' and ask_user_automation_anwser != 'n':
        print('Invalid input')
        ask_user_automation_anwser = input(
            "Would you like to convert this script to monitor mode and set auto_flag = 1. Type y/n\n").strip()
    if ask_user_automation_anwser == 'y':
        drive_volume_to_monitor()
        config_save('1')
        print("Automation mode enabled and saved to config.json.")
        print("You can disable it by setting auto_flag property back to '0' ")
    else:
        print("Exiting...")


def check_auto_flag():
    currentdir = Path(__file__).parent.absolute()
    fullpath = os.path.join(currentdir, 'config.json')
    if os.path.exists(fullpath):
        with open('config.json', 'r') as f:
            config_loaded = json.load(f)
            flag = config_loaded["Automation Flag"]
        return flag


def check_dir_for_changes():
    nameSet = set()
    for file in os.listdir(source_path):
        fullpath = os.path.join(source_path, file)
        if os.path.isfile(fullpath):
            nameSet.add(file)
        if os.path.isfile(fullpath):
            nameSet.add(file)
        else:
            os.path.isdir(fullpath)
            nameSet.add(file)

    current_files_set_now = set()
    for name in nameSet:
        stat = os.stat(os.path.join(source_path, name))
        time = os.path.getmtime(os.path.join(source_path, name))
        size = os.path.getsize(os.path.join(source_path, name))
        time_str = str(time)
        size_str = str(size)
        current_files_set_now.add((name, time_str, size_str))

    files_deleted_bool = (len(new_files_set) == 0)
    files_added_bool = (len(deleted__files_set) == 0)

    if files_added_bool == False or files_deleted_bool == False:
        Directory_change_bool = True
    else:
        Directory_change_bool = False

    return Directory_change_bool


def convertTuple(tup):
    st = ''.join(map(str, tup))
    return st


def save_data_to_cvs(data):
    with open('file_history.csv', 'a+', newline='') as f:
        for x in data:
            list_1 = list(x)

            time_convert = int(float(list_1[1]))  # CONVERT STR to INT (time)
            list_1[1] = time.ctime(time_convert)

            size_convert = int(list_1[2]) / 1000
            list_1[2] = size_convert

            write = csv.writer(f)
            write.writerows([list_1])


def check_csv_header():
    global refernce_header
    refernce_header = ['File name', 'Date modified', 'File size (KB)']
    with open('file_history.csv') as f:
        mycsv = csv.reader(f)

        for row in mycsv:

            if row == refernce_header:
                return None
            else:
                create_csv_header()
        if is_empty_csv() == True:
            create_csv_header()


def is_empty_csv():
    with open('file_history.csv') as f:
        reader = csv.reader(f)
        for i, _ in enumerate(reader):
            if i:
                return False
    return True


def create_csv_header():

    file = open('file_history.csv', 'w', newline='')
    write = csv.writer(file)
    write.writerows([refernce_header])


def convertTuple(tup):
    st = ''.join(map(str, tup))
    return st


def drive_volume_to_monitor():
    c = wmi.WMI()
    global source_volume_name
    global Driv_Letter
    valid = False
    source_volume_name = input("Enter Drive volume name to monitor\n").strip()
    for drive in c.Win32_LogicalDisk():
        if source_volume_name == drive.VolumeName:
            print("Drive volume name is valid")
            valid = True
            x = 0
            Driv_Letter = []
            Driv_Letter.append(drive.Caption)
            x = x + 1
    if valid != True:
        print("Drive Volume Name is not found")

    proceed_check = input("Would you like to proceed?Type y/n\n").strip()
    while proceed_check != 'y' and proceed_check != 'n':
        print('Invalid input')
        proceed_check = input(
            "Would you still like to proceed Type y/n\n").strip()
        if proceed_check == 'y':
            print(source_volume_name)


try:
    check_csv_header()
except:
    create_csv_header()

if check_auto_flag() == '1':

    load_config()
    if check_data_present() == False:
        print("No data.json found. Updating...")
        save_current_files_to_data()

    load_data()
    populate_data()

    if check_dir_for_changes() == True:
        print('File Changes are detected. Syncing...')
        sync(source_path, target_path, 'sync', create=True)

    else:
        print('No File changes detected since last ran.')

    save_data_to_cvs(new_files_list)
    print('Any file change has been recorded to the .csv file | Exiting...')
    time.sleep(1)
    quit()

if check_config_present() == False:
    first_ran_func()
    user_input()
    config_save('0')

check_data_present()

if ask_user_sync() == 'y':
    try:
        sync(source_path, target_path, 'sync', create=True)
    except ValueError as exception:
        print('There was a problem with loading the config, please reconfigure the source and target path values.\n')
        print(r'For example: Correct input format - C:\Users\Mike\Documents\Source_Copy')
        quit()
else:
    user_input()
    config_save('0')
    ask_user_automation()
    quit()

load_data()
populate_data()

save_data_to_cvs(new_files_list)

ask_user_automation()

#source_path = 'C:\Users\Mike\Documents\Source_Copy'
#target_path = 'C:\Users\Mike\Documents\Dest_Copy'

#C:\Users\Mike\Desktop\Test copy
#C:\Users\Mike\Desktop\Test -aste
"""


if __name__ == "__main__":

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    MainWindow.setFixedSize(QSize(232, 332))  # setFixedSize(QSize)

    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()

    sys.exit(app.exec_())
