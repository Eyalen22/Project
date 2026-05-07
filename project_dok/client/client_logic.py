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
    """Orchestrates the client's internal operations, including file encryption/decryption, monitoring, and backup queue management"""

    def __init__(self):
        """Initializes queues, communication layers, event subscriptions, and logging for the client application"""
        self.restoreQ = queue.Queue()
        self.back_up_list = []
        self.key = None
        self.user_name = ""
        self.client_comm = client_com.ClientCommunication('192.168.4.91', 2222)
        pub.subscribe(self.get_key, "get_key")
        pub.subscribe(self.monitor_file, "new_filename")
        pub.subscribe(self.save_files_to_send, "save")
        pub.subscribe(self.back_up_all, "backup_all_requested")
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
        """Background thread that continuously processes the backup queue and ensures files are sent when connection is available"""
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

    def _get_files(self):
        """Reads the local hidden backup file to retrieve paths of files waiting for re-transmission"""
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
        """Generates a cryptographic key based on user credentials for local file protection"""
        self.key = actions.cypher_files.create_key(user_name= user_name, password= password)
        self.user_name = user_name

    def send_back_up(self, file_path):
        """Extracts directory and filename to initiate a backup transfer via the communication module"""
        path = os.path.dirname(file_path)
        file_name = os.path.basename(file_path)
        return self.client_comm.send_file(file_name=file_name, path=path, user_name=self.user_name)

    def monitor_file(self, file_path):
        """Decrypts the target file and launches a monitor thread to watch for its closure"""
        self.logging.debug(f"got into the monitor file :)")
        decrypt_file(file_path, key=self.key)
        FileOpenerMonitor(file_path, self.restoreQ)

    def save_files_to_send(self, file_path):
        """Appends a file path to the offline queue file, maintaining hidden and system file attributes on Windows"""
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
        """Removes a successfully sent file path from the offline backup list and restores file attributes"""
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
        """Checks the size of the backup queue file to determine if any tasks are pending"""
        is_frozen = getattr(sys, 'frozen', False)
        base_path = os.path.dirname(sys.executable if is_frozen else os.path.abspath(__file__))
        backup_path = os.path.join(base_path, ".send_back_up")

        return os.path.getsize(backup_path) == 0


    def get_all_dok_files(self):
        """
        Identifies the DOK drive and scans for all files EXCEPT:
        - The EXE itself
        - .send_back_up (the hidden queue file)
        - OPEN_DOK (the app name/folder)
        - log.logs
        - System Volume Information (and everything inside)
        """
        if getattr(sys, 'frozen', False):
            running_path = sys.executable
            exe_name = os.path.basename(running_path)  # Get the EXE filename
        else:
            running_path = os.path.abspath(__file__)
            exe_name = None
        drive_root = os.path.splitdrive(running_path)[0] + os.sep
        all_files = []
        excluded_names = {".send_back_up", "OPEN_DOK", "logs.log"}
        if exe_name:
            excluded_names.add(exe_name)
        for root, dirs, files in os.walk(drive_root):
            if "System Volume Information" in dirs:
                dirs.remove("System Volume Information")
            if "OPEN_DOK" in dirs:
                dirs.remove("OPEN_DOK")
            for file in files:
                if file in excluded_names:
                    continue
                if file.endswith(".send_back_up"):
                    continue
                full_path = os.path.join(root, file)
                all_files.append(full_path)
        return all_files

    def back_up_all(self):
        """saving every file to send back"""
        log = logging.getLogger("logs.log")
        files = self.get_all_dok_files()
        log.debug(f"files - {files}")
        for file in files:
            self.save_files_to_send(file)

if __name__ == '__main__':
    client_log = clientLogic()
    app = app.App()
    app.start_app()