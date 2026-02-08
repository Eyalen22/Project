import os
import subprocess
import threading
import time


class FileOpenerMonitor:
    def __init__(self, file_path):
        self.file_path = os.path.abspath(file_path)
        self.file_name = os.path.basename(file_path)
        self.initial_mtime = os.path.getmtime(self.file_path)

    def kill_process_if_running(self, process_name):
        """סוגר תהליכים תקועים כדי להבטיח שהניטור יתחיל מחדש בצורה נקייה"""
        try:
            subprocess.run(['taskkill', '/F', '/IM', process_name],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(0.3)
        except:
            pass

    def open_and_monitor(self):
        try:
            ext = self.file_name.lower()
            # הגדרת קבוצות קבצים
            image_exts = ('.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp')
            code_exts = ('.py', '.java', '.c', '.cpp', '.cs', '.js', '.html', '.css', '.txt', '.json')
            doc_exts = ('.docx', '.doc', '.pdf')
            if ext.endswith(image_exts):
                print(f"[*] פותח תמונה ב-MSPaint...")
                self.kill_process_if_running("mspaint.exe")
                subprocess.run(f'start /wait mspaint "{self.file_path}"', shell=True)

            elif ext.endswith(code_exts):
                print(f"[*] פותח קוד/טקסט ב-Notepad...")
                subprocess.run(f'start /wait notepad "{self.file_path}"', shell=True)

            elif ext.endswith(doc_exts):
                print(f"[*] פותח מסמך ומנקה תהליכי רקע...")
                self.kill_process_if_running("WINWORD.EXE")
                self.kill_process_if_running("msedge.exe")
                subprocess.run(f'start /wait "" "{self.file_path}"', shell=True)

            else:
                subprocess.run(f'start /wait "" "{self.file_path}"', shell=True)

            self.check_if_changed()

        except Exception as e:
            print(f"שגיאה: {e}")

    def check_if_changed(self):
        time.sleep(0.5)
        current_mtime = os.path.getmtime(self.file_path)
        print(f"\n[!] הקובץ {self.file_name} נסגר.")

        if current_mtime > self.initial_mtime:
            print(f"[V] בוצע שינוי בקובץ!")
            self.initial_mtime = current_mtime
        else:
            print(f"[-] לא בוצע שינוי.")

    def start_thread(self):
        t = threading.Thread(target=self.open_and_monitor, daemon=True)
        t.start()


if __name__ == "__main__":
    # בדוק כאן: main.py, test.txt, image.png וכו'
    my_file = r"E:\Project\project_dok\Setting.py"
    if os.path.exists(my_file):
        monitor = FileOpenerMonitor(my_file)
        monitor.start_thread()
        monitor2 = FileOpenerMonitor(r"E:\Project\project_dok\server\noam\E\tevel.jpg")
        monitor2.start_thread()
        monitor3 = FileOpenerMonitor(r"E:\Project\project_dok\server\noam\E\tevel.jpg")
        monitor3.start_thread()
        while True:
            time.sleep(1)