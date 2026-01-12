print("Smart Folder Organizer ")
import os
fpath = input("Enter the folder path to organize: ")
if not os.path.exists(fpath):
    print("The specified folder path does not exist.")
else:
    print("Files in folder")
    for item in os.listdir(fpath):
        print(item)