print("Smart Folder Organizer")

import os
import shutil
import time
import json
import argparse
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk

# ==================================================
# ================= LOG FUNCTIONS ==================
# ==================================================

def write_log(message):
    with open("log.txt", "a", encoding="utf-8") as log:
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        log.write(f"{timestamp} - {message}\n")


def write_undo(src, dst):
    with open("undo_log.txt", "a", encoding="utf-8") as ulog:
        ulog.write(f"{dst}|{src}\n")


# ==================================================
# ================= UNDO FUNCTION ==================
# ==================================================

def undo_changes():
    if not os.path.exists("undo_log.txt"):
        return "No undo log found."

    with open("undo_log.txt", "r", encoding="utf-8") as file:
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


# ==================================================
# ================= LOAD CONFIG ====================
# ==================================================

def load_config():
    try:
        with open("config.json", "r", encoding="utf-8") as cfg:
            data = json.load(cfg)

        categories = data.get("categories", {})
        enable_unknown = data.get("enable_unknown_folder", True)
        unknown_name = data.get("unknown_folder_name", "Others")

        if not isinstance(categories, dict):
            return None

        return categories, enable_unknown, unknown_name

    except Exception:
        return None


# ==================================================
# ================= ORGANIZE LOGIC =================
# ==================================================

def organize_files(fpath, categories, enable_unknown, unknown_name, dry_run=False):
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

        # Match categories
        for folder, exts in categories.items():
            if not isinstance(exts, list):
                continue

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

        # Unknown files
        if not moved and enable_unknown:
            other_folder = os.path.join(fpath, unknown_name)
            destination = os.path.join(other_folder, file)

            if not dry_run:
                os.makedirs(other_folder, exist_ok=True)
                shutil.move(file_path, destination)
                write_log(f"{file} -> {unknown_name}")
                write_undo(file_path, destination)

    return "Dry run completed." if dry_run else "Folder organization complete."


# ==================================================
# ====================== CLI =======================
# ==================================================

def cli_mode():
    parser = argparse.ArgumentParser(description="Smart Folder Organizer")
    parser.add_argument("fpath", help="Folder path")
    parser.add_argument("--dry-run", action="store_true", help="Preview only")
    parser.add_argument("--undo", action="store_true", help="Undo last operation")
    args = parser.parse_args()

    if args.undo:
        print(undo_changes())
        return

    config_data = load_config()
    if not config_data:
        print("Invalid or missing config.json")
        return

    categories, enable_unknown, unknown_name = config_data

    result = organize_files(
        args.fpath,
        categories,
        enable_unknown,
        unknown_name,
        args.dry_run
    )

    print(result)


# ==================================================
# ===================== THEME ======================
# ==================================================

def apply_dark_theme(root):
    style = ttk.Style(root)
    style.theme_use("default")

    style.configure(".",
        background="#121212",
        foreground="white",
        font=("Segoe UI", 10)
    )

    style.configure("TFrame", background="#121212")
    style.configure("TLabel", background="#121212", foreground="white")

    style.configure(
        "TButton",
        background="#1e88e5",
        foreground="white",
        padding=8,
        borderwidth=0
    )

    style.map(
        "TButton",
        background=[("active", "#1565c0")]
    )

    style.configure(
        "TEntry",
        fieldbackground="#1e1e1e",
        foreground="white",
        insertcolor="white"
    )

    style.configure(
        "TCheckbutton",
        background="#121212",
        foreground="white"
    )


# ==================================================
# ====================== GUI =======================
# ==================================================

def gui_mode():
    root = tk.Tk()
    root.title("Smart Folder Organizer")
    root.geometry("520x350")
    root.configure(bg="#121212")

    apply_dark_theme(root)

    main = ttk.Frame(root, padding=20)
    main.pack(fill="both", expand=True)

    ttk.Label(
        main,
        text="Smart Folder Organizer",
        font=("Segoe UI", 16, "bold"),
        foreground="#1e88e5"
    ).pack(pady=(0, 15))

    path_var = tk.StringVar()
    dry_var = tk.BooleanVar()

    ttk.Entry(main, textvariable=path_var, width=55).pack(pady=5)

    def browse():
        path_var.set(filedialog.askdirectory())

    ttk.Button(main, text="Browse Folder", command=browse).pack(pady=5)

    ttk.Checkbutton(
        main,
        text="Dry Run (Preview Only)",
        variable=dry_var
    ).pack(pady=5)

    status = ttk.Label(main, text="", wraplength=460)
    status.pack(pady=15)

    def run():
        config_data = load_config()
        if not config_data:
            messagebox.showerror("Error", "Invalid or missing config.json")
            return

        categories, enable_unknown, unknown_name = config_data

        result = organize_files(
            path_var.get(),
            categories,
            enable_unknown,
            unknown_name,
            dry_var.get()
        )

        status.config(text=result)

    def undo():
        status.config(text=undo_changes())

    btn_frame = ttk.Frame(main)
    btn_frame.pack(pady=10)

    ttk.Button(btn_frame, text="Organize", command=run).pack(side="left", padx=10)
    ttk.Button(btn_frame, text="Undo", command=undo).pack(side="left", padx=10)

    root.mainloop()


# ==================================================
# ====================== MAIN ======================
# ==================================================

if __name__ == "__main__":
    import sys
    if "--gui" in sys.argv:
        gui_mode()
    else:
        cli_mode()
