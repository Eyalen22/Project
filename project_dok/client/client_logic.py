import time

import actions.cypher_files
import client_com
from actions.cypher_files import decrypt_file, encrypt_file
from design import app
from actions import client_protocol
import queue
import threading
from actions.monitor import FileOpenerMonitor
from pubsub import pub
import os
import sys
import ctypes
import logging



class clientLogic:

    def __init__(self):
        self.restoreQ = queue.Queue()
        self.back_up_list = []
        self.key = None
        self.user_name = ""
        self.client_comm = client_com.ClientCommunication('127.0.0.1', 2222)
        pub.subscribe(self.get_key, "get_key")
        pub.subscribe(self.monitor_file, "new_filename")
        pub.subscribe(self.save_files_to_send, "save")
        # Configure basic logging to a file
        logging.basicConfig(
            filename='logs.log',
            level=logging.DEBUG,  # Log messages of DEBUG level and higher
            format='%(asctime)s - %(levelname)s - %(message)s',
            filemode='a'  # Append to the file
        )
        self.logging = logging.getLogger("logs.log")
        threading.Thread(target=self.handle_send_files, args=(self.restoreQ,), daemon=False).start()


    def handle_send_files(self, msgQ):
        log = logging.getLogger("logs.log")
        log.debug("Thread is now running! - Debug")
        while True:
            sends_files = []
            while not msgQ.empty():
                log.debug(f"{msgQ.qsize()} - queue size1")# - problem
                file_path, status = msgQ.get()
                log.debug(f"got file {file_path} - in -----------------------------------")
                encrypt_file(file_path, self.key)
                if status:
                    connection = self.send_back_up(file_path=file_path)
                    log.debug(f"connection is - {connection}")
                    if connection:
                        sends_files.append(file_path)
                    else:
                        self.save_files_to_send(file_path=file_path)
            while True:
                files = self._get_files()
                for file in files:
                    if not msgQ.empty():
                        break
                    if not file in sends_files:
                        connection = self.send_back_up(file)
                        if not connection:
                            break
                        self.dell_back_up_list(file)
                if self.back_up_empty() or not msgQ.empty():
                    break
            time.sleep(0.5)

    ## לערוך
    def _get_files(self):
        if getattr(sys, 'frozen', False):
            base_path = os.path.dirname(sys.executable)
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))
        back_up_files = os.path.join(base_path, ".send_back_up")
        if not os.path.exists(back_up_files):
            return []
        try:
            with open(back_up_files, "r", encoding="utf-8") as f:
                content = [line.strip() for line in f.readlines() if line.strip()]
            return content
        except Exception as e:
            return []

    def get_key(self, user_name, password):
        self.key = actions.cypher_files.create_key(user_name= user_name, password= password)
        self.user_name = user_name

    def send_back_up(self, file_path):

        path = os.path.dirname(file_path)
        file_name = os.path.basename(file_path)
        return self.client_comm.send_file(file_name=file_name, path=path, user_name=self.user_name)

    def monitor_file(self, file_path):
        self.logging.debug(f"got into the monitor file :)")
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
            pass

    def dell_back_up_list(self, file_path):
        is_frozen = getattr(sys, 'frozen', False)
        base_path = os.path.dirname(sys.executable if is_frozen else os.path.abspath(__file__))
        backup_path = os.path.join(base_path, ".send_back_up")
        if os.path.exists(backup_path):
            if os.name == 'nt':
                ctypes.windll.kernel32.SetFileAttributesW(backup_path, 0x80)  # Normal
            with open(backup_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            with open(backup_path, 'w', encoding='utf-8') as f:
                for line in lines:
                    if line.strip() != file_path.strip():
                        f.write(line)
            if os.name == 'nt':
                ctypes.windll.kernel32.SetFileAttributesW(backup_path, 0x06)

    def back_up_empty(self):
        is_frozen = getattr(sys, 'frozen', False)
        base_path = os.path.dirname(sys.executable if is_frozen else os.path.abspath(__file__))
        backup_path = os.path.join(base_path, ".send_back_up")

        return os.path.getsize(backup_path) == 0




if __name__ == '__main__':
    client_log = clientLogic()
    app = app.App()
    app.start_app()