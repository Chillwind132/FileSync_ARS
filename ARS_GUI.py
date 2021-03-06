import re
import threading
import yaml
import wmi
import os.path
import time
import os
import sys
import pythoncom
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, LoggingEventHandler
from tkinter import EXCEPTION
from pathlib import Path
from dirsync import sync
from fileinput import close
from PyQt5 import QtCore, QtWidgets, uic, QtGui
from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, qApp
from PyQt5.QtGui import QIcon


class Ui_MainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        
        super(Ui_MainWindow, self).__init__()
        uic.loadUi('ARS.ui', self)  # Load the .ui file
        global stop_threads, text_t, text_s, is_closed, toggle
        stop_threads = True
        is_closed = True
        self.text_g = ""
        self.text_s = text_s = ""
        self.text_t = text_t = ""
        self.selected_drive = ""
        self.parameters = ""
        self.auto_flag = False
        self.l = True
        self.ctime = True
        self.force_file_sync = False
        self.create_dir = False
        self.two_way = False
        self.purge = False
        self.minimize_tray = False

        self.setWindowTitle("File Sync Menu")
        self.setWindowIcon(QtGui.QIcon("ars_icon"))
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

        self.pushButton_settings = self.findChild(
        QtWidgets.QPushButton, "pushButton_settings")
        self.pushButton_settings.clicked.connect(self.show_new_window_settings)

        self.pushButton_close = self.findChild(
            QtWidgets.QPushButton, "pushButton_close")
        self.pushButton_close.clicked.connect(self.quit_app_t)
        
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
            "Select your source and target directory for data synchronization.\n---\nIf you wish, you have an option to sync to a removable media - enable this option by clicking on the 'Drive' button.\n---\nWatchdog will monitor and sync any changes from the source directory. \n---\n'Auto' mode will start the application minimized and run watchdog automatically."))
        
        self.disambiguateTimer = QtCore.QTimer(self)
        self.disambiguateTimer.setSingleShot(True)
        self.disambiguateTimer.timeout.connect(
                self.disambiguateTimerTimeout)

        self.first_load() 

        self.update_menu()
        
        self.check_auto_flag()
        
    def show_new_window_settings(self):
        win_s = AnotherWindow_settings()
        win_s.exec_()

    def disambiguateTimerTimeout(self):
        print ("Tray icon single clicked")

    def update_menu(self):
        self.trayicon = QSystemTrayIcon(self)
        self.trayicon.setIcon(QIcon("ars_icon.ico"))
        self.menu = QMenu()
        self.dynamic_menu()

        self.trayicon.setContextMenu(self.menu)
        self.trayicon.setVisible(True)
        self.trayicon.activated.connect(self.onTrayIconActivated)

    def quit_app_t(self):
        self.load_yaml_config()
        if self.minimize_tray:
            self.hide()
            self.trayicon.showMessage(
                "ARS File Sync",
                "Application was minimized to Tray",
                QSystemTrayIcon.Information,
                2000
            )
        else:
            self.menu.close()
            self.trayicon.hide()
            global stop_threads
            stop_threads = True
            sys.exit()

    def onTrayIconActivated(self, reason):
        print ("onTrayIconActivated:", reason)
        if reason == QSystemTrayIcon.Trigger:
            self.disambiguateTimer.start(qApp.doubleClickInterval())
        elif reason == QSystemTrayIcon.DoubleClick:
            self.expand_menu()
            self.disambiguateTimer.stop()
            print ("Tray icon double clicked")

    def expand_menu(self):
        self.show()

    def dynamic_menu(self):
        self.menu.clear()
        checkAction = self.menu.addAction("Show Menu")
        checkAction.triggered.connect(self.show_main_window)
        if stop_threads is False:
            self.button_test_2 = self.menu.addAction("Stop Watchdog")
        else:
            self.button_test_2 = self.menu.addAction("Start Watchdog")
        self.button_test_2.triggered.connect(self._run_watchdog)
        
        self.quitAction = self.menu.addAction("Quit")
        self.quitAction.triggered.connect(self.hard_exit)

    def hard_exit(self):
        self.menu.close()
        self.trayicon.hide()
        global stop_threads
        stop_threads = True
        sys.exit()

    def check_auto_flag(self):
        _translate = QtCore.QCoreApplication.translate
        with open('data.yml') as outfile:
                doc = yaml.safe_load(outfile)
                if doc['auto']:
                    self.hide()
                    self.button_generate_mscript.setText(
                    _translate("TestQFileDialog", "Auto = ON"))
                    
                    self._run_watchdog()
                    self.dynamic_menu()
                    
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
                if doc['force']:
                    self.checkBox_force.setChecked(True)
                if os.path.isdir(text_t) is False or os.path.isdir(text_s) is False:
                    self.button_sync.setDisabled(True)
                    self.button_generate_mscript.setDisabled(True)
                    self.button_launch_watchdog.setDisabled(True)
                elif os.path.isdir(self.text_t) is True and os.path.isdir(self.text_t) is True:
                    self.button_sync.setDisabled(False)
                    self.button_generate_mscript.setDisabled(False)
                    self.button_launch_watchdog.setDisabled(False)
        
        else:
            with open('data.yml', 'w') as outfile:
                data = {
                    'src': '', 
                    'trg': '',
                    'auto': False,
                    'ctime': True,
                    'force': False,
                    'create': False,
                    'two_way': False,
                    'purge': False,
                    'minimize_tray': True,
                }
                yaml.dump(data, outfile)

    def save_to_yaml(self, **kwargs):
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
            elif i == "ctime":
                with open('data.yml') as outfile:
                   doc = yaml.safe_load(outfile)
                   doc['ctime'] = k
                with open('data.yml','w') as outfile:
                    yaml.dump(doc, outfile)
            elif i == "force":
                with open('data.yml') as outfile:
                   doc = yaml.safe_load(outfile)
                   doc['force'] = k
                with open('data.yml','w') as outfile:
                    yaml.dump(doc, outfile)
            elif i == "create":
                with open('data.yml') as outfile:
                   doc = yaml.safe_load(outfile)
                   doc['create'] = k
                with open('data.yml','w') as outfile:
                    yaml.dump(doc, outfile)
            elif i == "two_way":
                with open('data.yml') as outfile:
                   doc = yaml.safe_load(outfile)
                   doc['two_way'] = k
                with open('data.yml','w') as outfile:
                    yaml.dump(doc, outfile)
            elif i == "purge":
                with open('data.yml') as outfile:
                   doc = yaml.safe_load(outfile)
                   doc['purge'] = k
                with open('data.yml','w') as outfile:
                    yaml.dump(doc, outfile)
            elif i == "minimize_tray":
                with open('data.yml') as outfile:
                   doc = yaml.safe_load(outfile)
                   doc['minimize_tray'] = k
                with open('data.yml','w') as outfile:
                    yaml.dump(doc, outfile)
            
    def sync_parameters(self):
        if self.checkBox_force.isChecked():
            self.force_file_sync = True
            self.save_to_yaml(force=True)
        else:
            self.force_file_sync = False
            self.save_to_yaml(force=False)

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
       
        global text_t
        text_t = self.text_t = target_path

        self.save_to_yaml(trg=text_t)

        if os.path.isdir(self.text_t) is True and os.path.isdir(self.text_s) is True:
            self.button_sync.setDisabled(False)
            self.button_generate_mscript.setDisabled(False)
            self.button_launch_watchdog.setDisabled(False)

    def load_yaml_config(self):
        with open('data.yml') as outfile:
           doc = yaml.safe_load(outfile)
           self.ctime = doc['ctime']
           self.force_file_sync = doc['force'] 
           self.create_dir = doc['create']
           self.two_way = doc['two_way']
           self.purge = doc['purge']
           self.minimize_tray = doc['minimize_tray']

    def _sync_directory(self):
        global text_s, text_t
        self.load_yaml_config()
        self.volume_letter_source = self.find_drive_source()
        self.volume_letter_target = self.find_drive_target()
        self.valid_path_source = self.get_full_path(
            self.volume_letter_source, text_s, "[" + str(self.volumeN_source) + "]")
        self.valid_path_target = self.get_full_path(
            self.volume_letter_target, text_t, "[" + str(self.volumeN_target) + "]")
        try:
            sync(self.valid_path_source, self.valid_path_target, 'sync', verbose=True, ctime=self.ctime, force=self.force_file_sync, create=self.create_dir,
             twoway=self.two_way, purge=self.purge)
        except Exception:
            self.textEdit_m.setText('{}'.format(
                "Sync argument exception! 'Create files' setting not enabled? "))
        

    def get_drive_letter(self, abb_path):
        self.m = re.search(r"\[([A-Za-z0-9_]+)\]", abb_path)
        if self.m:
            found = self.m.group(1)
            
            return found
        return ""
        
    def find_drive_source(self): 
        c = wmi.WMI()
        self.volumeN_source = self.get_drive_letter(text_s)
        for drive in c.Win32_LogicalDisk():
            if drive.VolumeName == self.volumeN_source:
                
                return drive.Caption

    def find_drive_target(self): 
        c = wmi.WMI()

        self.volumeN_target = self.get_drive_letter(text_t)
        
        for drive in c.Win32_LogicalDisk():
            if drive.VolumeName == self.volumeN_target:
               
                return drive.Caption

    def get_full_path(self, drive, path, volumeN):
        if (path.find(str(drive)) != -1):
            return path
        self.path = str(drive) + path.replace(volumeN, "")
        
        return self.path

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
        self.save_to_yaml(src=text_s)
        text_t = self.text_t = self.lineEdit_target.text()
        self.save_to_yaml(trg=text_t)
        
        if os.path.isdir(text_t) is False or os.path.isdir(text_s) is False:
            self.button_sync.setDisabled(True)
            self.button_generate_mscript.setDisabled(True)
            self.button_launch_watchdog.setDisabled(True)
            
        elif os.path.isdir(self.text_t) is True and os.path.isdir(self.text_t) is True:
            self.button_sync.setDisabled(False)
            self.button_generate_mscript.setDisabled(False)
            self.button_launch_watchdog.setDisabled(False)
            
        if self.checkBox_override.isChecked():
            self.button_sync.setDisabled(False)
            self.button_generate_mscript.setDisabled(False)
            self.button_launch_watchdog.setDisabled(False)

    def _run_watchdog(self):
        global stop_threads

        _translate = QtCore.QCoreApplication.translate
        thread1 = myThread(1, "Thread-1", 1)

        if stop_threads:
            try:
                self._sync_directory()
            except Exception:
                self.textEdit_m.setText('{}'.format("Sync argument exception! Watchdog disabled. 'Create files' setting not enabled? "))
                return
            thread1.start()
            stop_threads = False
            self.button_launch_watchdog.setText(
                _translate("TestQFileDialog", "Watchdog running..."))
            self.textEdit_m.setText('{}'.format(
                "Watchdog is currently monitoring the source folder for any changes and syncing new data to the target directory automatically."))
        else:
            stop_threads = True

            self.button_launch_watchdog.setText(
                _translate("TestQFileDialog", "Watchdog disabled"))
            self.textEdit_m.setText('{}'.format(
                "Watchdog has been disabled - click the 'Watchdog' button again to re-activate."))
        self.dynamic_menu()

    def show_new_window(self, checked):
        global is_closed
        is_closed = True
        if self.l is True:
            self.textEdit_m.setText('{}'.format(
                "Select a media drive(USB, Portable SSD etc...) that you would like to monitor and sync to or from on connection. You can specify a directory within the drive if you wish. This feature is made to work in conjunction with the ARS watchdog.\n --- \nPlease note that the drive does not have to be connected in order for this feature to work - you can reference a drive by its volumeName in this format: [USB_MIKE]/Test_Folder"))
            win = AnotherWindow(self)
            win.exec_()
            self.index = win.listWidget.currentRow()
            
            if self.index != -1 and is_closed is False:
                self.v = str(win.listWidget.currentItem().text())
                self.p = win.lineEdit.text()
                self.selected_drive_index = re.split('[:]', self.v)
                self.selected_drive_index[0] += ":" # Selected Drive
                self.selected_drive = self.selected_drive_index[0]
                
                self.pre_populate_data()
            if win.checkBox_3.isChecked() is False:
                self.button_launch_watchdog.setDisabled(False)
        
    def pre_populate_data(self):
        c = wmi.WMI()
        for drive in c.Win32_LogicalDisk():
            if drive.Caption == self.selected_drive:
                drive_brackets = "[" + str(drive.VolumeName) + "]"
                self.test = drive_brackets + self.remove_prefix(
                    self.p, drive_brackets)
                if toggle == "source":
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
        self.load_yaml_config()
        if self.minimize_tray:
            event.ignore()
            self.hide()
            self.trayicon.showMessage(
                "ARS File Sync",
                "Application was minimized to Tray",
                QSystemTrayIcon.Information,
                2000
            )
        else:
            self.close()


