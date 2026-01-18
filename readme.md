📁 Smart Folder Organizer (Python)

A simple yet powerful Python-based file organization tool that automatically sorts files in a folder into categorized subfolders based on file extensions.
Built step-by-step as a learning project and enhanced with dry run, logging, and undo tracking.

🚀 Features

📂 Automatically organizes files into folders like:

Images
Documents
Audio
Videos
Archives
Scripts
Programs
Others

🔍 Dry Run mode – preview changes without moving files
📝 Logging system (log.txt)
↩️ Undo tracking (undo_log.txt) – records original file locations
🛡️ Safe checks for invalid paths and permission errors

🛠️ Requirements
Python 3.x
Works on:
Windows
Linux
macOS
No external libraries required.

📂 Project Structure
SmartFolderOrganizer/
│
├── organizer.py
├── log.txt
├── undo_log.txt
└── README.md

▶️ How to Run
Open a terminal / command prompt
Navigate to the project folder
Run the script:
python organizer.py

🧪 Dry Run Mode (Recommended First)
When prompted:Do you want to do a dry run? (yes/no):
Type:yes
✔ Shows what would happen
❌ Does NOT move any files

Example output:
[DRY RUN] photo.jpg -> Images
[DRY RUN] report.pdf -> Documents
-> Actual Organization
When you are confident, choose:no
Files will be moved into categorized folders inside the selected directory.

📝 Logging
log.txt
Stores:File movements
Errors (if any)Timestamed actions
Example:2026-01-18 11:42:10 - report.pdf -> Documents
↩️ Undo Tracking
undo_log.txt
Stores mappings like:new_path|original_path
This enables future undo / restore functionality.

⚠️ Undo execution logic can be added in the next version.

🧠 Learning Outcomes
This project helps you learn:
File handling in Python
OS path management
Safe scripting practices
Logging & audit trails
Real-world utility design
Incremental project development

🔮 Future Improvements
Full Undo Mode
Configurable categories via config.json
Command-line arguments (CLI flags)
GUI version

Summary report after execution

👤 Author

Mohamed Shaheem kp
AI Engineering & Data Science Student
Beginner-friendly project built for learning and growth 🚀

📜 License
This project is open for learning and personal use.