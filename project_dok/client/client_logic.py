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
                if connection:
                    files = self._get_files()
                    for file in files:
                        self.send_back_up(file)
                else:
                    self.save_files_to_send(file_path=file_path)
                    files = self._get_files()
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
            if len(content) > 1:
                files_list_text = "\n".join(content[1:])
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

    ## לערוך
    def save_files_to_send(self, file_path):
        if getattr(sys, 'frozen', False):
            base_path = os.path.dirname(sys.executable)
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))
        back_up_files = os.path.join(base_path, ".send_back_up")
        wx.MessageBox(f"Saving path: {file_path}", "Backup System")
        try:
            with open(back_up_files, "a", encoding="utf-8") as f:
                f.write(f"{file_path}\n")
            if os.name == 'nt':
                import ctypes
                ctypes.windll.kernel32.SetFileAttributesW(back_up_files, 0x06)
        except Exception as e:
            wx.MessageBox(f"Error saving to DOK: {str(e)}", "File Error")

if __name__ == '__main__':
    client_log = clientLogic()
    app = app.App()
    app.start_app()