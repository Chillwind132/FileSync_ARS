import re
import wmi
import os.path
import time
import json
import os
import sys
import yaml
from datetime import datetime
from tkinter import N
from pickle import FALSE, TRUE
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from dirsync import sync
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QApplication, QAction, QMessageBox
from pathlib import Path
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QGridLayout, QWidget, QCheckBox, QSystemTrayIcon, \
QSpacerItem, QSizePolicy, QMenu, QAction, QStyle, qApp
from PyQt5.QtGui import QIcon
import threading
import pythoncom

class Ui_MainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        
        super(Ui_MainWindow, self).__init__()
        uic.loadUi('ARS.ui', self)  # Load the .ui file
        global stop_threads, text_t, text_s, toggle, is_closed, force_file_sync
        self.auto_flag = False
        self.text_g = ""
        self.text_s = text_s = ""
        self.text_t = text_t = ""
        self.stop_threads_2 = "0"
        self.l = True
        self.selected_drive = ""
        self.parameters = ""
        stop_threads = "1"
        toggle = ""
        is_closed = True
        force_file_sync = False


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

        self.checkBox_override = self.findChild(
            QtWidgets.QCheckBox, "checkBox_override")
        self.checkBox_override.stateChanged.connect(self._manual_override)
        self.checkBox_force = self.findChild(
            QtWidgets.QCheckBox, "checkBox_force")
        self.checkBox_force.stateChanged.connect(self.sync_parameters)

        self.textEdit_m.setText('{}'.format(
            "1) Select your source and target directory for data synchronisation.\n2) If you wish, you have an option to sync to a removable media on connection - set this up by clicking on the 'select' button.\n3) Generate monitor script option is made to be launched at a specific time intervals.\n4) Watchdog is newer and therefore recommended to use."))
        


        self.trayicon = QSystemTrayIcon(self)
        self.trayicon.setIcon(QIcon("ars_icon.ico"))
        menu = QMenu()
        checkAction = menu.addAction("Show Menu")
        checkAction.triggered.connect(self.show_main_window)
        
        
        watchdogAction = menu.addAction("Start/Stop Watchdog")
            
        
        watchdogAction.triggered.connect(self._run_watchdog)
        watchdogAction.triggered.connect(self.update_menu)
        quitAction = menu.addAction("Quit")
        quitAction.triggered.connect(qApp.quit)

        self.trayicon.setContextMenu(menu)
        self.trayicon.show()
        
        self.check_auto_flag()
        self.first_load()
        
        #self.show()

    def update_menu(self):
        123
        
        
    def check_auto_flag(self):
        _translate = QtCore.QCoreApplication.translate
        with open('data.yml') as outfile:
                doc = yaml.safe_load(outfile)
                if doc['auto'] == True:
                    self.hide()
                    self.button_generate_mscript.setText(
                    _translate("TestQFileDialog", "Auto = ON"))
                    self._run_watchdog()
                    self.auto_flag = True
                else:
                    self.button_generate_mscript.setText(
                    _translate("TestQFileDialog", "Auto = OFF"))
                    self.show()


    def show_main_window(self):
        self.show()


    def first_load(self):
        
        if os.path.isfile("data.yml"):
            with open('data.yml') as outfile:
                global text_s, text_t
                doc = yaml.safe_load(outfile)
                self.text_s = text_s = doc['src']
                self.text_t = text_t = doc['trg']
                self.lineEdit_source.setText('{}'.format(doc['src']))
                self.lineEdit_target.setText('{}'.format(doc['trg']))
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
        else:
            with open('data.yml', 'w') as outfile:
                data = {
                    'src': '', 
                    'trg': '',
                    'auto': False,
                    
                }
                yaml.dump(data, outfile)

    def save_to_yaml(self, **kwargs):
        source_path = ""
        target_path = ""
        source_path = kwargs.get("src", source_path)
        source_path = kwargs.get("trg", target_path)

        for i, k in kwargs.items():   
            if i == "src":
                with open('data.yml') as outfile:
                   doc = yaml.safe_load(outfile)
                   doc['src'] = k
                with open('data.yml','w') as outfile:
                    yaml.dump(doc, outfile)
            elif i == "trg":
                with open('data.yml') as outfile:
                   doc = yaml.safe_load(outfile)
                   doc['trg'] = k
                with open('data.yml','w') as outfile:
                    yaml.dump(doc, outfile)
            

        
    def sync_parameters(self):
        if self.checkBox_force.isChecked():
            global force_file_sync
            force_file_sync = True
            print("force_file_sync enabled")
        else:
            force_file_sync = False

    def _manual_override(self):
        if self.checkBox_override.isChecked():
            self.button_launch_watchdog.setDisabled(False)
            self.button_generate_mscript.setDisabled(False)
            self.button_sync.setDisabled(False)
        else:
            self.button_launch_watchdog.setDisabled(True)
            self.button_generate_mscript.setDisabled(True)
            self.button_sync.setDisabled(True)

    def _open_file_dialog_source(self):  # function to open the dialog window
        source_path = str(QtWidgets.QFileDialog.getExistingDirectory())
        if source_path == "":
            return
        self.lineEdit_source.setText('{}'.format(source_path))
        print(source_path)
        global text_s
        text_s = self.text_s = source_path

        self.save_to_yaml(src=text_s)

        if os.path.isdir(self.text_t) is True and os.path.isdir(self.text_s) is True:
            self.button_sync.setDisabled(False)
            self.button_generate_mscript.setDisabled(False)
            self.button_launch_watchdog.setDisabled(False)

    def _open_file_dialog_target(self):
        target_path = str(QtWidgets.QFileDialog.getExistingDirectory())
        if target_path == "":
            return
        self.lineEdit_target.setText('{}'.format(target_path))
        print(target_path)
        global text_t
        text_t = self.text_t = target_path

        self.save_to_yaml(trg=text_t)

        if os.path.isdir(self.text_t) is True and os.path.isdir(self.text_s) is True:
            self.button_sync.setDisabled(False)
            self.button_generate_mscript.setDisabled(False)
            self.button_launch_watchdog.setDisabled(False)

    def _sync_directory(self):
        global text_s, text_t
        print("Source_path:", text_s)
        print("Target_path:", text_t)
        print(force_file_sync)
        sync(text_s, text_t, 'sync', create=True,
             force=force_file_sync, purge=True)

    def _enable_auto_flag(self):

        _translate = QtCore.QCoreApplication.translate
        
        if self.auto_flag:
            self.auto_flag = False
            self._generate_auto_py(self.auto_flag)
            self.button_generate_mscript.setText(
                _translate("TestQFileDialog", "Auto = OFF"))
            self.textEdit_m.setText('{}'.format(
                "Automation mode disabled. Application will now start normally. "))
        else:
            self.auto_flag = True
            self._generate_auto_py(self.auto_flag)
            self.button_generate_mscript.setText(
                _translate("TestQFileDialog", "Auto = ON"))
            self.textEdit_m.setText('{}'.format(
                "Automation mode enabled. Application will start minimized and launch Watchdog automatically. Configuration file is data.yml"))
        print("Autoflag set to:", self.auto_flag)

    def _generate_auto_py(self, auto_value):
        with open('data.yml') as outfile:
           doc = yaml.safe_load(outfile)
           doc['auto'] = auto_value
        with open('data.yml','w') as outfile:
            yaml.dump(doc, outfile)

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
                "Watchdog is currently monitoring the target directory for changes and syncing any changes automatically."))
        else:
            stop_threads = "1"

            self.button_launch_watchdog.setText(
                _translate("TestQFileDialog", "Watchdog disabled"))
            self.textEdit_m.setText('{}'.format(
                "Watchdog has been disabled - click the button again to re-activate."))

    def show_new_window(self, checked):
        global is_closed
        is_closed = True
        if self.l is True:
            self.textEdit_m.setText('{}'.format(
                "Select a removable media drive(USB, Portable SSD etc...) that you would like to monitor and sync on connection. You can specify a directory within the drive if you wish. This feature is made to work in conjunction with the ARS watchdog."))
            win = AnotherWindow(self)
            win.exec_()
            self.index = win.listWidget.currentRow()
            
            if self.index != -1 and is_closed == False:
                self.v = str(win.listWidget.currentItem().text())
                

                self.p = win.lineEdit.text()
                self.selected_drive_index = re.split('[:]', self.v)
                self.selected_drive_index[0] += ":" # Selected Drive
                self.selected_drive = self.selected_drive_index[0]
                #print(self.selected_drive)
                self.pre_populate_data()
            if win.checkBox_3.isChecked() == False:
                self.button_launch_watchdog.setDisabled(False)


        else:
            self.l.close()  # Close window.
            
            self.l = True

    def pre_populate_data(self):
        c = wmi.WMI()
        for drive in c.Win32_LogicalDisk():
            if drive.Caption == self.selected_drive:
                
                

                drive_brackets = "[" + str(drive.VolumeName) + "]"

                self.test = drive_brackets + self.remove_prefix(
                    self.p, drive_brackets)
                
                if toggle == "source":
                    #text_s = drive.Caption + self.remove_prefix(self.p, drive_brackets)
                    #print (text_s)
                    self.text_s = test = self.test
                    self.lineEdit_source.setText('{}'.format(self.test))
                    self.save_to_yaml(src=test)
                elif toggle == "target":
                    self.text_t = test = self.test
                    self.lineEdit_target.setText('{}'.format(self.test))
                    self.save_to_yaml(trg=test)
                else:
                    return

                    
            

    def remove_prefix(self, text, prefix):
        return text[text.startswith(prefix) and len(prefix):]

    def are_paths_valid(self):
        if os.path.isdir(text_t) is True and os.path.isdir(text_s) is True:
            self.button_sync.setDisabled(False)
            self.button_generate_mscript.setDisabled(False)
            self.button_launch_watchdog.setDisabled(False)
            return True

    def closeEvent(self, event):
        
            event.ignore()
            self.hide()
            self.trayicon.showMessage(
                "ARS File Sync",
                "Application was minimized to Tray",
                QSystemTrayIcon.Information,
                2000
            )


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
        self.pushButton_select.setDisabled(True) # Temp
        self.commandLinkButton_go.setDisabled(True)  # Temp
        self.pushButton_select.clicked.connect(self.target_directory_select)
        self.commandLinkButton_go.clicked.connect(self.close_window)
    
        self.checkBox.toggled.connect(self.checkbox_function)
        self.checkBox_2.toggled.connect(self.checkbox_function_2)
        self.checkBox_3.setChecked(True)
        self.checkBox.stateChanged.connect(self.button_state)
        self.checkBox_2.stateChanged.connect(self.button_state)

    def UiComponents(self):
        self.listWidget = self.findChild(QtWidgets.QListWidget, "listWidget")
        self.lineEdit = self.findChild(QtWidgets.QLineEdit, "lineEdit")
        self.commandLinkButton_go = self.findChild(QtWidgets.QCommandLinkButton, "commandLinkButton_go")
        self.pushButton_select = self.findChild(QtWidgets.QPushButton, "pushButton_select")
        self.checkBox = self.findChild(QtWidgets.QCheckBox, "checkBox")
        self.checkBox_2 = self.findChild(QtWidgets.QCheckBox, "checkBox_2")
        self.checkBox_3 = self.findChild(QtWidgets.QCheckBox, "checkBox_3")
        
    def button_state(self):
        if self.listWidget.currentRow() != -1:
            if self.checkBox.isChecked() or self.checkBox_2.isChecked() :
                self.pushButton_select.setDisabled(False)
                self.commandLinkButton_go.setDisabled(False)
            elif self.checkBox.isChecked() == False or self.checkBox_2.isChecked() == False:
                
                self.pushButton_select.setDisabled(True)
                self.commandLinkButton_go.setDisabled(True)
        else:
            self.pushButton_select.setDisabled(True)
            self.commandLinkButton_go.setDisabled(True)


    def selectionChanged(self):
        self.button_state()
        v = str(self.listWidget.currentItem().text())
        global current_drive_index# ['E:\\', '[USB_MIKE]']
        current_drive_index = re.split('[:]', v)
        current_drive_index[0] += ":\\"
        current_drive_index[1] = "[" + current_drive_index[1] + "]"
        self.lineEdit.setText('{}'.format(current_drive_index[1]))
         
        self.checkBox.setChecked(False)
        self.checkBox_2.setChecked(False)
        

    def checkbox_function(self):
        if self.checkBox.isChecked() :
            self.checkBox_2.setChecked(False)
            global toggle
            toggle = "source"
        
    def checkbox_function_2(self):
        if self.checkBox_2.isChecked() :
            self.checkBox.setChecked(False)
            global toggle
            toggle = "target"
        
    def close_window(self):
        global is_closed
        is_closed = False
        self.close()
        

    def target_directory_select(self):
        if self.checkBox.isChecked():
            global text_s
            
            target_path = text_s = str(QtWidgets.QFileDialog.getExistingDirectory(
                None, "", current_drive_index[0]))
            
            if os.path.isdir(target_path) is True:
                self.commandLinkButton_go.setDisabled(False) 
                append_index = re.split('[:]', target_path)
                append_index[0] = current_drive_index[1]
                 # ['[USB_MIKE]', '/Test_Folder']

                view_index = (''.join(str(x) for x in append_index))
                
            try:
                self.lineEdit.setText('{}'.format(view_index))
                
            except:
                text_s = ""
                return
            
        else:
            self.pushButton_select.setDisabled(True)
        if self.checkBox_2.isChecked():
            global text_t
            
            target_path = text_t = str(QtWidgets.QFileDialog.getExistingDirectory(
                None, "", current_drive_index[0]))
            
            if os.path.isdir(target_path) is True:
                self.commandLinkButton_go.setDisabled(False) 
                append_index = re.split('[:]', target_path)
                append_index[0] = current_drive_index[1]
                 # ['[USB_MIKE]', '/Test_Folder']
                
                view_index = (''.join(str(x) for x in append_index))
            try:
                self.lineEdit.setText('{}'.format(view_index))
            except:
                text_t =""
                return
            
        else:
            
            self.pushButton_select.setDisabled(True)
            return
        
        
