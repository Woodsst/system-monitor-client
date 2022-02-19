import threading
import enum
import base64

from http_ws_api import BaseHttpApi
from cpu_monitor import cpu_load
from datatype import DataType


class ThreadStatus(enum.Enum):
    THREAD_ON = 'THREAD ON'
    THREAD_OFF = 'THREAD OFF'


class DataThread(BaseHttpApi):

    def __init__(self, *, data_type: DataType, interval: int, cpu: bool, login: str, password: str):
        super().__init__(host='localhost', port=5000)
        self.thread_status = ThreadStatus.THREAD_ON
        self.data_type = data_type
        self.interval = interval
        self.cpu = cpu
        self.login = login
        self.password = password
        self.registration = self.post('/client', json={'login': login, 'pass': password})
        if self.registration.json().get('Error'):
            self.thread_status = ThreadStatus.THREAD_OFF

    def _data_thread(self):
        while self.thread_status == ThreadStatus.THREAD_ON:
            response = self.post(f'/client/{self.client_id()}', data={'cpu_load': cpu_load(self.interval)},
                                 headers=self.header())
            if response.status_code != 202:
                self.thread_status = ThreadStatus.THREAD_OFF

    def close_thread(self):
        self.thread_status = ThreadStatus.THREAD_OFF

    def thread_start(self):
        cpu_thread = threading.Thread(target=self._data_thread)
        cpu_thread.start()

    def client_id(self):
        return self.registration.json().get('client_id')

    def header(self):
        coding_login_pass = base64.b64encode(f'{self.login}:{self.password}'.encode())
        return {
            'Authorization': f'Basic {coding_login_pass.decode()}'
        }


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--user', type=str, help='username')
    parser.add_argument('-p', '--password', type=str, help='username')
    parser.add_argument('-i', '--interval', type=int, help='reception data interval', default=1)
    args = parser.parse_args()
    cpu = DataThread(data_type=DataType.Megabyte, interval=args.interval, cpu=True, login=args.user, password=args.password)
    cpu.thread_start()
