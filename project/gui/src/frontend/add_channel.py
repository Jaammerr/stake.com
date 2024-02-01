import flet as ft
from flet_core import ControlEvent

from .list_channels import ListChannels
from utils import LoadingAnimation
from loader import api


class AddChannel(ft.UserControl):
    def __init__(self, page: ft.Page, channels: ListChannels):
        super().__init__()
        self.page = page
        self.channels = channels

        self.text = "Add channel"
        self.input_channel_field = ft.TextField(border_radius=4, on_change=self.on_change_input)
        self.dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Channel creation"),
            content=ft.Text("Enter channel ID"),
            actions=[
                self.input_channel_field,
                ft.Container(
                    ft.Row(
                        [
                            ft.ElevatedButton(text="Cancel", color=ft.colors.RED_50, on_click=self.on_close, height=40, width=150),
                            ft.ElevatedButton(text="Submit", color=ft.colors.PRIMARY, on_click=self.on_submit, height=40, width=150),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,

                    ),
                    padding=ft.padding.all(10),
                )
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            # content_padding=ft.padding.all(20),
        )


    def on_close(self, event: ControlEvent):
        self.dialog.open = False
        self.page.update()

    def on_change_input(self, event: ControlEvent):
        self.input_channel_field.error_text = ""

        if event.control.value.replace("-", "").isdigit():
            self.input_channel_field.border_color = ft.colors.GREEN_300
        else:
            self.input_channel_field.border_color = ft.colors.RED_300

        self.page.update()


    def on_click(self, event: ControlEvent):
        self.page.dialog = self.dialog
        self.dialog.open = True
        self.page.update()


    def on_submit(self, event: ControlEvent):
        if not self.input_channel_field.value.replace("-", "").isdigit():
            self.input_channel_field.error_text = "Channel ID must be a number"
            self.page.update()
            return


        LoadingAnimation.start(self.page)
        self.page.dialog.open = False
        self.page.update()

        # response = requests.post('http://api:8000/channel/verify', json={
        #     'channel_id': int(self.input_channel_field.value)
        # })
        json_data = api.verify_channel(int(self.input_channel_field.value))

        if json_data['status'] == 'ok':
            success_snack_bar = ft.SnackBar(
                ft.Text(json_data["message"], text_align=ft.TextAlign.CENTER, size=17, weight=ft.FontWeight.W_500),
                behavior=ft.SnackBarBehavior.FLOATING,
                duration=3000,
                bgcolor=ft.colors.GREEN_300,
                show_close_icon=True,
                width=250,
            )
            self.page.snack_bar = success_snack_bar
            self.channels.close_last_channel()
            self.channels.update_channels()
            self.channels.container.update()

        else:
            error_snack_bar = ft.SnackBar(
                ft.Text(json_data['message'], text_align=ft.TextAlign.LEFT, size=17, weight=ft.FontWeight.W_500),
                behavior=ft.SnackBarBehavior.FLOATING,
                duration=3000,
                bgcolor=ft.colors.RED_300,
                show_close_icon=True,
                width=250,
            )
            self.page.snack_bar = error_snack_bar

        self.page.snack_bar.open = True
        self.page.update()
        LoadingAnimation.stop(self.page)

    def build(self):
        return ft.Container(
            ft.ElevatedButton(
                text=self.text,
                color=ft.colors.WHITE,
                on_click=self.on_click,
                style=ft.ButtonStyle(
                    side={
                        ft.MaterialState.DEFAULT: ft.BorderSide(2, ft.colors.GREEN),
                        ft.MaterialState.HOVERED: ft.BorderSide(4, ft.colors.GREEN),
                    },
                    shape=ft.ContinuousRectangleBorder(radius=15),
                ),
                height=45,
            ),
            padding=ft.padding.all(10),
        )
