import os
import queue
import subprocess
import threading
import time
import logging

class FileOpenerMonitor:
    """Monitors local file access by opening files in appropriate viewers and detecting modifications upon closure"""

    def __init__(self, file_path, changeQ):
        """Initializes the monitor for a specific file and starts the tracking thread"""
        self.file_path = os.path.abspath(file_path)
        self.changeQ = changeQ
        self.file_name = os.path.basename(file_path)
        self.initial_mtime = os.path.getmtime(self.file_path)
        self.logger = logging.getLogger("logs.log")
        threading.Thread(target=self.open_and_monitor, daemon=True).start()

    def kill_process_if_running(self, process_name):
        """Forcefully terminates a process by name to ensure a clean file state before opening"""
        try:
            subprocess.run(['taskkill', '/F', '/IM', process_name],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(0.3)
        except Exception:
            pass

    def open_and_monitor(self):
        """Identifies file type and launches the associated Windows application to handle the file"""
        logger = logging.getLogger("logs.log")
        logger.debug("Monitoring started for: " + self.file_name)
        ext = self.file_name.lower()

        # Define file type associations
        image_exts = ('.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp')
        code_exts = ('.py', '.java', '.c', '.cpp', '.cs', '.js', '.html', '.css', '.txt', '.json')
        doc_exts = ('.docx', '.doc', '.pdf')

        if ext.endswith(image_exts):
            self.kill_process_if_running("mspaint.exe")
            subprocess.run(f'start /wait mspaint "{self.file_path}"', shell=True)
        elif ext.endswith(code_exts):
            subprocess.run(f'start /wait notepad "{self.file_path}"', shell=True)
        elif ext.endswith(doc_exts):
            self.kill_process_if_running("WINWORD.EXE")
            self.kill_process_if_running("msedge.exe")
            subprocess.run(f'start /wait "" "{self.file_path}"', shell=True)
        else:
            subprocess.run(f'start /wait "" "{self.file_path}"', shell=True)

        self.check_if_changed()

    def check_if_changed(self):
        """Compares the file's modification time after closure to determine if it needs to be synced/re-encrypted"""
        flag = True
        time.sleep(0.5)
        self.logger.debug("Process closed for: " + self.file_name)

        current_mtime = os.path.getmtime(self.file_path)
        if current_mtime > self.initial_mtime:
            self.initial_mtime = current_mtime
        else:
            flag = False

        self.logger.debug(f"File change status: {flag}")
        self.changeQ.put((self.file_path, flag))

if __name__ == "__main__":
    # Test block for standalone monitoring
    myQ = queue.Queue()
    test_path = r"F:\document.pdf"
    if os.path.exists(test_path):
        monitor = FileOpenerMonitor(test_path, myQ)
        while True:
            if not myQ.empty():
                print("Queue received update:", myQ.get())