class AnotherWindow(QtWidgets.QDialog):
    def __init__(self, parent=Ui_MainWindow):

        super(AnotherWindow, self).__init__()
        uic.loadUi('Dialog.ui', self)  # Load the .ui file
        self.setWindowTitle("Drive Selection Menu")
        self.drive_volume_to_monitor()
        
    def drive_volume_to_monitor(self):
        c = wmi.WMI()
        for drive in c.Win32_LogicalDisk():
            drive_letter = str(drive.Caption) + str(drive.VolumeName)
            self.listWidget.addItem(drive_letter)

        self.listWidget.itemSelectionChanged.connect(self.selectionChanged)
        self.pushButton_select.setDisabled(True) 
        self.commandLinkButton_go.setDisabled(True)  
        self.pushButton_select.clicked.connect(self.target_directory_select)
        self.commandLinkButton_go.clicked.connect(self.close_window)
    
        self.checkBox.toggled.connect(self.checkbox_function)
        self.checkBox_2.toggled.connect(self.checkbox_function_2)
        
        self.checkBox.stateChanged.connect(self.button_state)
        self.checkBox_2.stateChanged.connect(self.button_state)
        self.checkBox_3.setChecked(True)
        self.checkBox_3.setEnabled(False)

    def UiComponents(self):
        self.listWidget = self.findChild(QtWidgets.QListWidget, "listWidget")
        self.lineEdit = self.findChild(QtWidgets.QLineEdit, "lineEdit")
        self.commandLinkButton_go = self.findChild(QtWidgets.QCommandLinkButton, "commandLinkButton_go")
        self.pushButton_select = self.findChild(QtWidgets.QPushButton, "pushButton_select")
        self.checkBox = self.findChild(QtWidgets.QCheckBox, "checkBox")
        self.checkBox_2 = self.findChild(QtWidgets.QCheckBox, "checkBox_2")
        self.checkBox_3 = self.findChild(QtWidgets.QCheckBox, "checkBox_3")
    
    def save_to_yaml(self, **kwargs):
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
            elif i == "ctime":
                with open('data.yml') as outfile:
                   doc = yaml.safe_load(outfile)
                   doc['ctime'] = k
                with open('data.yml','w') as outfile:
                    yaml.dump(doc, outfile)
            elif i == "force":
                with open('data.yml') as outfile:
                   doc = yaml.safe_load(outfile)
                   doc['force'] = k
                with open('data.yml','w') as outfile:
                    yaml.dump(doc, outfile)
            elif i == "create":
                with open('data.yml') as outfile:
                   doc = yaml.safe_load(outfile)
                   doc['create'] = k
                with open('data.yml','w') as outfile:
                    yaml.dump(doc, outfile)
            elif i == "two_way":
                with open('data.yml') as outfile:
                   doc = yaml.safe_load(outfile)
                   doc['two_way'] = k
                with open('data.yml','w') as outfile:
                    yaml.dump(doc, outfile)
            elif i == "purge":
                with open('data.yml') as outfile:
                   doc = yaml.safe_load(outfile)
                   doc['purge'] = k
                with open('data.yml','w') as outfile:
                    yaml.dump(doc, outfile)
            elif i == "minimize_tray":
                with open('data.yml') as outfile:
                   doc = yaml.safe_load(outfile)
                   doc['minimize_tray'] = k
                with open('data.yml','w') as outfile:
                    yaml.dump(doc, outfile)

    def load_yaml_config(self):
        with open('data.yml') as outfile:
           doc = yaml.safe_load(outfile)
           self.ctime = doc['ctime']
           self.force_file_sync = doc['force'] 
           self.create_dir = doc['create']
           self.two_way = doc['two_way']
           self.purge = doc['purge']
           self.minimize_tray = doc['minimize_tray']
        
    def button_state(self):
        if self.listWidget.currentRow() != -1:
            if self.checkBox.isChecked() or self.checkBox_2.isChecked() :
                self.pushButton_select.setDisabled(False)
                self.commandLinkButton_go.setDisabled(False)
            elif self.checkBox.isChecked() is False or self.checkBox_2.isChecked() is False:
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
                self.save_to_yaml(src=view_index)
            except Exception:
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
                view_index = (''.join(str(x) for x in append_index))
            try:
                self.lineEdit.setText('{}'.format(view_index))
                self.save_to_yaml(trg=view_index)
            except Exception:
                text_t =""
                return
        else:
            self.pushButton_select.setDisabled(True)
            return
        

