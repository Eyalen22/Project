import threading
from Lib.queue import Queue
import actions.cypher_files
import client_com
from actions.cypher_files import decrypt_file, encrypt_file
from design import app
from actions import client_protocol
from actions import monitor
import queue
import threading
from actions.monitor import FileOpenerMonitor
from pubsub import pub
import os
import sys
import wx
import ctypes

class clientLogic:

    def __init__(self):
        self.restoreQ = queue.Queue()
        self.client_comm = client_com.ClientCommunication('127.0.0.1', 2222, self.restoreQ)
        self.back_up_list = []
        self.key = None
        self.user_name = ""
        pub.subscribe(self.get_key, "get_key")
        pub.subscribe(self.monitor_file, "new_filename")
        threading.Thread(target=self.handle_send_files).start()


    def handle_send_files(self):
        while True:
            file_path, status = self.restoreQ.get()
            encrypt_file(file_path, self.key)
            if status:
                connection = self.send_back_up(file_path=file_path)
                wx.MessageBox(f"{connection}", "connection")
                if connection:
                    files = self._get_files()
                    for file in files:
                        if not file == file_path:
                            self.send_back_up(file)
                    self.dell_back_up_list()
                else:
                    self.save_files_to_send(file_path=file_path)
    ## לערוך
    def _get_files(self):
        if getattr(sys, 'frozen', False):
            base_path = os.path.dirname(sys.executable)
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))
        back_up_files = os.path.join(base_path, ".send_back_up")
        if not os.path.exists(back_up_files):
            wx.MessageBox("Backup file not found on drive.", "Error")
            return []
        try:
            with open(back_up_files, "r", encoding="utf-8") as f:
                content = [line.strip() for line in f.readlines() if line.strip()]
            if len(content) > 0:
                files_list_text = "\n".join(content)
                wx.MessageBox(f"Files found in backup:\n\n{files_list_text}", "Backup List")
            else:
                wx.MessageBox("The backup list is empty.", "Information")
            return content
        except Exception as e:
            wx.MessageBox(f"Error reading backup file: {str(e)}", "Error")
            return []

    def get_key(self, user_name, password):
        self.key = actions.cypher_files.create_key(user_name= user_name, password= password)
        self.user_name = user_name

    def send_back_up(self, file_path):
        path = os.path.dirname(file_path)
        file_name = os.path.basename(file_path)
        connection = self.client_comm.send_file(file_name=file_name, path=path, user_name=self.user_name)

        return connection

    def monitor_file(self, file_path):
        decrypt_file(file_path, key=self.key)
        FileOpenerMonitor(file_path, self.restoreQ)

    def save_files_to_send(self, file_path):
        is_frozen = getattr(sys, 'frozen', False)
        base_path = os.path.dirname(sys.executable if is_frozen else os.path.abspath(__file__))
        backup_path = os.path.join(base_path, ".send_back_up")
        try:
            existing_paths = set()
            if os.path.exists(backup_path):
                if os.name == 'nt':
                    import ctypes
                    ctypes.windll.kernel32.SetFileAttributesW(backup_path, 0x80)
                with open(backup_path, "r", encoding="utf-8") as f:
                    existing_paths = {line.strip() for line in f if line.strip()}
            existing_paths.add(file_path.strip())
            with open(backup_path, "w", encoding="utf-8") as f:
                f.write("\n".join(existing_paths) + "\n")
            if os.name == 'nt':
                import ctypes
                ctypes.windll.kernel32.SetFileAttributesW(backup_path, 0x06)
        except Exception as e:
            wx.MessageBox(f"Error: {e}", "File Error")

    def dell_back_up_list(self):
        is_frozen = getattr(sys, 'frozen', False)
        base_path = os.path.dirname(sys.executable if is_frozen else os.path.abspath(__file__))
        backup_path = os.path.join(base_path, ".send_back_up")
        if os.path.exists(backup_path):
            if os.name == 'nt':
                ctypes.windll.kernel32.SetFileAttributesW(backup_path, 0x80)
            open(backup_path, 'w').close()
            if os.name == 'nt':
                ctypes.windll.kernel32.SetFileAttributesW(backup_path, 0x06)

if __name__ == '__main__':
    client_log = clientLogic()
    app = app.App()
    app.start_app()