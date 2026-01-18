print("Smart Folder Organizer ")

import os
import shutil
import time
import json

# log func

def write_log(message):
    with open("log.txt", "a") as log:
         timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
         log.write(f"{timestamp} - {message}\n")

def write_undo(src, dst):
    with open("undo_log.txt", "a") as ulog:
        ulog.write(f"{dst}|{src}\n")

#undo fun

def undo_changes():
    if not os.path.exists("undo_log.txt"):
        print("No undo log found.")
        return

    with open("undo_log.txt", "r") as file:
        lines = file.readlines()
    
    if not lines:
        print("No actions to undo.")
        return

    for line in reversed(lines):
        dst, src = line.strip().split("|")

        if os.path.exists(dst):
            os,makedirs(os.path.dirname(src), exist_ok=True)
            shutil.move(dst, src)
            print(f"Reverted: {os.path.basename(dst)}")

    open("undo_log.txt", "w").close()
    write_log("Undo operation completed.")
    print("Undo operation completed.")


# user choice

choice = input("Type 'undo' to revert last organization or press Enter to continue: ").strip().lower()
if choice == "undo":
    undo_changes()
    exit()
      
# i/p

fpath = input("Enter the folder path to organize: ")

if not os.path.exists(fpath):
    print("The specified folder path does not exist.")
    exit()

if not os.path.isdir(fpath):
    print("The specified path is not a folder.")
    exit()

# dry run option

dry_run = input("Do you want to do a dry run? (yes/no): ").strip().lower() == "yes"
print("Dry run mode:", dry_run)

# load config
try:
    with open("config.json", "r") as cfg:
        extensions = json.load(cfg)
except Exception as e:
    print("config.json not found.")
    exit()
except json.JSONDecodeError:
    print("Invalid json format in config.json.")
    exit()


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
                     src = file_path
                     dst = destination
                     shutil.move(src, dst)

                     write_log(f"{file} -> {folder}")
                     write_undo(src, dst)
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
                src = file_path
                dst = destination
                shutil.move(src, dst)

                write_log(f"{file} -> Others")
                write_undo(src, dst)
                print(f"Moved: {file} -> Others folder")
            except Exception as e:
                print(f"Error moving file {file}: {e}")
                write_log(f"Error moving file {file}: {e}")
            
print("Folder Organization complete.")