class Watcher(Ui_MainWindow):

    def __init__(self, directory=".", handler=FileSystemEventHandler()):
        self.observer = Observer()
        pythoncom.CoInitialize()
        self.handler = handler
        self.directory = text_s
        self.valid_path_source = ""
        self.valid_path_target = ""


    def run(self):
        global text_s, text_t, valid_path_source_sync, valid_path_target_sync
        
        while self.is_drive_connected_source() != True and self.is_drive_connected_target() != True:  # Loop to detect target drive connection
            self.volume_letter_source = self.find_drive_source()
            self.volume_letter_target = self.find_drive_target()
            self.valid_path_source = self.get_full_path(self.volume_letter_source, text_s, "[" + str(self.volumeN_source) + "]")
            self.valid_path_target = self.get_full_path(self.volume_letter_target, text_t,"[" + str(self.volumeN_target) + "]")
            valid_path_source_sync = self.valid_path_source 
            valid_path_target_sync = self.valid_path_target 
            print("NOT CONNECTED", text_s, text_t, valid_path_source_sync, valid_path_target_sync)
            time.sleep(2)
        print("drive connected")
        if self.volume_letter_source != None and self.volume_letter_target != None:
            sync(self.valid_path_source, self.valid_path_target,
            'sync', force=force_file_sync, create=True, purge=True)
        

        self.observer.schedule(
            self.handler, self.valid_path_source, recursive=True)
        self.observer.start()

        try:
            while True:
                print("\nWatcher Running in {}/\n".format(self.directory))
                time.sleep(1)
                global stop_threads
                self.volume_letter_source = self.find_drive_source()
                self.volume_letter_target = self.find_drive_target()
                self.valid_path_source = valid_path_source_sync = self.get_full_path(
                    self.volume_letter_source, text_s, "[" + str(self.volumeN_source) + "]")
                self.valid_path_target = valid_path_target_sync = self.get_full_path(
                    self.volume_letter_target, text_t, "[" + str(self.volumeN_target) + "]")
                
                if stop_threads == "1":
                    self.observer.stop()
                    self.observer.join()
                    return
        except:
            self.observer.stop()
            self.observer.join()
        print("\nWatcher Terminated\n")

    def is_drive_connected_source(self):
        global text_s, text_t
        if os.path.isdir(self.valid_path_source):
            return True

    def is_drive_connected_target(self):
        if os.path.isdir(self.valid_path_target):
            return True


    def get_drive_letter(self, abb_path):
        self.m = re.search(r"\[([A-Za-z0-9_]+)\]", abb_path)
        if self.m:
            found = self.m.group(1)
            print(found)
            return found
        return ""
        

    def find_drive_source(self): ### WORK IN PROGRESS
        c = wmi.WMI()

        self.volumeN_source = self.get_drive_letter(text_s)
        
        for drive in c.Win32_LogicalDisk():
            if drive.VolumeName == self.volumeN_source:
                #print(drive.Caption)
                return drive.Caption

    def find_drive_target(self): ### WORK IN PROGRESS
        c = wmi.WMI()

        self.volumeN_target = self.get_drive_letter(text_t)
        
        for drive in c.Win32_LogicalDisk():
            if drive.VolumeName == self.volumeN_target:
                #print(drive.Caption)
                return drive.Caption


    def get_full_path(self, drive, path, volumeN):
        if os.path.isdir(path):
            return path
        self.path = str(drive) + path.replace(volumeN, "")
        #print(drive, path, volumeN)
        return self.path

class MyHandler(FileSystemEventHandler):

    def on_any_event(self, event):
        global text_s, text_t, valid_path_source_sync, valid_path_target_sync
        print(valid_path_source_sync, valid_path_target_sync, force_file_sync)
        sync(valid_path_source_sync, valid_path_target_sync, 'sync', force=force_file_sync, create=True, purge=True)


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
           #print("Working")
           #print("Starting " + self.name)
           w = Watcher(".", MyHandler())
           w.run()
           print("Exiting " + self.name)
           
           if stop_threads:
               return


if __name__ == "__main__":

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = Ui_MainWindow()
    sys.exit(app.exec_())
