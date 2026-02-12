import hashlib
import os


def setup_dok():
    username = "noam"
    password = "eyal_en22"

    # 2. יצירת ה-Hash
    u_hash = hashlib.sha256(username.encode()).hexdigest()
    p_hash = hashlib.sha256(password.encode()).hexdigest()

    # 3. מציאת ה-DOK באופן אוטומטי (או שתכתוב ידנית את האות שלו)
    drive_letter = input("Enter your USB drive letter (e.g. E): ").strip()
    file_path = f"{drive_letter}:\\.auth_vault"

    try:
        with open(file_path, "w") as f:
            f.write(f"{u_hash}\n{p_hash}")
        if os.name == 'nt':
            os.system(f'attrib +h {file_path}')

        print(f"Success! Created secret file on {drive_letter}:")
        print(f"Path: {file_path}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    setup_dok()