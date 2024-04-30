import flet as ft
from .servotab import ServoTab
from .settingtab import SettingTab
from .servo import ServoCommunication
import logging

APP_TITLE = "Servo Tester UI"

def main(page: ft.Page):
    page.title = APP_TITLE
    page.theme_mode = ft.ThemeMode.LIGHT

    page.controls = [
            # ft.AppBar(
            #     title=ft.Text(APP_TITLE),
            #     center_title=False,
            #     bgcolor=ft.colors.LIGHT_BLUE_ACCENT_700,
            # ),
            ft.Tabs(
                selected_index=0,
                tabs=[
                    ServoTab(text="Servo"),
                    SettingTab(storage=page.client_storage, text="Settings")
                ],
                animation_duration = 300,
                scrollable = False,
                expand=1,
            ),
        ]
    page.update()

if __name__ == "__main__":
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.DEBUG)
    ft.app(target=main)
