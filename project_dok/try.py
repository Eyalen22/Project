import ctypes
import os

def get_drive_name(drive_letter):
    # מוודא שהנתיב בפורמט ש-Windows אוהב, למשל "F:\\"
    drive_path = f"{drive_letter.strip(':')}:\\"

    # יצירת Buffer לאחסון השם
    volumeNameBuffer = ctypes.create_unicode_buffer(1024)

    # קריאה ל-API של Windows
    ctypes.windll.kernel32.GetVolumeInformationW(
        ctypes.c_wchar_p(drive_path),
        volumeNameBuffer,
        ctypes.sizeof(volumeNameBuffer),
        None, None, None, None, 0
    )

    return volumeNameBuffer.value

def replace_drive_with_name(full_path, volume_name):
    # 1. מפרק את הנתיב לאות הכונן ולשאר הנתיב
    # למשל: "F:" ו- "\folder\file.txt"
    drive, rest_of_path = os.path.splitdrive(full_path)

    # 2. מוודא שהנתיב שקיבלנו אכן התחיל באות כונן
    if drive:
        # 3. מחבר את שם ה-USB החדש עם שאר הנתיב
        # אנחנו מוסיפים ":" אחרי השם כדי שזה ייראה כמו כונן
        new_path = f"{volume_name}:{rest_of_path}"
        return new_path

    return full_path  # אם לא היה כונן, מחזיר את המקור


# דוגמה לשימוש:
print(replace_drive_with_name("E:\Project\project_dok\server\\noam\E\Project", get_drive_name("E")))