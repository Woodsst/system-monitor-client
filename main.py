import threading
import enum

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
        self.registration = self.post('/client', data={'login': login, 'pass': password})
        if self.registration.json().get('Error'):
            self.thread_status = ThreadStatus.THREAD_OFF

    def _data_thread(self):
        while self.thread_status == ThreadStatus.THREAD_ON:
            self.post(f'/client/{self.client_id()}', data={'cpu_load': cpu_load(self.interval)})

    def close_thread(self):
        self.thread_status = ThreadStatus.THREAD_OFF

    def thread_start(self):
        cpu_thread = threading.Thread(target=self._data_thread)
        cpu_thread.start()

    def client_id(self):
        return self.registration.json().get('client_id')


if __name__ == '__main__':
    cpu = DataThread(data_type=DataType.Megabyte, interval=1, cpu=True, login='wood', password='121222')
    cpu.thread_start()
