import logging
import threading
import json
import enum
import time

from http_ws_api import WebSocketApi
from cpu_monitor import cpu_load
from memory_monitor import memory_info
from datatype import DataType
from storage_monitor import storage_info


class ThreadStatus(enum.Enum):
    THREAD_ON = 'THREAD ON'
    THREAD_OFF = 'THREAD OFF'


class DataThreadWS(WebSocketApi):

    def __init__(self, data_type: DataType, username: str, password: str,
                 interval: int, cpu: bool = None, mem: bool = None, storage: bool = None):
        super().__init__(host='localhost', port=5000, path="/echo")
        self.thread_status = ThreadStatus.THREAD_OFF
        self.data_type = data_type
        self.username = username
        self.password = password
        self.interval = interval
        self.cpu = cpu
        self.mem = mem
        self.storage = storage
        self.data_container = {}
        self.registration()
        self.client_id = self.client_id_parce()

    def _data_thread(self):
        while self.thread_status == ThreadStatus.THREAD_ON:
            if self.cpu is True:
                self.data_container['cpu_load'] = cpu_load(0)
            if self.mem is True:
                self.data_container['mem'] = memory_info(self.data_type)['used']
            if self.storage is True:
                self.data_container['storage'] = storage_info(self.data_type)['used']
            elif len(self.data_container) == 0:
                self.thread_status = ThreadStatus.THREAD_OFF
            self.ws.send(json.dumps({"type": "CLIENT_DATA",
                                     "data": self.data_container,
                                     "interval": self.interval,
                                     "client_id": self.client_id
                                     }, indent=4))
            time.sleep(self.interval)
            logging.info(self.ws.recv())

    def close_thread(self):
        self.thread_status = ThreadStatus.THREAD_OFF

    def thread_start(self):
        self.thread_status = ThreadStatus.THREAD_ON
        cpu_thread = threading.Thread(target=self._data_thread)
        cpu_thread.start()

    def client_id_parce(self) -> str:
        recv = json.loads(self.ws.recv())
        recv = recv.get('payload').get('client_id')
        self.thread_status = ThreadStatus.THREAD_ON
        return recv

    def error(self, recv):
        recv = json.loads(recv)
        if recv.get('Error'):
            self.thread_status = ThreadStatus.THREAD_OFF
            return logging.warning(recv.get('reason'))

    def registration(self):
        self.ws.send(json.dumps({"type": "HELLO"}))
        self.ws.recv()
        self.ws.send(
            json.dumps({"type": "REGISTRATION_CLIENT", "username": self.username, "password": self.password}))

