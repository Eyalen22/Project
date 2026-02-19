import threading
from Lib.queue import Queue
import client_com
from design import app
from actions import client_protocol
from actions import monitor
import queue
import threading
from actions.monitor import FileOpenerMonitor
from pubsub import pub
class clientLogic:

    def __init__(self):
        self.restoreQ = queue.Queue()
        self.client_comm = client_com.ClientCommunication('127.0.0.1', 2222, self.restoreQ)
        self.back_up_list = []

        pub.subscribe(self.monitor_file, "new_filename")
        threading.Thread(target=self.handle_send_files).start()


    def handle_send_files(self):
        while True:
            file_name = self.restoreQ.get()
            print(file_name)


    def send_back_up(self, directory):
        pass

    def monitor_file(self, file_path):
        print("got file_path:", file_path)
        monitor = FileOpenerMonitor(file_path, self.restoreQ)


    def save_files_to_send(self, file_name, file_path):
        pass

if __name__ == '__main__':
    client_log = clientLogic()
    app = app.App()
    app.start_app()