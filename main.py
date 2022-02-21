import threading
import enum
import base64
import logging
import log_config
from data_thread_in_websocket import DataThreadWS

from http_ws_api import BaseHttpApi
from cpu_monitor import cpu_load
from datatype import DataType


class ThreadStatus(enum.Enum):
    THREAD_ON = 'THREAD ON'
    THREAD_OFF = 'THREAD OFF'


class DataThread(BaseHttpApi):

    def __init__(self, data_type: DataType, interval: int, cpu: bool, username: str, password: str):
        super().__init__(host='localhost', port=5000)
        self.thread_status = ThreadStatus.THREAD_ON
        self.data_type = data_type
        self.interval = interval
        self.cpu = cpu
        self.username = username
        self.password = password
        self.registration = self.post('/client', json={'username': username, 'pass': password})
        logging.info(f'{self.username} registration')
        if self.registration.json().get('Error'):
            self.thread_status = ThreadStatus.THREAD_OFF
            logging.warning(f'{username} incorrect username or pass')

    def _data_thread(self):
        while self.thread_status == ThreadStatus.THREAD_ON:
            response = self.post(f'/client/{self.client_id()}', data={'cpu_load': cpu_load(self.interval)},
                                 headers=self.header())
            logging.info(response.text)
            if response.status_code != 202:
                self.thread_status = ThreadStatus.THREAD_OFF
                logging.warning(f'{response.status_code}')

    def cancel_thread(self):
        self.thread_status = ThreadStatus.THREAD_OFF
        logging.info('Thread off')

    def thread_start(self):
        cpu_thread = threading.Thread(target=self._data_thread)
        cpu_thread.start()

    def client_id(self):
        return self.registration.json().get('client_id')

    def header(self):
        coding_username_pass = base64.b64encode(f'{self.username}:{self.password}'.encode())
        return {
            'Authorization': f'Basic {coding_username_pass.decode()}'
        }


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-ht', '--http', help='thread for http requests', action='store_true')
    parser.add_argument('-w', '--websocket', help='thread for http requests', action='store_true')
    parser.add_argument('-u', '--user', type=str, help='username')
    parser.add_argument('-p', '--password', type=str, help='password')
    parser.add_argument('-i', '--interval', type=int, help='reception data interval', default=1)
    args = parser.parse_args()
    if args.http:
        cpu = DataThread(data_type=DataType.Megabyte, interval=args.interval, cpu=True, username=args.user, password=args.password)
        cpu.thread_start()
    if args.websocket:
        web = DataThreadWS(data_type=DataType.Megabyte, interval=args.interval, cpu=True, username=args.user, password=args.password)
        web.thread_start()
