
from pathlib import Path
from tkinter import N
from dirsync import sync
import os.path
import json
import pathlib

#load config from JSON
def load_config():
    with open('config.json', 'r') as f:
        config_loaded = json.load(f)
    
        src = config_loaded["source_path"]
        trg = config_loaded["target_path"]
    return src, trg


#Get user input
def user_input():
    source_path = input (r"Enter the sync SOURCE (folder):").strip()
    print(source_path)

    my_file = Path(source_path)
    if my_file.is_dir():
        print("Dir exists")
    else:
        print("Dir does not exist, try again")

        isdir = os.path.isdir(source_path)
        while isdir == False:
            source_path = input (r"Enter the sync SOURCE (folder):").strip()
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
            target_path = input (r"Enter the sync TARGET (folder):").strip()
            isdir = os.path.isdir(target_path)
            my_file = Path(target_path)
            if my_file.is_dir():
                print("Dir exists")
            else:
                print("Dir does not exist, try again")
    return source_path, target_path

def config_save(s_path, t_path):
    op_conf = {
        r"source_path" : s_path,
        r"target_path" : t_path,
    }

    with open("config.json", "w") as jsonfile:
        json.dump(op_conf, jsonfile)



#Check for Config file 
currentdir = Path(__file__).parent.absolute()

v = str(currentdir)

a = '\config.json'
c = v + a
print(c)

if os.path.exists(c):
    print("Config found")
    verification = input ("Would you like to load the config? Type y/n\n").strip()
    while verification != 'y' and verification != 'n':
        print('Invalid input')
        verification = input ("Would you like to load the config? Type y/n\n").strip()

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

if verification == 'n':
    verification_2 = input ("Would you like to save the config? Type y/n\n").strip()
    while verification_2 != 'y' and verification_2 != 'n':
        print('Invalid input')
        verification_2 = input ("Would you like to save the config? Type y/n\n").strip()

    if verification_2 == 'y':
        config_save(source_path, target_path)
        print('Config Saved')