class AnotherWindow_settings(QtWidgets.QDialog):
    def __init__(self, parent=Ui_MainWindow):
        
        super(AnotherWindow_settings, self).__init__()
        uic.loadUi('Dialog_s.ui', self)  # Load the .ui file
        self.setWindowTitle("Settings")
        self.create_dir = True
        self.two_way = True
        self.purge = True
        self.minimize_tray = True
        self.button_connect()
        self.load_yaml_config()
        self.dynamic_updates()
        self.update_values()
        
    def UiComponents(self):
        self.checkBox_create = self.findChild(
            QtWidgets.QCheckBox, "checkBox_create")
        self.checkBox_twoway = self.findChild(
            QtWidgets.QCheckBox, "checkBox_twoway")
        self.checkBox_purge = self.findChild(
            QtWidgets.QCheckBox, "checkBox_purge")
        self.checkBox_minimize = self.findChild(
            QtWidgets.QCheckBox, "checkBox_minimize")
        
    def button_connect(self):
        self.checkBox_create.toggled.connect(self.update_values)
        self.checkBox_twoway.toggled.connect(self.update_values)
        self.checkBox_purge.toggled.connect(self.update_values)
        self.checkBox_minimize.toggled.connect(self.update_values)
        
    def dynamic_updates(self):
        if self.create_dir:
            self.checkBox_create.setChecked(True)
        if self.two_way:
            self.checkBox_twoway.setChecked(True)
        if self.purge:
            self.checkBox_purge.setChecked(True)
        if self.minimize_tray:
            self.checkBox_minimize.setChecked(True)
        
    def update_values(self):
        if self.checkBox_create.isChecked():
            self.save_to_yaml(create=True)
        else:
            self.save_to_yaml(create=False)
        if self.checkBox_twoway.isChecked():
            self.save_to_yaml(two_way=True)
        else:
            self.save_to_yaml(two_way=False)
        if self.checkBox_purge.isChecked():
            self.save_to_yaml(purge=True)
        else:
            self.save_to_yaml(purge=False)
        if self.checkBox_minimize.isChecked():
            self.save_to_yaml(minimize_tray=True)
        else:
            self.save_to_yaml(minimize_tray=False)

    def save_to_yaml(self, **kwargs):
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
            elif i == "ctime":
                with open('data.yml') as outfile:
                   doc = yaml.safe_load(outfile)
                   doc['ctime'] = k
                with open('data.yml','w') as outfile:
                    yaml.dump(doc, outfile)
            elif i == "force":
                with open('data.yml') as outfile:
                   doc = yaml.safe_load(outfile)
                   doc['force'] = k
                with open('data.yml','w') as outfile:
                    yaml.dump(doc, outfile)
            elif i == "create":
                with open('data.yml') as outfile:
                   doc = yaml.safe_load(outfile)
                   doc['create'] = k
                with open('data.yml','w') as outfile:
                    yaml.dump(doc, outfile)
            elif i == "two_way":
                with open('data.yml') as outfile:
                   doc = yaml.safe_load(outfile)
                   doc['two_way'] = k
                with open('data.yml','w') as outfile:
                    yaml.dump(doc, outfile)
            elif i == "purge":
                with open('data.yml') as outfile:
                   doc = yaml.safe_load(outfile)
                   doc['purge'] = k
                with open('data.yml','w') as outfile:
                    yaml.dump(doc, outfile)
            elif i == "minimize_tray":
                with open('data.yml') as outfile:
                   doc = yaml.safe_load(outfile)
                   doc['minimize_tray'] = k
                with open('data.yml','w') as outfile:
                    yaml.dump(doc, outfile)

    def load_yaml_config(self):
        with open('data.yml') as outfile:
           doc = yaml.safe_load(outfile)
           self.force_file_sync = doc['force'] 
           self.create_dir = doc['create']
           self.two_way = doc['two_way']
           self.purge = doc['purge']
           self.minimize_tray = doc['minimize_tray']


