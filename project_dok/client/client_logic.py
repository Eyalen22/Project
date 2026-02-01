import client_com
import client_protocol
import queue
import threading



class clientLogic:

    def __init__(self):
        self.msgQ = queue.Queue()
        self.client_comm = client_com.ClientCommunication('127.0.0.1', 2222, self.msgQ)
        self.back_up_list = []
        threading.Thread(target=self.handle_msg, args=(self.msgQ,)).start()

    def handle_msg(self, recvQ):
        """

        :param comm:
        :param recvQ:
        :return:
        """
        while True:
            msg = recvQ.get()


    def send_back_up(self, directory):
        pass

    def monitor_directory(self, directory):
        pass

    def save_files_to_send(self, file_name, file_path):
        pass
