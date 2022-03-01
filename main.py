import logging
from tkinter import Tk, ttk

from log_config import logger_config
from datatype import DataType
from web_api import DataThreadHttp, DataThreadWebSocket, DataCollector


class GUI:
    def __init__(self, data_collector: DataCollector) -> None:
        self.root = Tk()
        self.root.wm_title("idle")
        self.frm = ttk.Frame(self.root, padding=10)
        self.frm.grid()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        ttk.Label(self.frm, text="Hello from client!").grid(column=0, row=0)
        ttk.Button(self.frm, text="start", command=self._start).grid(column=1, row=0)
        ttk.Button(self.frm, text="stop", command=self._stop).grid(column=2, row=0)
        self.data_collector = data_collector

    def on_closing(self):
        self._stop()
        self.root.destroy()

    def _start(self):
        self.data_collector.start()

    def _stop(self):
        self.data_collector.stop()

    def run(self):
        self.root.mainloop()


if __name__ == '__main__':
    logger_config()
    logging.info('client start')
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
    collector = None
    if args.http:
        collector = DataThreadHttp(data_type=DataType.Megabyte,
                                   interval=args.interval,
                                   cpu=args.cpu,
                                   mem=args.memory,
                                   storage=args.storage,
                                   username=args.user,
                                   password=args.password)
    if args.websocket:
        collector = DataThreadWebSocket(data_type=DataType.Megabyte,
                                        interval=args.interval,
                                        cpu=args.cpu,
                                        mem=args.memory,
                                        storage=args.storage,
                                        username=args.user,
                                        password=args.password)
    gui = GUI(collector)
    gui.run()
