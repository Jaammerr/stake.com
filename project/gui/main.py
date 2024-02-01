import flet as ft

from src import ChannelFilters, ListChannels, AddChannel
from utils import LoadingAnimation


def get_content(page: ft.Page):
    page.scroll = ft.ScrollMode.ALWAYS
    page.theme_mode = ft.ThemeMode.DARK

    def handle_view_pop(view: ft.ViewPopEvent):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    page.fonts = {
        "lemon": "fonts/Lemon-Regular.ttf",
        "Exo1": "fonts/Exo_1.ttf",
        "Exo2": "fonts/Exo_2.ttf",
    }
    page.on_view_pop = handle_view_pop

    filters = ChannelFilters(page)
    list_channels = ListChannels(page, filters)

    page.appbar = ft.AppBar(
        bgcolor=ft.colors.BLACK38,
        title=ft.Text("Stake Control Panel", size=25, color=ft.colors.WHITE, weight=ft.FontWeight.W_700, font_family="Exo1"),
        actions=[
            AddChannel(page, list_channels)
        ],
        center_title=True,
        toolbar_height=60,
    )

    list_channels.update_channels()
    page_row = ft.ResponsiveRow([
        list_channels,
        filters
    ])

    return page_row


def main(page: ft.Page):
    LoadingAnimation.start(page)
    page_row = get_content(page)

    page.add(
        page_row
    )

    LoadingAnimation.stop(page)


ft.app(target=main, view=ft.WEB_BROWSER, assets_dir="assets")
