import serial.tools
import flet as ft
import serial.tools.list_ports
import platform
from .servo import ServoProtocol, ServoCommunication

TEXT_WIDTH = 120


class SettingTab(ft.Tab):
    def __init__(self, storage, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.content = ft.Column([
            ft.Row([
                ft.Text("Serial Port:", width=TEXT_WIDTH),
                ft.Dropdown(
                    options=[ft.dropdown.Option(serial_port)
                             for serial_port in self.get_serial_port_list()],
                    on_change=self.set_serial_port
                ),
            ]),
            ft.Row([
                ft.Text("Protocol:", width=TEXT_WIDTH),
                ft.Dropdown(
                    options=[ft.dropdown.Option(proto.name)
                             for proto in ServoProtocol],
                    on_change=self.set_proto_by_name
                ),
            ]),
            SamplingRaw(storage)
        ])
        self.servo_comm = ServoCommunication.get_instance()

    def set_proto_by_name(self, e):
        for proto in ServoProtocol:
            if proto.name == e.control.value:
                self.servo_comm.servo_proto = proto

    def set_serial_port(self, e):
        self.servo_comm.serial_path = e.control.value

    def get_serial_port_list(self):
        ports = serial.tools.list_ports.comports()    # ポートデータを取得
        return [port.device for port in ports]

class SamplingRaw(ft.Row):
    def __init__(self, storage, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.value = 10
        self.storage = storage
        if self.storage.contains_key("settings.sampling_period"):
            val = self.storage.get("settings.sampling_period")
            if isinstance(val, int) and val > 0:
                self.value = val

        self.sampling_period = ft.TextField(value=str(self.value), text_align=ft.TextAlign.RIGHT, width=100,
                                            on_change=self.change_value)

        self.controls = \
            [
                ft.Text("Sampling Period", width=TEXT_WIDTH),
                ft.IconButton(ft.icons.REMOVE, on_click=self.click_minus),
                self.sampling_period,
                ft.Text("ms"),
                ft.IconButton(ft.icons.ADD, on_click=self.click_plus),
            ]

    def click_minus(self, e):
        self.sampling_period.value = str(int(self.sampling_period.value) - 1)
        self.storage.set("settings.sampling_period",
                         int(self.sampling_period.value))
        self.page.update()

    def click_plus(self, e):
        self.sampling_period.value = str(int(self.sampling_period.value) + 1)
        self.storage.set("settings.sampling_period",
                         int(self.sampling_period.value))
        self.page.update()

    def change_value(self, e):
        self.storage.set("settings.sampling_period",
                         int(self.sampling_period.value))