class Watcher(Ui_MainWindow):

    def __init__(self, directory=".", handler=FileSystemEventHandler()):
        
        event_handler = LoggingEventHandler()
        pythoncom.CoInitialize()
        self.observer = Observer()
        self.handler = handler
        self.directory = text_s
        self.valid_path_source = ""
        self.valid_path_target = ""
        self.check_1 = ""
        self.check_2 = ''
        self.volume_letter_source = None
        self.volume_letter_target = None
        self.unscheduled = False

    def run(self):
        global text_s, text_t, stop_threads 
        self.load_yaml_config()
        while self.volume_letter_source is None or self.volume_letter_target is None: # Loop to detect target drive connection
           
            self.load_yaml_config()
            self.volume_letter_source = self.find_drive_source()
            self.volume_letter_target = self.find_drive_target()
            self.valid_path_source = self.get_full_path(self.volume_letter_source, text_s, "[" + str(self.volumeN_source) + "]")
            self.valid_path_target = self.get_full_path(self.volume_letter_target, text_t,"[" + str(self.volumeN_target) + "]")
            
            time.sleep(2)
        
        if self.volume_letter_source is not None and self.volume_letter_target is not None:
        
                sync(self.valid_path_source, self.valid_path_target,
                 'sync', ctime=self.ctime, verbose=True, force=self.force_file_sync, create=self.create_dir,
                 twoway=self.two_way, purge=self.purge)

                self.watch_id = self.observer.schedule(self.handler, self.valid_path_source, recursive=True)
                self.observer.start()
    
        while True:
                print("\nWatcher Running in {}/\n".format(self.directory))
                time.sleep(1)
                
                self.volume_letter_source = self.find_drive_source()
                self.volume_letter_target = self.find_drive_target()
                self.valid_path_source = valid_path_source_sync = self.get_full_path(
                    self.volume_letter_source, text_s, "[" + str(self.volumeN_source) + "]")
                self.valid_path_target = valid_path_target_sync = self.get_full_path(
                    self.volume_letter_target, text_t, "[" + str(self.volumeN_target) + "]")
                if self.volume_letter_source is None or self.volume_letter_target is None: 
                    
                    self.observer.unschedule_all()
                    self.unscheduled = True

                if self.volume_letter_source is not None and self.unscheduled is True:
                    self.observer.schedule(
                        self.handler, self.valid_path_source, recursive=True)
                    self.unscheduled = False
                    
                if stop_threads is True:
                    self.observer.stop()
                    self.observer.join()
                    return
        
        print("\nWatcher Terminated\n")

    def load_yaml_config(self):
        with open('data.yml') as outfile:
           doc = yaml.safe_load(outfile)
           self.force_file_sync = doc['force'] 
           self.create_dir = doc['create']
           self.two_way = doc['two_way']
           self.purge = doc['purge']
           self.minimize_tray = doc['minimize_tray']
           self.ctime = doc['ctime']
        

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
            
            return found
        return ""
        
    def find_drive_source(self): 
        c = wmi.WMI()

        self.volumeN_source = self.get_drive_letter(text_s)
        
        for drive in c.Win32_LogicalDisk():
            if drive.VolumeName == self.volumeN_source:
                
                return drive.Caption

    def find_drive_target(self): 
        c = wmi.WMI()

        self.volumeN_target = self.get_drive_letter(text_t)
        
        for drive in c.Win32_LogicalDisk():
            if drive.VolumeName == self.volumeN_target:
                
                return drive.Caption

    def get_full_path(self, drive, path, volumeN):
        if (path.find(str(drive)) != -1):
            return path
        self.path = str(drive) + path.replace(volumeN, "")
        
        return self.path


