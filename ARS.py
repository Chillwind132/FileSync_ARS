
from pathlib import Path
from pickle import FALSE, TRUE
from tkinter import N
from dirsync import sync
import os.path
import json
import pathlib
import jsonpickle
import time

def check_if_config_1stp():
    currentdir = Path(__file__).parent.absolute()
    v = str(currentdir)
    a = '\config.json'
    c = v + a
    if os.path.exists(c):
        with open('config.json', 'r') as f:
            config_loaded = json.load(f)
            src = config_loaded["source_path"]
    return src

def populate_data():
    mypath = r'C:\Users\Mike\Documents\Dest_Copy'
    nameSet=set()
    for file in os.listdir(mypath):
        fullpath=os.path.join(mypath, file)
        if os.path.isfile(fullpath):
            nameSet.add(file)

    retrievedSet=set()
    for name in nameSet:
        stat=os.stat(os.path.join(mypath, name))
        time=os.path.getmtime(os.path.join(mypath, name))
        size = os.path.getsize(os.path.join(mypath, name))
        retrievedSet.add((name, time, size))


    sampleJson = jsonpickle.encode(retrievedSet)
        #print('Saved set:', savedSet)
        #print('Saved JSON:', sampleJson)

    with open("data.json", "w") as jsonfile:
        json.dump(sampleJson, jsonfile)


def check_dir_change():
    currentdir = Path(__file__).parent.absolute()
    v = str(currentdir)
    a = '\data.json'
    c = v + a
    if os.path.exists(c):
        with open('data.json', 'r') as f:
            file_history_loaded = json.load(f)
            if file_history_loaded == '':
                print("data.json is empty! Scanning...")

                populate_data()

    else:
        with open("data.json", "w") as jsonfile:
            json.dump('0', jsonfile)
        populate_data()

    with open('data.json', 'r') as f:
        file_history_loaded = json.load(f)

    decodedSet = jsonpickle.decode(file_history_loaded)
    #print('Decoded set:', decodedSet)   

    #mypath=Path(__file__).parent.absolute()
    mypath = r'C:\Users\Mike\Documents\Source_Copy'

    nameSet=set()
    for file in os.listdir(mypath):
        fullpath=os.path.join(mypath, file)
        
        if  os.path.isfile(fullpath):
            nameSet.add(file)
        else:
            os.path.isdir(fullpath)
            nameSet.add(file)

   

    retrievedSet=set()
    for name in nameSet:
        stat=os.stat(os.path.join(mypath, name))
        time=os.path.getmtime(os.path.join(mypath, name))
        size=os.path.getsize(os.path.join(mypath, name)) 
        retrievedSet.add((name, time, size)) 
        

    if decodedSet != 0:
        newSet=retrievedSet-decodedSet
        deletedSet = decodedSet-retrievedSet
        print('NewSet:', newSet)
        print('DeletedSet:', deletedSet)

        isEmpty_1 = (len(newSet) == 0)
        isEmpty_2 = (len(deletedSet) == 0)

        if isEmpty_1 == False or isEmpty_2 == False:
            isEmpty = False
        else:
            isEmpty = True


        if isEmpty == True:
            print("No File Changes")
        else:
            print("File Changes")

        sampleJson = jsonpickle.encode(retrievedSet)
        #print('Saved set:', savedSet)
        #print('Saved JSON:', sampleJson)


        with open("data.json", "w") as jsonfile:
           json.dump(sampleJson, jsonfile)


        return isEmpty
    else:
        newSet = set()
    


#Get user input
def user_input():
    source_path = input (r"Enter the sync source directory:").strip()
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
    target_path = input (r"Enter the sync TARGET (folder):").strip()
    print(target_path)

    my_file = Path(target_path)
    if my_file.is_dir():
        print("Dir exists")
    else:    
        print("Dir does not exist, try again")

        isdir = os.path.isdir(target_path)
        while isdir == False:
            target_path = input (r"Enter the sync target directory:").strip()
            isdir = os.path.isdir(target_path)
            my_file = Path(target_path)
            if my_file.is_dir():
                print("Dir exists")
            else:
                print("Dir does not exist, try again")

    
    
    return source_path, target_path
    

