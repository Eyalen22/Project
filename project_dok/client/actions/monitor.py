import os
import queue
import subprocess
import threading
import time
import logging
import wx

class FileOpenerMonitor:
    def __init__(self, file_path, changeQ):
        self.file_path = os.path.abspath(file_path)
        self.changeQ = changeQ
        self.file_name = os.path.basename(file_path)
        self.initial_mtime = os.path.getmtime(self.file_path)
        self.logger = logging.getLogger("logs.log")
        threading.Thread(target=self.open_and_monitor, daemon=True).start()
    def kill_process_if_running(self, process_name):
        """close the process"""
        try:
            subprocess.run(['taskkill', '/F', '/IM', process_name],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(0.3)
        except:
            pass
    def open_and_monitor(self):
        logger = logging.getLogger("logs.log")
        logger.debug("start monitor")
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

    def check_if_changed(self):
        flag = True
        time.sleep(0.5)
        self.logger.debug("file got closed")
        current_mtime = os.path.getmtime(self.file_path)
        if current_mtime > self.initial_mtime:
            self.initial_mtime = current_mtime
        else:
            flag = False
        self.logger.debug(f"status of changing is - {flag}")
        self.changeQ.put((self.file_path, flag))


if __name__ == "__main__":
    myQ = queue.Queue()
    if os.path.exists(r"F:\יכולות מערכת רשי פרקים.pdf"):
        monitor = FileOpenerMonitor(r"F:\יכולות מערכת רשי פרקים.pdf", myQ)
        while True:
            if not myQ.empty():
                print(myQ.get())