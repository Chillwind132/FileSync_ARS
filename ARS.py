

from pathlib import Path
from dirsync import sync
import os.path
import json
import pathlib

#Check for Config file 
currentdir = Path(__file__).parent.absolute()

v = str(currentdir)

a = '\config.json'
c = v + a
print(c)

if os.path.exists(c):
     print("Config found")
else:
    print("Config NOT found")




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

#source_path = 'C:\Users\Mike\Documents\Source_Copy'
#target_path = 'C:\Users\Mike\Documents\Dest_Copy'

sync(source_path,target_path,'sync', twoway=True, create=True)

op_conf = {
    r"source_path" : source_path,
    r"target_path" : target_path,
}

with open("config.json", "w") as jsonfile:
    json.dump(op_conf, jsonfile)



