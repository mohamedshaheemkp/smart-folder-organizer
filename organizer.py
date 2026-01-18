print("Smart Folder Organizer")

import os
import shutil
import time
import json
import argparse
import tkinter as tk
from tkinter import filedialog, messagebox

# ---------------- LOG FUNCTIONS ---------------- #

def write_log(message):
    with open("log.txt", "a") as log:
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        log.write(f"{timestamp} - {message}\n")

def write_undo(src, dst):
    with open("undo_log.txt", "a") as ulog:
        ulog.write(f"{dst}|{src}\n")

# ------------------ SUMMARY -------------------- #
summary = {}

def update_summary(folder):
    summary[folder] = summary.get(folder, 0) + 1

def write_summary():
    with open("summary.txt", "w") as s:
        s.write("Smart Folder Organizer Summary\n")
        for folder, count in summary.items():
            s.write(f"{folder}: {count} files\n")

# ---------------- UNDO FUNCTION ---------------- #

def undo_changes():
    if not os.path.exists("undo_log.txt"):
        return "No undo log found."

    with open("undo_log.txt", "r") as file:
        lines = file.readlines()

    if not lines:
        return "No actions to undo."

    for line in reversed(lines):
        dst, src = line.strip().split("|")
        if os.path.exists(dst):
            os.makedirs(os.path.dirname(src), exist_ok=True)
            shutil.move(dst, src)

    open("undo_log.txt", "w").close()
    write_log("Undo operation completed.")
    return "Undo operation completed."

# ---------------- LOAD CONFIG ---------------- #

def load_config():
    try:
        with open("config.json", "r") as cfg:
            return json.load(cfg)
    except Exception as e:
        return None

# ---------------- ORGANIZE FUNCTION ---------------- #
# (UNCHANGED LOGIC, JUST RETURN STRINGS)

def organize_files(fpath, extensions, dry_run=False):
    if not os.path.exists(fpath):
        return "Folder does not exist."

    if not os.path.isdir(fpath):
        return "Not a valid folder."

    try:
        files = os.listdir(fpath)
    except PermissionError:
        return "Permission denied."

    for file in files:
        file_path = os.path.join(fpath, file)

        if not os.path.isfile(file_path):
            continue

        moved = False
        file_lower = file.lower()

        for folder, exts in extensions.items():
            if file_lower.endswith(tuple(exts)):
                target_folder = os.path.join(fpath, folder)
                destination = os.path.join(target_folder, file)

                if not dry_run:
                    os.makedirs(target_folder, exist_ok=True)
                    shutil.move(file_path, destination)
                    write_log(f"{file} -> {folder}")
                    write_undo(file_path, destination)

                moved = True
                break

        if not moved:
            other_folder = os.path.join(fpath, "Others")
            destination = os.path.join(other_folder, file)

            if not dry_run:
                os.makedirs(other_folder, exist_ok=True)
                shutil.move(file_path, destination)
                write_log(f"{file} -> Others")
                write_undo(file_path, destination)

    return "Dry run completed." if dry_run else "Folder organization complete."

# ==================================================
# ===================== CLI ========================
# ==================================================

def cli_mode():   # ADDED
    parser = argparse.ArgumentParser(description="Smart Folder Organizer")
    parser.add_argument("fpath", help="Folder path")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--undo", action="store_true")
    args = parser.parse_args()

    if args.undo:
        print(undo_changes())
        return

    extensions = load_config()
    if not extensions:
        print("Error loading config.json")
        return

    result = organize_files(args.fpath, extensions, args.dry_run)
    print(result)

# ==================================================
# ===================== GUI ========================
# ==================================================

def gui_mode():   # ADDED
    root = tk.Tk()
    root.title("Smart Folder Organizer")
    root.geometry("500x300")

    tk.Label(root, text="Smart Folder Organizer", font=("Arial", 14)).pack(pady=10)

    path_var = tk.StringVar()
    dry_var = tk.BooleanVar()

    def browse():
        path_var.set(filedialog.askdirectory())

    tk.Entry(root, textvariable=path_var, width=50).pack(pady=5)
    tk.Button(root, text="Browse Folder", command=browse).pack()

    tk.Checkbutton(root, text="Dry Run", variable=dry_var).pack(pady=5)

    status = tk.Label(root, text="")
    status.pack(pady=10)

    def run():
        extensions = load_config()
        if not extensions:
            messagebox.showerror("Error", "config.json not found or invalid")
            return

        result = organize_files(path_var.get(), extensions, dry_var.get())
        status.config(text=result)

    def undo():
        status.config(text=undo_changes())

    tk.Button(root, text="Organize", command=run).pack(pady=5)
    tk.Button(root, text="Undo Last Action", command=undo).pack(pady=5)

    root.mainloop()

# ==================================================
# ===================== MAIN =======================
# ==================================================

if __name__ == "__main__":   # MODIFIED
    import sys
    if "--gui" in sys.argv:
        gui_mode()
    else:
        cli_mode()
