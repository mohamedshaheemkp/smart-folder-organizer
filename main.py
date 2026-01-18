print("Smart Folder Organizer ")

import os
import shutil
import time

#log

def write_log(message):
    with open("log.txt", "a") as log:
         timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
         log.write(f"{timestamp} - {message}\n")

def write_undo(src, dst):
    with open("undo_log.txt", "a") as ulog:
        ulog.write(f"{dst}|{src}\n")
         
#i/p

fpath = input("Enter the folder path to organize: ")

if not os.path.exists(fpath):
    print("The specified folder path does not exist.")
    exit()

if not os.path.isdir(fpath):
    print("The specified path is not a folder.")
    exit()

#dry run option

dry_run = input("Do you want to do a dry run? (yes/no): ").strip().lower() == "yes"
print("Dry run mode:", dry_run)

# file extensions and their corresponding folders

extensions = {
        'Images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff'],
        'Documents': ['.pdf', '.docx', '.txt', '.xlsx', '.pptx'],
        'Audio': ['.mp3', '.wav', '.aac', '.flac'], 
        'Videos': ['.mp4', '.avi', '.mov', '.mkv'],
        'Archives': ['.zip', '.rar', '.tar', '.gz'],
        'Scripts': ['.py', '.js', '.sh', '.bat'],
        'Programs': ['.exe', '.msi', '.dmg']}

# organization logic

try:
    files = os.listdir(fpath)
except PermissionError:
    print("Permission denied to access the folder.")
    exit()

for file in files:
    file_path = os.path.join(fpath, file)

# skip folders and shortcuts

    if not os.path.isfile(file_path):
        continue
    
    moved = False
    file_lower = file.lower()

    for folder, exts in extensions.items():
        if file_lower.endswith(tuple(exts)):
            if dry_run:
                 print(f"[DRY RUN] {file} -> {folder}")
            else:
                 target_folder = os.path.join(fpath, folder)
                 os.makedirs(target_folder, exist_ok=True)

                 destination = os.path.join(target_folder, file)

                 try:
                     shutil.move(file_path, destination)
                     write_log(f"{file} -> {folder}")
                     write_undo(file_path, destination)
                     print(f"Moved: {file} -> {folder} folder")
                 except Exception as e:
                    print(f"Error moving file {file}: {e}")
                    write_log(f"Error moving file {file}: {e}")

            moved = True
            break


#others folder logic

    if not moved:
         if dry_run:
            print(f"[DRY RUN] {file} -> Others")
         else:
            other_folder = os.path.join(fpath, 'Others')
            os.makedirs(other_folder, exist_ok=True)

            destination = os.path.join(other_folder, file)

            try:
                shutil.move(file_path, destination)
                write_log(f"{file} -> Others")
                write_undo(file_path, destination)
                print(f"Moved: {file} -> Others folder")
            except Exception as e:
                print(f"Error moving file {file}: {e}")
                write_log(f"Error moving file {file}: {e}")
            
print("Folder Organization complete.")