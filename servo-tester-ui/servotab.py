import flet as ft
from .servo import ServoProtocol, ServoCommunication, ServoData


class ServoContainer(ft.Container):
    def __init__(self, id, servo_list, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.servo_id = ServoID(id, servo_list, col={"sm": 3, "md": 2})

        self.slider = ft.Slider(min=-180, max=180, divisions=360*10,
                                label="{value}°", on_change=self.slider_change,
                                col={"sm": 6, "md": 8})
        self.slider.value = 0

        self.target_text = ft.Text(
            "Target: {:<+.1f}".format(self.slider.value))
        self.current_text = ft.Text("Current: ")
        self.value_text = ft.Column(
            [self.target_text, self.current_text],
            col={"sm": 3, "md": 2})

        self.content = ft.ResponsiveRow([
            self.servo_id,
            self.slider,
            self.value_text
        ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.SPACE_AROUND)

        self.selected = False

    def slider_change(self, e):
        servo_comm = ServoCommunication.get_instance()
        for servo in servo_comm.servo_list:
            if servo.id == self.servo_id.value:
                servo.target_angle = self.slider.value

        self.target_text.value = "Target: {:<+.1f}".format(self.slider.value)
        self.update()

class ServoID(ft.Row):
    def __init__(self, id, servo_list, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.value = id
        self.servo_list = servo_list
        self.id_text = ft.Text("ID: {:3d}".format(self.value))
        self.controls = \
            [
                ft.IconButton(ft.icons.REMOVE, on_click=self.click_minus),
                self.id_text,
                ft.IconButton(ft.icons.ADD, on_click=self.click_plus),
            ]

    def click_minus(self, e):
        value = self.value - 1
        while any(servo.id == value for servo in self.servo_list):
            value -= 1
        if value >= 0:  # TODO: change to min id value
            for servo in self.servo_list:
                if servo.id == self.value:
                    servo.id = value
            self.value = value
        self.id_text.value = "ID: {:3d}".format(self.value)
        self.update()

    def click_plus(self, e):
        value = self.value + 1
        while any(servo.id == value for servo in self.servo_list):
            value += 1
        if value < 255:  # TODO: change to max id value
            for servo in self.servo_list:
                if servo.id == self.value:
                    servo.id = value
            self.value = value
        self.id_text.value = "ID: {:3d}".format(self.value)
        self.update()


class ServoTab(ft.Tab):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.servo_comm = ServoCommunication.get_instance()
        self._header_content = [
            ft.Row([
                ft.IconButton(
                    icon=ft.icons.ADD,
                    icon_color=ft.colors.LIME_300,
                    tooltip="Add servo",
                    on_click=self.add_servo
                ),
                ft.IconButton(
                    icon=ft.icons.DELETE,
                    icon_color=ft.colors.PINK_300,
                    tooltip="Delete servo",
                    on_click=self.delete_servo
                ),
                ft.IconButton(
                    icon=ft.icons.SEND,
                    icon_color=ft.colors.BLUE_300,
                    tooltip="Send Position",
                    on_click=self.send_servo
                ),
                ft.IconButton(
                    icon=ft.icons.SYNC,
                    icon_color=ft.colors.BLUE_300,
                    tooltip="Sync Position",
                    selected=False,
                    on_click=self.sync_servo,
                )
            ], spacing=20),
        ]

        self.update_content()

    def add_servo(self, e):
        id = 1
        while any(servo.id == id for servo in self.servo_comm.servo_list):
            id += 1
        self.servo_comm.servo_list.append(ServoData(id))
        self.update_content()
        self.update()

    def select_servo(self, e):
        e.control.selected = not e.control.selected
        if e.control.selected:
            e.control.bgcolor = ft.colors.PINK_50
        else:
            e.control.bgcolor = ft.colors.BLUE_50
        e.control.update()

    def delete_servo(self, e):
        id_list = []
        for control in self.content.controls:
            if isinstance(control, ServoContainer) and control.selected:
                id_list.append(control.servo_id.value)
        for servo in self.servo_comm.servo_list:
            if servo.id in id_list:
                self.servo_comm.servo_list.remove(servo)
        self.update_content()
        self.update()

    def send_servo(self, e):
        servo_if = self.servo_comm._servo_if
        for servo in self.servo_comm.servo_list:
            servo_if.set_torque_enable(True, sid=servo.id)
            servo_if.set_target_position(servo.target_angle, sid=servo.id)

    def sync_servo(self, e):
        e.control.selected = not e.control.selected
        if e.control.selected:
            e.control.icon_color = ft.colors.BLUE_500
            e.control.bgcolor = ft.colors.BLUE_100
        else:
            e.control.icon_color = ft.colors.BLUE_300
            e.control.bgcolor = None
        e.control.update()

    def update_content(self) -> None:
        content = []
        content.extend(self._header_content)
        content.extend([
            ServoContainer(
                servo.id,
                self.servo_comm.servo_list,
                # border=ft.border.all(1, ft.colors.BLACK),
                bgcolor=ft.colors.BLUE_50,
                border_radius=10,
                on_click=self.select_servo
            )
            for servo in self.servo_comm.servo_list
        ])
        self.content = ft.Column(content, scroll=ft.ScrollMode.AUTO)
