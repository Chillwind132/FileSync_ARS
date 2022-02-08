
from pathlib import Path
from dirsync import sync
import os.path
source_path = input (r"Enter the sync source (folder):").strip()
#source_path.strip()
print(source_path)

my_file = Path(source_path)
if my_file.is_dir():
    print("Dir exists")
else:
    print("Dir does not exist, try again")

    isdir = os.path.isdir(source_path)
    while isdir == False:
        source_path = input (r"Enter the sync source (folder):").strip()
        isdir = os.path.isdir(source_path)
        if my_file.is_dir():
            print("Dir exists")



target_path = input (r"Enter the sync target (folder):").strip()
print(target_path)


#source_path = 'C:\Users\Mike\Documents\Source_Copy'
#target_path = 'C:\Users\Mike\Documents\Dest_Copy'

sync(source_path,target_path,'sync', twoway=True, create=True)

