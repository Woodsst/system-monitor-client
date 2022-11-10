import tkinter
import datetime
from tkinter import Tk, ttk
from tkinter.messagebox import showinfo

from monitoring_utilities.datatype import DataType
from web_api import (
    DataCollector,
    BaseHttpApi,
    DataThreadHttp,
    DataThreadWebSocket,
)


class Client:
    def __init__(self, data_collector: DataCollector) -> None:
        self.root = Tk()
        self.root.wm_title("System monitor")
        self.frm = ttk.Frame(self.root, padding=10)
        self.frm.grid()
        self.data_collector = data_collector
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.get_frame_constructing()
        self.start_log = ttk.Entry(self.frm, width=16)
        self.start_log.grid(column=0, row=5)
        self.end_log = ttk.Entry(self.frm, width=16)
        self.end_log.grid(column=1, row=5)
        self.time_for_convert = ttk.Entry(self.frm, width=25)
        self.time_for_convert.grid(column=0, row=7, columnspan=2)
        self.text_window = tkinter.Text(self.frm, width=33, height=2)
        self.text_window.grid(column=0, columnspan=2, row=6, pady=5)

    def show_time(self):
        response = self.data_collector.time_work_write_log()
        self.text_output(
            f'start = {response["start"]}\nend = {response["end"]}'
        )

    def convert_time(self):
        if len(self.time_for_convert.get()) < 11:
            convert = datetime.datetime.fromtimestamp(
                int(self.time_for_convert.get())
            )
        else:
            convert = int(
                time_converter(self.time_for_convert.get()).timestamp()
            )
        self.text_output(convert)

    def get_frame_constructing(self):
        ttk.Label(self.frm, text="start time").grid(column=0, row=4)
        ttk.Label(self.frm, text="end time").grid(column=1, row=4)
        ttk.Button(self.frm, width=15, text="start", command=self._start).grid(
            column=0, row=1
        )
        ttk.Button(self.frm, width=15, text="stop", command=self._stop).grid(
            column=1, row=1
        )
        ttk.Button(
            self.frm,
            width=15,
            text="create log slice",
            command=self.create_log_slice,
        ).grid(column=1, row=2)
        ttk.Button(
            self.frm, width=15, text="run time", command=self.show_time
        ).grid(column=0, row=2)
        ttk.Button(
            self.frm, width=15, text="convert", command=self.convert_time
        ).grid(column=0, row=9, pady=5, columnspan=2)

    def on_closing(self):
        self._stop()
        self.root.destroy()

    def _start(self):
        self.text_output("Start data thread")
        self.data_collector.start()

    def _stop(self):
        self.text_output("Stop data thread")
        self.data_collector.stop()

    def run(self):
        self.root.mainloop()

    def create_log_slice(self):
        response = self.data_collector.log_slice(
            self.start_log.get(), self.end_log.get()
        )
        payload = response.get("payload")
        if payload is None:
            self.text_output("log slice bad request")
            return
        with open("log_slice.csv", "w", encoding="utf-8") as file:
            for string in payload:
                file.write(f"{string}\n")
        self.text_output("Log slice file create")

    def text_output(self, text: str) -> None:
        self.text_window.delete("1.0", "end")
        self.text_window.insert("1.0", text)


class Login:
    def __init__(self):
        self.username = None
        self.password = None
        self.root = Tk()
        self.root.wm_title("Login")
        self.frame = ttk.Frame(self.root, padding=5)
        self.frame.grid()
        self.get_frame_constructing()

    def run(self):
        self.root.mainloop()

    def get_frame_constructing(self):
        self.username = username = tkinter.StringVar()
        self.password = password = tkinter.StringVar()
        ttk.Label(self.frame, text="Username").grid(column=0, row=0, padx=5)
        ttk.Label(self.frame, text="Password").grid(column=0, row=2, padx=5)
        ttk.Entry(self.frame, width=15, textvariable=username).grid(
            column=1, row=0, padx=5, pady=6
        )
        ttk.Entry(self.frame, width=15, textvariable=password).grid(
            column=1, row=2, padx=5
        )
        ttk.Button(self.frame, width=10, text="Ok", command=self.login).grid(
            column=0, row=3, pady=3
        )

    def login(self):
        api = BaseHttpApi("localhost", 5000)
        response = api.post(
            "/client",
            json={
                "username": self.username.get(),
                "pass": self.password.get(),
            },
        )
        if response.json().get("client_id") is not None:
            showinfo(message=f"Hello: {self.username.get()}", title="login")
            self.root.destroy()
            settings = Settings(
                response.json()["client_id"], self.username.get()
            )
            settings.run()
        else:
            if response.json().get("error") == "unsupportable username":
                showinfo(message="name must start with a letter")
                return
            showinfo(message="incorrect user or pass", title="login")


