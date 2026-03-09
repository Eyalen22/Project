import hashlib
import os
import sys
import shutil
import PyInstaller.__main__
import ctypes
from pathlib import Path


def run_full_process(drive_letter):
    # קבלת פרטים מהמשתמש
    username = input("Enter username -> ").strip()
    password = input("Enter password -> ").strip()
    base_folder = Path(r"E:/Project/project_dok/client")
    main_script = base_folder / "client_logic.py"
    vault_path = base_folder / ".auth_vault"
    exe_name = "OPEN_DOK"
    usb_drive_str = f"{drive_letter.upper()}"
    print(f"\n--- Starting Build Process (Hybrid OS/Pathlib) ---")
    if not os.path.exists(usb_drive_str):
        print(f"CRITICAL ERROR: Drive {usb_drive_str} not found!")
        return username, password
    usb_path = Path(usb_drive_str)
    final_exe_path = usb_path / f"{exe_name}.exe"
    final_secret_path = usb_path / ".send_back_up"

    try:
        u_hash = hashlib.sha256(username.encode()).hexdigest()
        p_hash = hashlib.sha256(password.encode()).hexdigest()
        vault_path.write_text(f"{u_hash}\n{p_hash}", encoding="utf-8")

        print(f"Packaging {exe_name}.exe... Please wait.")

        # 2. הרצת PyInstaller (חייב strings)
        PyInstaller.__main__.run([
            str(main_script),
            '--onefile',
            '--noconsole',
            f'--name={exe_name}',
            f'--add-data={str(vault_path)}{os.pathsep}.',
            f'--paths={str(base_folder)}',
            '--clean',
            '--log-level=WARN'
        ])

        # 3. העברה ל-DOK וניהול הגיבוי
        source_exe = Path("dist") / f"{exe_name}.exe"

        if source_exe.exists():
            print(f"Copying EXE to {usb_drive_str}...")
            # שימוש ב-shutil להעתקה
            shutil.copy2(source_exe, final_exe_path)
        else:
            print("Error: EXE was not created.")
            return username, password

        # טיפול ב-Attribute של הקובץ (שימוש ב-os/ctypes כי זה Tricky)
        if final_secret_path.exists():
            if os.name == 'nt':
                ctypes.windll.kernel32.SetFileAttributesW(str(final_secret_path), 0x80)

        # כתיבת קובץ הגיבוי
        final_secret_path.write_text("", encoding="utf-8")

        # הגדרת נסתר + מערכת
        if os.name == 'nt':
            ctypes.windll.kernel32.SetFileAttributesW(str(final_secret_path), 0x06)

        print(f"SUCCESS! Ready on {usb_drive_str}")

    except Exception as e:
        print(f"Error during process: {e}")

    finally:
        # 4. ניקוי (Pathlib עושה את זה אלגנטי)
        print("Cleaning up...")
        for folder_name in ['build', 'dist']:
            folder = Path(folder_name)
            if folder.exists():
                shutil.rmtree(folder, ignore_errors=True)

        for f in [Path(f"{exe_name}.spec"), vault_path]:
            if f.exists():
                try:
                    f.unlink()
                except:
                    pass

    return username, password


if __name__ == "__main__":
    u, p = run_full_process("F")
    print(f"\nFinal Status: Build complete for user '{u}'.")