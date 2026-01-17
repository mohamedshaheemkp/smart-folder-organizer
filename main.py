print("Smart Folder Organizer ")
import os
fpath = input("Enter the folder path to organize: ")
if not os.path.exists(fpath):
    print("The specified folder path does not exist.")
else:
    print("Files in folder")
    for item in os.listdir(fpath):
        print(item)
    extensions = {
        'Images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff'],
        'Documents': ['.pdf', '.docx', '.txt', '.xlsx', '.pptx'],
        'Audio': ['.mp3', '.wav', '.aac', '.flac'], 
        'Videos': ['.mp4', '.avi', '.mov', '.mkv'],
        'Archives': ['.zip', '.rar', '.tar', '.gz'],
        'Scripts': ['.py', '.js', '.sh', '.bat']}
    files = os.listdir(fpath)
    for files in files:
        file_path = os.path.join(fpath,files)
        if os.path.isfile(file_path):
            moved = False
        for folder, exts in extensions.items():
            if files.lower().endswith(tuple(exts)):
                target_folder = os.path.join(fpath, folder)
                os.makedirs(target_folder, exist_ok=True)
                os.rename(file_path, os.path.join(target_folder, files))
                print(f"Moved: {files} ➡️ {folder} folder")
                moved = True
                break
        if not moved:
                other_folder = os.path.join(fpath, 'Others')
                os.makedirs(other_folder, exist_ok=True)
                os.rename(file_path, os.path.join(other_folder, files))
                print(f"Moved: {files} ➡️ Others folder")