class Settings:
    def __init__(self, client_id: str, username: str):
        self.client_id = client_id
        self.username = username
        self.root = Tk()
        self.root.wm_title("Settings")
        self.frame = ttk.Frame(self.root, padding=5)
        self.frame.grid()
        self.get_frame_constructing()
        self.cpu = tkinter.BooleanVar()
        self.memory = tkinter.BooleanVar()
        self.storage = tkinter.BooleanVar()
        self.interval = tkinter.IntVar()
        self.http = tkinter.BooleanVar()
        self.data_type = tkinter.StringVar()
        ttk.Spinbox(
            self.frame, width=5, from_=0, to=60, textvariable=self.interval
        ).grid(column=1, row=1)
        ttk.Checkbutton(
            self.frame, text="cpu", variable=self.cpu, offvalue=0, onvalue=1
        ).grid(column=0, row=2)
        ttk.Checkbutton(
            self.frame,
            text="memory",
            variable=self.memory,
            offvalue=0,
            onvalue=1,
        ).grid(column=0, row=3)
        ttk.Checkbutton(
            self.frame,
            text="storage",
            variable=self.storage,
            offvalue=0,
            onvalue=1,
        ).grid(column=0, row=4)
        ttk.Radiobutton(
            self.frame, text="Http", variable=self.http, value=True
        ).grid(column=1, row=3)
        ttk.Radiobutton(
            self.frame, text="Web Socket", variable=self.http, value=False
        ).grid(column=1, row=4)
        data_type_values = ["TB", "GB", "MB", "KB", "B"]
        ttk.Combobox(
            self.frame,
            values=data_type_values,
            width=10,
            textvariable=self.data_type,
        ).grid(column=1, row=0, pady=3)

    def get_frame_constructing(self):
        ttk.Label(self.frame, text="Choice data type for log").grid(
            column=0, row=0, padx=5
        )
        ttk.Label(self.frame, text="Data acquisition interval").grid(
            column=0, row=1
        )
        ttk.Button(self.frame, text="Ok", command=self.start_client).grid(
            column=1, row=5
        )

    def run(self):
        self.root.mainloop()

    def start_client(self):
        if self.http.get() is True:
            client = Client(self.http_data_thread())
        else:
            client = Client(self.web_socket_data_thread())
        showinfo(title="welcome", message="Welcome to system monitor client")
        self.root.destroy()
        client.run()

    def http_data_thread(self):
        http_thread = DataThreadHttp(
            interval=self.interval.get(),
            mem=self.memory.get(),
            storage=self.storage.get(),
            cpu=self.cpu.get(),
            data_type=self.data_type_choice(self.data_type.get()),
            client_id=self.client_id,
            username=self.username,
        )
        return http_thread

    def web_socket_data_thread(self):
        ws_thread = DataThreadWebSocket(
            interval=self.interval.get(),
            mem=self.memory.get(),
            storage=self.storage.get(),
            cpu=self.cpu.get(),
            data_type=self.data_type_choice(self.data_type.get()),
            client_id=self.client_id,
            username=self.username,
        )
        return ws_thread

    @staticmethod
    def data_type_choice(data):
        for value in DataType:
            if value.value == data:
                return value
        return DataType.MEGABYTE


def time_converter(str_time: str) -> datetime:
    str_time = str_time.split(" ")
    date_s = str_time[0].split("-")
    year = int(date_s[0])
    month = int(date_s[1])
    day = int(date_s[2])
    date_t = str_time[1].split(":")
    hour = int(date_t[0])
    minute = int(date_t[1])
    sec = int(date_t[2])
    return datetime.datetime(
        year=year,
        month=month,
        day=day,
        hour=hour,
        minute=minute,
        second=sec,
        microsecond=0,
    )
