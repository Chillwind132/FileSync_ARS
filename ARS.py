from ast import excepthandler
from pathlib import Path
from pickle import FALSE, TRUE
from tkinter import N
from dirsync import sync
import os.path
import json
import pathlib
import jsonpickle
import time


def check_config_present():
    currentdir = Path(__file__).parent.absolute()
    fullpath = os.path.join(currentdir, 'config.json')
    if os.path.exists(fullpath):
        config_exists = True
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
    }
    json_string = json.dumps(data)
    with open("config.json", "w") as jsonfile:
        json.dump(data, jsonfile)


def load_config():
    mypath = Path(__file__).parent.absolute()
    fullpath = os.path.join(mypath, 'config.json')
    if os.path.isfile(fullpath):
        print("Config.json exists - Loading....")
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
        print("Data.json exists - Loading....")
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
        retrievedSet.add((name, time, size))
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
        current_files_set_now.add((name, time, size))

    global new_files_set
    global deleted__files_set
    global Directory_change_bool

    new_files_set = current_files_set_now - file_history_snapshot_set
    deleted__files_set = file_history_snapshot_set - current_files_set_now

    files_deleted_bool = (len(new_files_set) == 0)
    files_added_bool = (len(deleted__files_set) == 0)

    if files_added_bool == False or files_deleted_bool == False:
        Directory_change_bool = True
    else:

        Directory_change_bool = False

    return Directory_change_bool


if check_auto_flag() == '1':
    if check_config_present() == False:
        print("Log error to excel placeholder")
    elif check_data_present() == False:
        print("Log error to excel placeholder")
    else:
        load_config()
        load_data()

        if check_dir_for_changes() == True:
            print('File Changes are detected. Syncing...')
            sync(source_path, target_path, 'sync', create=True)
            
        else:
            print('No File changes detected since last ran.')

        populate_data()
        print('File data updated. Exiting...')
        time.sleep(1)
        quit()

if check_config_present() == False:
    first_ran_func()
    user_input()
    config_save('0')
else:
    load_config()
ask_user_sync()

if ask_user_sync_anwser == 'y':
    try:
        sync(source_path, target_path, 'sync', create=True)
    except ValueError as exception:
        print('There was a problem with loading the config, please reconfigure the source and target path values.\n')
        print(r'For example: Correct input format - C:\Users\Mike\Documents\Source_Copy')
        quit()
    else:
        print('Unknow sync error, exiting')
        quit()
else:
    user_input()
    config_save('0')


populate_data()


ask_user_automation()

#source_path = 'C:\Users\Mike\Documents\Source_Copy'
#target_path = 'C:\Users\Mike\Documents\Dest_Copy'
