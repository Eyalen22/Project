import client_com
from actions import client_protocol
from actions import monitor
import queue
from actions.monitor import FileOpenerMonitor


class clientLogic:

    def __init__(self):
        self.restoreQ = queue.Queue()
        self.client_comm = client_com.ClientCommunication('127.0.0.1', 2222, self.restoreQ)
        self.back_up_list = []


    def handle_msg(self):
        pass


    def send_back_up(self, directory):
        pass

    def monitor_file(self, file_path):
        monitor = FileOpenerMonitor(file_path, self.restoreQ)


    def save_files_to_send(self, file_name, file_path):
        pass
