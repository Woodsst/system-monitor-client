import requests
import websocket
from requests import Response


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
