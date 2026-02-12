import hashlib
import os
import sys
import shutil
import PyInstaller.__main__


def run_full_process():
    # 1. קלט מהמשתמש
    username = input("Enter username -> ").strip()
    password = input("Enter password -> ").strip()

    # --- הגדרת נתיבים ---
    base_folder = r"F:\Project\project_dok\client"
    main_script = os.path.join(base_folder, "design", "app.py")
    vault_full_path = os.path.join(base_folder, ".auth_vault")
    exe_name = "OPENDOK"
    usb_drive = r"E:"

    print(f"--- Starting Build Process ---")

    # 2. יצירת ה-Vault הזמני
    u_hash = hashlib.sha256(username.encode()).hexdigest()
    p_hash = hashlib.sha256(password.encode()).hexdigest()
    with open(vault_full_path, "w") as f:
        f.write(f"{u_hash}\n{p_hash}")

    # 3. הרצת PyInstaller (בנייה)
    print(f"🚀 Packaging {exe_name}.exe... This might take a minute.")
    try:
        PyInstaller.__main__.run([
            main_script,
            '--onefile',
            '--noconsole',
            f'--name={exe_name}',
            f'--add-data={vault_full_path};.',
            f'--paths={base_folder}',
            '--clean',
            '--log-level=WARN'
        ])

        # 4. העברה לכונן E
        source_exe = os.path.join("dist", f"{exe_name}.exe")
        final_destination = os.path.join(usb_drive, f"{exe_name}.exe")

        if os.path.exists(usb_drive):
            if os.path.exists(final_destination):
                os.remove(final_destination)
            shutil.copy2(source_exe, final_destination)
            print(f"✅ SUCCESS! File is now on drive {usb_drive}")
        else:
            print(f"⚠️ Warning: Drive {usb_drive} not found. File is in local 'dist' folder.")

    except Exception as e:
        print(f"❌ Error during build: {e}")

    # --- 5. מנגנון ניקוי יסודי (מחיקת קבצים כבדים) ---
    print("\n🧹 Cleaning up heavy build files...")

    # תיקיות ש-PyInstaller יוצר
    folders_to_delete = ['build', 'dist']
    # קבצי הגדרות ו-vault זמני
    files_to_delete = [f"{exe_name}.spec", vault_full_path]

    # מחיקת תיקיות
    for folder in folders_to_delete:
        if os.path.exists(folder):
            try:
                shutil.rmtree(folder)
                print(f"Removed folder: {folder}")
            except Exception as e:
                print(f"Could not remove folder {folder}: {e}")

    # מחיקת קבצים
    for file in files_to_delete:
        if os.path.exists(file):
            try:
                os.remove(file)
                print(f"Removed file: {file}")
            except Exception as e:
                print(f"Could not remove file {file}: {e}")

    print("\n✨ All clean! Your computer is light again.")


if __name__ == "__main__":
    run_full_process()