
import re
import wmi
import os.path
import time
import json
import os
import sys
from datetime import datetime
from tkinter import N
from pickle import FALSE, TRUE
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from dirsync import sync
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QApplication
from pathlib import Path

import threading


class Ui_MainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        
        super(Ui_MainWindow, self).__init__()
        uic.loadUi('ARS.ui', self)  # Load the .ui file
        global stop_threads, text_t, text_s
        self.auto_flag = "0"
        self.text_g = ""
        self.text_s = text_s = ""
        self.text_t = text_t = ""
        self.stop_threads_2 = "0"
        self.l = True
        self.selected_drive = ""
        
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
        self.button_launch_watchdog.setDisabled(False)


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
            win = AnotherWindow(self)
            win.exec_()
            self.v = str(win.listWidget.currentItem().text())
            self.p = win.lineEdit.text()
            self.selected_drive_index = re.split('[:]', self.v)
            self.selected_drive_index[0] += ":" # Selected Drive
            self.selected_drive = self.selected_drive_index[0]
            self.pre_populate_data()

        else:
            self.l.close()  # Close window.
            
            self.l = True

    def pre_populate_data(self):
        c = wmi.WMI()
        for drive in c.Win32_LogicalDisk():
            if drive.Caption == self.selected_drive:
                print(drive.Caption)
                print(self.selected_drive)

                drive_brackets = "[" + str(drive.VolumeName) + "]"

                self.test = drive.Caption + self.remove_prefix(
                    self.p, drive_brackets)
                print(drive_brackets)
                print(self.test)
                text_s = self.text_s = self.test
                self.lineEdit_source.setText('{}'.format(self.test))
            else:
                print("no luck")

    def remove_prefix(self, text, prefix):
        return text[text.startswith(prefix) and len(prefix):]

    def are_paths_valid(self):
        if os.path.isdir(text_t) is True and os.path.isdir(text_s) is True:
            self.button_sync.setDisabled(False)
            self.button_generate_mscript.setDisabled(False)
            self.button_launch_watchdog.setDisabled(False)
            return True

    
        

class AnotherWindow(QtWidgets.QDialog):
    def __init__(self, parent=Ui_MainWindow):
        super(AnotherWindow, self).__init__()
        uic.loadUi('Dialog.ui', self)  # Load the .ui file
        
        self.drive_volume_to_monitor()
        


    def drive_volume_to_monitor(self):
        c = wmi.WMI()
        
        for drive in c.Win32_LogicalDisk():
            drive_letter = str(drive.Caption) + str(drive.VolumeName)
            self.listWidget.addItem(drive_letter)
            

        self.listWidget.itemSelectionChanged.connect(self.selectionChanged)
        self.pushButton_select.setDisabled(False) # Temp
        self.commandLinkButton_go.setDisabled(False)  # Temp
        self.pushButton_select.clicked.connect(self.target_directory_select)
        self.commandLinkButton_go.clicked.connect(self.close_window)
    def UiComponents(self):
        self.listWidget = self.findChild(QtWidgets.QListWidget, "listWidget")
        self.lineEdit = self.findChild(QtWidgets.QLineEdit, "lineEdit")
        self.commandLinkButton_go = self.findChild(QtWidgets.QCommandLinkButton, "commandLinkButton_go")
        self.pushButton_select = self.findChild(QtWidgets.QPushButton, "pushButton_select")
        
        

    def selectionChanged(self):
        v = str(self.listWidget.currentItem().text())
        global current_drive_index# ['E:\\', '[USB_MIKE]']
        current_drive_index = re.split('[:]', v)
        current_drive_index[0] += ":\\"
        current_drive_index[1] = "[" + current_drive_index[1] + "]"
        self.lineEdit.setText('{}'.format(current_drive_index[1])) 
        self.pushButton_select.setDisabled(False)
        
        

    def close_window(self):
        
        self.close()
        
    
    def target_directory_select(self):
        
        global text_s
        target_path = text_s = str(QtWidgets.QFileDialog.getExistingDirectory(
            None, "", current_drive_index[0]))
        if os.path.isdir(target_path) is True:
            self.commandLinkButton_go.setDisabled(False) 
            append_index = re.split('[:]', target_path)
            append_index[0] = current_drive_index[1]
             # ['[USB_MIKE]', '/Test_Folder']

            view_index = (''.join(str(x) for x in append_index))

            self.lineEdit.setText('{}'.format(view_index))
            
        else:
            return
        

    
        
class Watcher(Ui_MainWindow):

    def __init__(self, directory=".", handler=FileSystemEventHandler()):
        self.observer = Observer()
        self.handler = handler
        global text_s
        self.directory = text_s

    def run(self):
        global text_s, text_t
        while self.is_drive_connected() != True: ## Loop to detect target drive connection
            
            print("NOT CONNECTED", text_s, text_t)
            time.sleep(0.5)
        print("drive connected")
        
        sync(text_s, text_t, 'sync', create=True)


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

    def is_drive_connected(self):
        global text_s, text_t
        if os.path.isdir(text_s) is True and os.path.isdir(text_t) is True:
            return True


class MyHandler(FileSystemEventHandler):

    def on_any_event(self, event):
        global text_s, text_t
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
           
           if stop_threads:
               return


if __name__ == "__main__":

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = Ui_MainWindow()
    sys.exit(app.exec_())