class MyHandler(FileSystemEventHandler):
    
    def on_any_event(self, event):
        
        global text_s, text_t
        self.load_yaml_config()

        self.volume_letter_source = self.find_drive_source()
        self.volume_letter_target = self.find_drive_target()
        self.valid_path_source = valid_path_source_sync = self.get_full_path(
            self.volume_letter_source, text_s, "[" + str(self.volumeN_source) + "]")
        self.valid_path_target = valid_path_target_sync = self.get_full_path(
            self.volume_letter_target, text_t, "[" + str(self.volumeN_target) + "]")

        time.sleep(1)
        sync(valid_path_source_sync, valid_path_target_sync, 'sync', verbose=True, ctime=self.ctime, force=self.force_file_sync, create=self.create_dir,
        twoway=self.two_way, purge=self.purge)

    def find_drive_source(self): 
        pythoncom.CoInitialize()
        c = wmi.WMI()

        self.volumeN_source = self.get_drive_letter(text_s)
        
        for drive in c.Win32_LogicalDisk():
            if drive.VolumeName == self.volumeN_source:
                
                return drive.Caption
    def find_drive_target(self): 
        c = wmi.WMI()

        self.volumeN_target = self.get_drive_letter(text_t)

        for drive in c.Win32_LogicalDisk():
            if drive.VolumeName == self.volumeN_target:
                
                return drive.Caption

    def get_full_path(self, drive, path, volumeN):
        if (path.find(drive) != -1):
            return path
        self.path = str(drive) + path.replace(volumeN, "")
        
        return self.path

    def load_yaml_config(self):
        with open('data.yml') as outfile:
           doc = yaml.safe_load(outfile)
           self.ctime = doc['ctime']
           self.force_file_sync = doc['force'] 
           self.create_dir = doc['create']
           self.two_way = doc['two_way']
           self.purge = doc['purge']
           self.minimize_tray = doc['minimize_tray']

    def get_drive_letter(self, abb_path):
        self.m = re.search(r"\[([A-Za-z0-9_]+)\]", abb_path)
        if self.m:
            found = self.m.group(1)
            return found
        return ""

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
           w = Watcher(".", MyHandler())
           w.run()
           print("Exiting " + self.name)
           
           if stop_threads:
               return

if __name__ == "__main__":

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = Ui_MainWindow()
    sys.exit(app.exec_())
