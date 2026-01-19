from logging import root
import os
import shutil
import time
import json
import argparse
import sys
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk

#============= GLASS THEME ===============

# ================= DEFAULT CONFIG =================

def ensure_config():
    default_config = {
        "categories": {
            "Images": [".jpg", ".jpeg", ".png", ".gif"],
            "Documents": [".pdf", ".docx", ".txt"],
            "Videos": [".mp4", ".mkv"],
            "Music": [".mp3", ".wav"],
            "Archives": [".zip", ".rar"]
        },
        "enable_unknown_folder": True,
        "unknown_folder_name": "Others"
    }

    if not os.path.exists("config.json"):
        with open("config.json", "w", encoding="utf-8") as f:
            json.dump(default_config, f, indent=4)

# ================= LOG FUNCTIONS ==================

def write_log(message):
    with open("log.txt", "a", encoding="utf-8") as log:
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        log.write(f"{timestamp} - {message}\n")


def write_undo(src, dst):
    with open("undo_log.txt", "a", encoding="utf-8") as ulog:
        ulog.write(f"{dst}|{src}\n")


# ================= UNDO FUNCTION ==================


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


# ================= LOAD CONFIG ====================


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


# ================= ORGANIZE LOGIC =================


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

        if not moved and enable_unknown:
            other_folder = os.path.join(fpath, unknown_name)
            destination = os.path.join(other_folder, file)

            if not dry_run:
                os.makedirs(other_folder, exist_ok=True)
                shutil.move(file_path, destination)
                write_log(f"{file} -> {unknown_name}")
                write_undo(file_path, destination)

    return "Dry run completed." if dry_run else "Folder organization complete."


# ====================== CLI =======================


def cli_mode():
    ensure_config()

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

# ==================== log data display ===================

def show_log_window(title, file_path):
    win = tk.Toplevel()
    win.title(title)
    win.geometry("600x400")

    text = tk.Text(win, wrap="word", bg="#1e1e1e", fg="white")
    text.pack(fill="both", expand=True)

    scrollbar = ttk.Scrollbar(text, command=text.yview)
    text.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")

    if not os.path.exists(file_path):
        text.insert("end", "No log found.")
        return
    with open(file_path, "r", encoding="utf-8") as f:
        text.insert("end", f.read())
    
    text.configure(state="disabled")

# ===================== THEME ======================


def apply_dark_theme(root):
    style = ttk.Style(root)
    style.theme_use("default")

    style.configure(".", background="#121212", foreground="white")
    style.configure("TFrame", background="#121212")
    style.configure("TLabel", background="#121212", foreground="white")
    style.configure("TButton", background="#1e88e5", foreground="white", padding=8)
    style.map("TButton", background=[("active", "#1565c0")])
    style.configure("TEntry", fieldbackground="#1e1e1e", foreground="white")
    style.configure("TCheckbutton", background="#121212", foreground="white")

#===================== clear fun in gui ======================

def clear_log_file(file_path, label):
    if os.path.exists(file_path):
        messagebox.showinfo("Info", f"No {label} to clear.")
        return
    
    confirm = messagebox.askyesno("Confirm", f"Are you sure you want to clear the {label}?")

    if confirm:
        open(file_path, "w").close()
        messagebox.showinfo("Info", f"{label} cleared.")

# ====================== GUI =======================


def gui_mode():
    ensure_config()

    root = tk.Tk()
    root.title("Smart Folder Organizer")

    root.geometry("900x400")
    root.configure(bg="#1e1e1e")

    root.resizable(True, True)
    root.state("zoomed")

    root.attributes("-alpha", 0.9)
    
    def update_log_buttons(*args):
        state = "normal" if dry_var.get() else "disabled"
        view_log_btn.config(state=state)
        view_undo_btn.config(state=state)
        clear_log_btn.config(state=state)
        clear_undo_btn.config(state=state)

    dry_var.trace_add("write", update_log_buttons)


    is_fullscreen = False

    def toggle_fullscreen(event=None):
        nonlocal is_fullscreen
        is_fullscreen = not is_fullscreen
        root.attributes("-fullscreen", is_fullscreen)

    def exit_fullscreen(event=None):
        nonlocal is_fullscreen
        is_fullscreen = False
        root.attributes("-fullscreen", False)
        is_fullscreen = False
        root.attributes("-fullscreen", False)

    root.bind("<F11>", toggle_fullscreen)
    root.bind("<Escape>", exit_fullscreen)

#====dark theme ====

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

    ttk.Entry(main, textvariable=path_var).pack(fill="x", pady=5)

    def browse():
        path_var.set(filedialog.askdirectory())

    ttk.Button(main, text="Browse Folder", command=browse).pack(pady=5)

    ttk.Checkbutton(
        main,
        text="Dry Run (Preview Only)",
        variable=dry_var
    ).pack(pady=(5, 2))

    status = ttk.Label(main, text="", wraplength=460)
    status.pack(pady=15)
    
    log_btn_frame = ttk.Frame(main)
    log_btn_frame.pack(fill="x", pady=(0,10))

    for i in range(4):
        log_btn_frame.columnconfigure(i, weight=1)

    view_log_btn = ttk.Button(
        log_btn_frame,
        text="View Log",
        command=lambda: show_log_window("Log data", "log.txt"),
        state="disabled"
    )
    
    view_undo_btn = ttk.Button(
        log_btn_frame,
        text="View Undo Log",
        command=lambda: show_log_window("Undo Log", "undo_log.txt"),
        state="disabled"
    )

    clear_log_btn = ttk.Button(
        log_btn_frame,
        text="Clear Log",
        command=lambda: clear_log_file("log.txt", "log")
        state="disabled"
    )

    clear_undo_btn = ttk.Button(
        log_btn_frame,
        text="Clear Undo Log",
        command=lambda: clear_log_file("undo_log.txt", "undo log")
        state="disabled"
    )

    log_btn_frame.columnconfigure(0, weight=1)
    log_btn_frame.columnconfigure(1, weight=1)

    view_log_btn.grid(row=0, column=0, sticky="ew", padx=10)
    view_undo_btn.grid(row=0, column=1, sticky="ew", padx=10)
    clear_log_btn.grid(row=0, column=2, sticky="ew", padx=10)
    clear_undo_btn.grid(row=0, column=3, sticky="ew", padx=10)

    def run():
        if not path_var.get():
            messagebox.showerror("Error", "Please select a folder")
            return

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
    btn_frame.pack(fill = "x", pady=10)

    btn_frame.columnconfigure(0, weight=1)
    btn_frame.columnconfigure(1, weight=1)

    organize_btn = ttk.Button(btn_frame, text="Organize", command=run)
    undo_btn = ttk.Button(btn_frame, text="Undo", command=undo)

    organize_btn.grid(row=0, column=0, sticky="ew", padx=10)
    undo_btn.grid(row=0, column=1, sticky="ew", padx=10)

    root.mainloop()

# ====================== MAIN ======================

if __name__ == "__main__":
    # GUI by default (double-click friendly)
    if "--cli" in sys.argv:
        sys.argv.remove("--cli")
        cli_mode()
    else:
        gui_mode()
