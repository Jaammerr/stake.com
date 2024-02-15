import flet as ft
from flet_core import ControlEvent

from .channel_filters import ChannelFilters
from loader import api


class ListChannels(ft.UserControl):
    def __init__(self, page: ft.Page, filters: ChannelFilters):
        super().__init__()
        self.page = page
        self.filters = filters
        self.channel_titles = {}

        self.flow = ft.ResponsiveRow()
        self.container = ft.Container(
            bgcolor=ft.colors.BLACK38, border_radius=10, padding=ft.padding.all(20)
        )
        self.selected_channel = None

    def update_channels(self):
        # response = requests.get('http://api:8000/data/channels')
        # json_data = response.json()
        json_data = api.get_channels()

        def on_focus_button(event: ControlEvent):
            event.control.style.side = {
                ft.MaterialState.DEFAULT: ft.BorderSide(6, ft.colors.GREY_700),
            }
            event.control.update()

        if json_data["status"] == "ok":
            channels = []

            for channel in json_data["result"]:
                title = (
                    f"{channel['channel_title'][:25]}.."
                    if len(channel["channel_title"]) > 25
                    else channel["channel_title"]
                )
                channels.append(
                    ft.Container(
                        ft.TextButton(
                            on_click=self.on_click,
                            style=ft.ButtonStyle(
                                side={
                                    ft.MaterialState.DEFAULT: ft.BorderSide(
                                        6, ft.colors.CYAN_900
                                    ),
                                    ft.MaterialState.HOVERED: ft.BorderSide(
                                        6, ft.colors.CYAN_700
                                    ),
                                },
                                shape=ft.ContinuousRectangleBorder(radius=140),
                            ),
                            height=45,
                            content=ft.Text(
                                title,
                                size=20,
                                weight=ft.FontWeight.W_600,
                                color=ft.colors.GREY,
                                max_lines=1,
                            ),
                        ),
                        border_radius=4,
                        col={"sm": 6, "md": 4, "xl": 2},
                    )
                )

                self.page.client_storage.set(title, channel["channel_id"])
                self.channel_titles[channel["channel_id"]] = channel["channel_title"]

            # for i in range(10):
            #     channels.append(
            #         ft.Container(
            #             ft.TextButton(f"Channel {i+1}"),
            #             col={"sm": 6, "md": 4, "xl": 2},
            #             border=ft.border.all(color=ft.colors.GREEN_300, width=2),
            #         )
            #     )

            self.flow.controls = channels
            self.container.content = ft.Column(
                [
                    ft.Container(
                        ft.Text(
                            "Active Channels",
                            size=25,
                            weight=ft.FontWeight.W_500,
                            font_family="Exo1",
                        ),
                        alignment=ft.alignment.top_left,
                    ),
                    self.flow,
                ],
            )

            # check if flow is bind to page
            if self.flow.page:
                self.flow.update()
                self.container.update()
                self.page.update()

    def close_last_channel(self):
        last_channel_id = self.page.client_storage.get("last_channel_id")
        if last_channel_id:
            self.page.client_storage.set("last_channel_id", 1)

            if self.selected_channel:
                self.selected_channel.style.side = {
                    ft.MaterialState.DEFAULT: ft.BorderSide(6, ft.colors.CYAN_900),
                    ft.MaterialState.HOVERED: ft.BorderSide(6, ft.colors.CYAN_700),
                }
                self.selected_channel.disabled = False
                self.selected_channel.update()
                self.selected_channel = None
                self.filters.close_filters()
                self.flow.update()
                self.container.update()
                self.page.update()

    def on_click(self, event: ControlEvent):
        if not event.control.page:
            # self.page.client_storage.set("last_channel_id", 5)
            event.control.page = self.page

        if not self.flow.page:
            self.flow.page = self.page

        if self.selected_channel and not self.selected_channel.page:
            self.selected_channel.page = self.page

        last_channel_id = self.page.client_storage.get("last_channel_id")
        channel_id = self.page.client_storage.get(event.control.content.value)

        if last_channel_id == channel_id:
            event.control.style.side = {
                ft.MaterialState.DEFAULT: ft.BorderSide(6, ft.colors.CYAN_900),
            }
            event.control.update()

            self.filters.close_filters()
            self.page.client_storage.set("last_channel_id", 1)

        else:
            if self.selected_channel:
                try:
                    self.selected_channel.style.side = {
                        ft.MaterialState.DEFAULT: ft.BorderSide(6, ft.colors.CYAN_900),
                        ft.MaterialState.HOVERED: ft.BorderSide(6, ft.colors.CYAN_700),
                    }
                    self.selected_channel.disabled = False
                    self.selected_channel.update()
                except:
                    pass

            event.control.disabled = True
            event.control.style.side = {
                ft.MaterialState.DEFAULT: ft.BorderSide(6, ft.colors.CYAN_700),
            }
            event.control.update()

            self.page.client_storage.set("last_channel_id", channel_id)

            self.flow.disabled = True
            self.flow.update()
            self.filters.open_filters(
                channel_id, event.control, self.channel_titles.get(channel_id)
            )
            self.flow.disabled = False
            self.flow.update()

            self.selected_channel = event.control

    def build(self):
        return self.container