#Save current config to JSON
def config_save(s_path, t_path, auto_flag):
    op_conf = {
        r"source_path" : s_path,
        r"target_path" : t_path,
        r'Automation Flag': auto_flag,
    }

    with open("config.json", "w") as jsonfile:
        json.dump(op_conf, jsonfile)



#load config from JSON
def load_config():
    with open('config.json', 'r') as f:
        config_loaded = json.load(f)

        src = config_loaded["source_path"]
        trg = config_loaded["target_path"]
    return src, trg
#Checks for automation flag; 1 = enabled
def check_auto_flag():
    currentdir = Path(__file__).parent.absolute()
    v = str(currentdir)
    a = '\config.json'
    c = v + a
    if os.path.exists(c):
        with open('config.json', 'r') as f:
            config_loaded = json.load(f)
            flag = config_loaded["Automation Flag"]
        return flag
    

#Check for Config file 
flag = check_auto_flag()

if flag == '1':
    print('Automation mode detected, loading the config and checking the target dir for any changes')
    print('To revert back to normal mode set "Automation Flag" to "0" in config.json')
    time.sleep(1)
    result = load_config()
    source_path = result[0]
    target_path = result[1]
    
    dir_flag = check_dir_change()
    if dir_flag == False:
        print('File Changes detected, syncing...')
        time.sleep(1)
        sync(source_path, target_path, 'sync', create=True)
    elif dir_flag == True:
        print('No File Changes detected since last scan')
    else:
        print('Unknown exception')

    
    quit()


dir_flag = check_dir_change()

currentdir = Path(__file__).parent.absolute()

v = str(currentdir)

a = '\config.json'
c = v + a
#print(c)

if os.path.exists(c):
    print("Automation mode disabled. You can enable it once you save the current config")

    if check_if_config_1stp() == '0':
        print("First time setup mode")
        dest_array = user_input()

        config_save(dest_array[0], dest_array[1], '0') # SAVE THE S AND T VALUES INTO CONFIG.JSON 

    print("Config found")
    verification = input ("Would you like to load the config and run the sync now? Or enter the configuration menu? Type y to sync, n to enter menu\n").strip()
    while verification != 'y' and verification != 'n':
        print('Invalid input')
        verification = input("Type y to sync, n to enter menu\n").strip()

    if verification == 'y':

        load_config()
        result = load_config()
        print(result)
        source_path = result[0]
        target_path = result[1]
    elif verification == 'n':
        result_userinput = user_input()
        print(result_userinput)
        source_path = result_userinput[0]
        target_path = result_userinput[1]
else:
    print("Config NOT found")
    result_userinput = user_input()
    print(result_userinput)
    source_path = result_userinput[0]
    target_path = result_userinput[1]




#source_path = 'C:\Users\Mike\Documents\Source_Copy'
#target_path = 'C:\Users\Mike\Documents\Dest_Copy'


sync(source_path,target_path,'sync', twoway=True, create=True)



verification_2 = input("Would you like to save the config and set up automation mode? Type y/n\n").strip()
if verification_2 == 'y':
    while verification_2 != 'y' and verification_2 != 'n':
        print('Invalid input')
        verification_2 = input("Would you like to save the config and set up automation mode? Type y/n\n").strip()

    if verification_2 == 'y':
        config_save(source_path, target_path, '0')
        print('Config Saved')
        verification_3 = input("Would you like to convert this script to monitor mode and set auto_flag = 1. Type y/n\n").strip()
        while verification_2 != 'y' and verification_2 != 'n':
            print('Invalid input')
            verification_3 = input("Would you like to convert this script to monitor mode and set auto_flag = 1. Type y/n\n").strip()
        if verification_3 == 'y':
            config_save(source_path, target_path, '1')
            print("Automation mode enabled and saved to config.json.")
            print("You can disable it by setting auto_flag property back to '0' ")
        else:
            print("Exiting...")
    elif verification_2 == 'n':
        print('Config not saved, automation mode can not function without config.json.')
        print('Exiting the script...')

       
        



        

