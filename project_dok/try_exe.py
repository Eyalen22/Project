import hashlib
import os
import sys
import shutil
import PyInstaller.__main__
import ctypes  # נדרש להגדרת קובץ כנסתר בווינדוס
from pathlib import Path


def run_full_process(dok_path):
    username = input("Enter username -> ").strip()
    password = input("Enter password -> ").strip()
    base_folder = r"C:\Users\USER\Documents\Project\project_dok\client"
    main_script = os.path.join(base_folder, "client_logic.py")

    # קבצים זמניים לצורך הבנייה
    vault_full_path = os.path.join(base_folder, ".auth_vault")
    exe_name = "OPEN_DOK"
    usb_drive = dok_path

    print(f"--- Starting Build Process ---")

    # 1. יצירת קובץ ה-Vault (נשאר פנימי בתוך ה-EXE)
    u_hash = hashlib.sha256(username.encode()).hexdigest()
    p_hash = hashlib.sha256(password.encode()).hexdigest()
    with open(vault_full_path, "w") as f:
        f.write(f"{u_hash}\n{p_hash}")

    print(f"Packaging {exe_name}.exe... This might take a minute.")
    try:
        # 2. הרצת PyInstaller
        # שים לב: הורדתי את ה-secret_text_path מהאריזה כדי שיהיה דינמי בחוץ
        PyInstaller.__main__.run([
            main_script,
            '--onefile',
            '--noconsole',
            f'--name={exe_name}',
            f'--add-data={vault_full_path}{os.pathsep}.',
            f'--paths={base_folder}',
            '--clean',
            '--log-level=WARN'
        ])

        # 3. העברה ל-DOK ויצירת קובץ סודי חיצוני
        
        source_exe = os.path.join("dist", f"{exe_name}.exe")
        final_exe_path = os.path.join(usb_drive, f"{exe_name}.exe")
        final_secret_path = os.path.join(usb_drive, ".send_back_up")

        if os.path.exists(usb_drive):
            if os.path.exists(final_exe_path):
                os.remove(final_exe_path)
            shutil.copy2(source_exe, final_exe_path)

            # יצירת הקובץ הדינמי ישירות על ה-DOK
            with open(final_secret_path, "w", encoding="utf-8") as f:
                f.write("back up files:\n")

            # הפיכת הקובץ לנסתר + קובץ מערכת (0x06 = Hidden (2) + System (4))
            if os.name == 'nt':
                ctypes.windll.kernel32.SetFileAttributesW(final_secret_path, 0x06)

            print(f"SUCCESS! EXE and Hidden Secret file are now on {usb_drive}")
        else:
            print(f"Warning: Drive {usb_drive} not found.")

    except Exception as e:
        print(f"Error during build: {e}")

    # --- 4. מנגנון ניקוי ---
    print("\nCleaning up build files...")
    folders_to_delete = ['build', 'dist']
    # מוחקים רק את ה-vault הזמני, ה-secret כבר ב-DOK
    files_to_delete = [f"{exe_name}.spec", vault_full_path]

    for folder in folders_to_delete:
        if os.path.exists(folder):
            shutil.rmtree(folder, ignore_errors=True)
    for file in files_to_delete:
        if os.path.exists(file):
            os.remove(file)

    print("\nAll clean! Ready to go.")
    return username, password


if __name__ == "__main__":
    run_full_process("E:\\")