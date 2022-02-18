import threading
import json
import enum
import time

from http_ws_api import WebSocketApi, BaseHttpApi
from cpu_monitor import cpu_load
from memory_monitor import memory_info
from datatype import DataType
from storage_monitor import storage_info

request_id = 0


class ThreadStatus(enum.Enum):
    THREAD_ON = 'THREAD ON'
    THREAD_OFF = 'THREAD OFF'


class DataThread(WebSocketApi):

    def __init__(self, *, host: str, port: int, path: str,
                 data_type: DataType,
                 interval: int, cpu: bool = None, mem: bool = None, storage: bool = None):
        super().__init__(host=host, port=port, path=path)
        self.thread_status = ThreadStatus.THREAD_ON
        self.data_type = data_type
        self.ws.send(json.dumps({"type": "HELLO"}))
        self.interval = interval
        global request_id
        self.request_id = request_id
        request_id += 1
        self.cpu = cpu
        self.mem = mem
        self.storage = storage
        self.data_container = {}

    def _data_thread(self):
        while self.thread_status == ThreadStatus.THREAD_ON:
            if self.cpu is True:
                self.data_container['cpu'] = cpu_load(self.interval)
            if self.mem is True:
                self.data_container['mem'] = memory_info(self.data_type)['used']
            if self.storage is True:
                self.data_container['storage'] = storage_info(self.data_type)['used']
            elif len(self.data_container) == 0:
                self.thread_status = ThreadStatus.THREAD_OFF
            self.ws.send(json.dumps({"type": "CLIENT_DATA",
                                     "data": self.data_container,
                                     "interval": self.interval
                                     }, indent=4))
            print(self.ws.recv())

    def close_thread(self):
        self.thread_status = ThreadStatus.THREAD_OFF

    def thread_start(self):
        cpu_thread = threading.Thread(target=self._data_thread)
        cpu_thread.start()
