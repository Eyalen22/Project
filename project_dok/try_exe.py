import hashlib
import os
import sys
import shutil
import PyInstaller.__main__


def run_full_process(dok_path):
    username = input("Enter username -> ").strip()
    password = input("Enter password -> ").strip()

    base_folder = r"E:\Project\project_dok\client"
    main_script = os.path.join(base_folder, "design", "app.py")
    vault_full_path = os.path.join(base_folder, ".auth_vault")
    exe_name = "OPEN_DOK"
    usb_drive = dok_path

    print(f"--- Starting Build Process ---")

    u_hash = hashlib.sha256(username.encode()).hexdigest()
    p_hash = hashlib.sha256(password.encode()).hexdigest()
    with open(vault_full_path, "w") as f:
        f.write(f"{u_hash}\n{p_hash}")

    # 3. הרצת PyInstaller (בנייה)
    print(f"Packaging {exe_name}.exe... This might take a minute.")
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
            print(f"SUCCESS! File is now on drive {usb_drive}")
        else:
            print(f"Warning: Drive {usb_drive} not found. File is in local 'dist' folder.")

    except Exception as e:
        print(f"Error during build: {e}")

    # --- 5. מנגנון ניקוי יסודי (מחיקת קבצים כבדים) ---
    print("\nCleaning up heavy build files...")

    folders_to_delete = ['build', 'dist']
    files_to_delete = [f"{exe_name}.spec", vault_full_path]
    for folder in folders_to_delete:
        if os.path.exists(folder):
            try:
                shutil.rmtree(folder)
                print(f"Removed folder: {folder}")
            except Exception as e:
                print(f"Could not remove folder {folder}: {e}")
    for file in files_to_delete:
        if os.path.exists(file):
            try:
                os.remove(file)
                print(f"Removed file: {file}")
            except Exception as e:
                print(f"Could not remove file {file}: {e}")

    print("\nAll clean! Your computer is light again.")
    return username, password


if __name__ == "__main__":
    run_full_process("E:\\")