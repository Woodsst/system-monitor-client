import threading
import enum
import base64
import logging
import time

import log_config
from data_thread_in_websocket import DataThreadWS

from http_ws_api import BaseHttpApi
from cpu_monitor import cpu_load
from datatype import DataType
from memory_monitor import memory_info
from storage_monitor import storage_info

logger = logging.getLogger(__name__)


class ThreadStatus(enum.Enum):
    THREAD_ON = 'THREAD ON'
    THREAD_OFF = 'THREAD OFF'


class DataThread(BaseHttpApi):

    def __init__(self, data_type: DataType, interval: int, username: str, password: str, mem: bool = None, cpu: bool = None, storage: bool = None):
        super().__init__(host='localhost', port=5000)
        self.thread_status = ThreadStatus.THREAD_ON
        self.data_type = data_type
        self.interval = interval
        self.cpu = cpu
        self.mem = mem
        self.storage = storage
        self.username = username
        self.password = password
        self.registration = self.post('/client', json={'username': username, 'pass': password})
        logging.info(f'{self.username} registration')
        if self.registration.json().get('Error'):
            self.thread_status = ThreadStatus.THREAD_OFF
            logging.warning(f'{username} incorrect username or pass')

    def _data_thread(self):
        while self.thread_status == ThreadStatus.THREAD_ON:
            data = {}
            if self.cpu:
                data['cpu_load'] = cpu_load(0)
            if self.mem:
                data['mem'] = memory_info(self.data_type)['used']
            if self.storage:
                data['storage'] = storage_info(self.data_type)['used']
            response = self.post(f'/client/{self.client_id()}', data=data,
                                 headers=self.header())
            logging.info(response.text)
            time.sleep(self.interval)
            if response.status_code != 202:
                self.thread_status = ThreadStatus.THREAD_OFF
                logging.warning(f'{response.status_code}')

    def cancel_thread(self):
        self.thread_status = ThreadStatus.THREAD_OFF
        logging.info('Thread off')

    def thread_start(self):
        self.thread_status = ThreadStatus.THREAD_ON
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
    parser.add_argument('-c', '--cpu', help='thread for http requests cpu load', action='store_true')
    parser.add_argument('-m', '--memory', help='thread for http requests memory load', action='store_true')
    parser.add_argument('-s', '--storage', help='thread for http requests storage load', action='store_true')
    parser.add_argument('-u', '--user', type=str, help='username')
    parser.add_argument('-p', '--password', type=str, help='password')
    parser.add_argument('-i', '--interval', type=int, help='reception data interval', default=1)
    args = parser.parse_args()
    if args.http:
        thread = DataThread(data_type=DataType.Megabyte, interval=args.interval, cpu=args.cpu, mem=args.memory,
                            storage=args.storage, username=args.user, password=args.password)
        thread.thread_start()
    if args.websocket:
        websocket_thread = DataThreadWS(data_type=DataType.Megabyte, interval=args.interval, cpu=args.cpu, mem=args.memory,
                                        storage=args.storage, username=args.user, password=args.password)
        websocket_thread.thread_start()
