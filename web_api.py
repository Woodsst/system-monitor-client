import enum
import json
import logging
import threading
import time

import requests
import websocket
from requests import Response

from cpu_monitor import cpu_load
from datatype import DataType
from memory_monitor import memory_info
from storage_monitor import storage_info
from abc import ABC, abstractmethod


class DataCollector(ABC):
    @abstractmethod
    def start(self):
        raise NotImplementedError()

    @abstractmethod
    def stop(self):
        raise NotImplementedError()

    @abstractmethod
    def time_work_write_log(self):
        raise NotImplementedError()

    @abstractmethod
    def log_slice(self, start, end):
        raise NotImplementedError()


class ThreadStatus(enum.Enum):
    THREAD_ON = 'THREAD ON'
    THREAD_OFF = 'THREAD OFF'


class BaseHttpApi:
    def __init__(self, host: str, port: int) -> object:
        self.host = host
        self.port = port
        self.base_url = f"http://{self.host}:{self.port}"

    def get(self, path, params=None) -> Response:
        url = self.base_url + path
        return requests.get(url, params=params)

    def post(self, path, data=None, json=None, **kwargs) -> Response:
        url = self.base_url + path
        return requests.post(url, data=data, json=json, **kwargs)

    def patch(self, path, data=None) -> Response:
        url = self.base_url + path
        return requests.patch(url, data=data)

    def delete(self, path) -> Response:
        url = self.base_url + path
        return requests.delete(url)

    def put(self, path, data=None, json=None) -> Response:
        url = self.base_url + path
        return requests.put(url, data=data, json=json)


class WebSocketApi:
    def __init__(self, host: str, port: int, path: str):
        self.host = host
        self.port = port
        self.path = path
        self.url = f'ws://{self.host}:{self.port}{self.path}'
        self.ws = websocket.WebSocket()
        self.ws.connect(self.url)

    def get(self, data: str):
        self.ws.send(data)

    def recv(self):
        return self.ws.recv()

    def close(self):
        self.ws.close()


class DataThreadHttp(BaseHttpApi, DataCollector):

    def __init__(self, data_type: DataType, interval: int, client_id: str, mem: bool = None,
                 cpu: bool = None, storage: bool = None):
        super().__init__(host='localhost', port=5000)
        self.thread_status = ThreadStatus.THREAD_OFF
        self.data_type = data_type
        self.interval = interval
        self.cpu = cpu
        self.mem = mem
        self.storage = storage
        self.client_id = client_id
        if self.data_type is None:
            self.data_type = DataType.Megabyte

    def _data_thread(self):
        while self.thread_status == ThreadStatus.THREAD_ON:
            data = {
                "time": int(time.time()),
            }
            if self.cpu:
                data['cpu_load'] = cpu_load(0)
            if self.mem:
                data['mem'] = memory_info(self.data_type)['used']
            if self.storage:
                data['storage'] = storage_info(self.data_type)['used']
            response = self.post(f'/client/{self.client_id}', data=data,
                                 headers=self.header())
            logging.info(response.text)
            time.sleep(self.interval)
            if response.status_code != 202:
                self.thread_status = ThreadStatus.THREAD_OFF
                logging.warning(f'{response.status_code}')

    def stop(self):
        self.thread_status = ThreadStatus.THREAD_OFF
        logging.info('Thread off')

    def start(self):
        self.thread_status = ThreadStatus.THREAD_ON
        cpu_thread = threading.Thread(target=self._data_thread)
        cpu_thread.start()

    def time_work_write_log(self):
        response = self.get(f'/client/{self.client_id}/time')
        return response.json()

    def log_slice(self, start: int, end: int):
        response = self.get(f'/client/{self.client_id}/time/report?start={start}&end={end}')
        return response.json()

    def header(self):
        return {
            'Authorization': f'Basic {self.client_id}'
        }


class DataThreadWebSocket(WebSocketApi, DataCollector):

    def __init__(self, data_type: DataType, interval: int, client_id, cpu: bool = None, mem: bool = None, storage: bool = None):
        super().__init__(host='localhost', port=5000, path="/echo")
        self.thread_status = ThreadStatus.THREAD_OFF
        self.data_type = data_type
        self.client_id = client_id
        self.interval = interval
        self.cpu = cpu
        self.mem = mem
        self.storage = storage
        self.http_request = BaseHttpApi(host=self.host, port=self.port)
        if self.data_type is None:
            self.data_type = DataType.Megabyte

    def _data_thread(self):
        while self.thread_status == ThreadStatus.THREAD_ON:
            self.ws.send(json.dumps({"type": "HELLO"}))
            self.ws.recv()
            self.data_container = {"time": int(time.time())}
            if self.cpu:
                self.data_container['cpu_load'] = cpu_load(0)
            if self.mem:
                self.data_container['mem'] = memory_info(self.data_type)['used']
            if self.storage:
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

    def stop(self):
        self.thread_status = ThreadStatus.THREAD_OFF

    def start(self):
        self.thread_status = ThreadStatus.THREAD_ON
        cpu_thread = threading.Thread(target=self._data_thread)
        cpu_thread.start()

    def time_work_write_log(self):
        response = self.http_request.get(f'/client/{self.client_id}/time')
        return response.json()

    def log_slice(self, start: int, end: int):
        response = self.http_request.get(f'/client/{self.client_id}/time/report?start={start}&end={end}')
        return response.json()
