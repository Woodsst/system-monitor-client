import logging
import time
import tkinter
from tkinter import Tk, ttk
from tkinter.messagebox import showinfo

from log_config import logger_config
from datatype import DataType
from web_api import DataThreadHttp, DataThreadWebSocket, DataCollector


class GUI:
    def __init__(self, data_collector: DataCollector) -> None:
        self.root = Tk()
        self.root.wm_title("System monitor")
        self.frm = ttk.Frame(self.root, padding=10)
        self.frm.grid()
        self.data_collector = data_collector
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.get_frame_constructing()
        self.start_log = tkinter.StringVar()
        self.end_log = tkinter.StringVar()
        ttk.Entry(self.frm, width=16, textvariable=self.start_log).grid(column=0, row=5)
        ttk.Entry(self.frm, width=16, textvariable=self.end_log).grid(column=0, row=7)

    def run_time(self):
        response = self.data_collector.time_work_write_log()
        return f'Start: {response["start"]}\n{time.ctime(int(response["start"]))}\nEnd: {response["end"]}\n{time.ctime(int(response["end"]))}'

    def on_closing(self):
        self._stop()
        self.root.destroy()

    def _start(self):
        self.data_collector.start()

    def _stop(self):
        self.data_collector.stop()

    def run(self):
        self.root.mainloop()

    def create_log_slice(self):
        response = self.data_collector.log_slice(self.start_log.get(), self.end_log.get())
        with open(f'data_slice_for_{self.data_collector.username}.csv', 'w') as file:
            file.write(f'time;cpu;memory;storage\n')
            for string in response['payload']:
                file.write(f'{string}\n')
        showinfo(title='Create file log slice', message=f'Data slice writtеn to data_slice_for_{self.data_collector.username}.csv')

    def get_frame_constructing(self):
        username = f"Hello {self.data_collector.username}!"
        ttk.Label(self.frm, text=username, width=len(username)).grid(column=0, row=0)
        ttk.Label(self.frm, text='start time for log slice').grid(column=0, row=4)
        ttk.Label(self.frm, text='end time for log slice').grid(column=0, row=6)
        ttk.Button(self.frm, width=15, text="start", command=self._start).grid(column=0, row=1)
        ttk.Button(self.frm, width=15,  text="stop", command=self._stop).grid(column=0, row=2)
        ttk.Button(self.frm, width=15, text="create log slice", command=self.create_log_slice).grid(column=0, row=8)
        ttk.Button(self.frm, width=15, text='run time', command=lambda: showinfo(title='run time', message=self.run_time())).grid(column=0, row=3)


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
