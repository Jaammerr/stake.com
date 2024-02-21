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

    def on_reload_channels(event):
        LoadingAnimation.start(page)

        list_channels.close_last_channel()
        list_channels.visible = False
        list_channels.update()

        list_channels.update_channels()
        list_channels.visible = True
        list_channels.update()

        LoadingAnimation.stop(page)


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
        title=ft.Text(
            "Stake Control Panel",
            size=25,
            color=ft.colors.WHITE,
            weight=ft.FontWeight.W_700,
            font_family="Exo1",
        ),
        actions=[ft.IconButton(icon=ft.icons.RESTART_ALT, on_click=on_reload_channels), AddChannel(page, list_channels)],
        center_title=True,
        toolbar_height=60,
    )

    list_channels.update_channels()
    page_row = ft.ResponsiveRow([list_channels, filters])

    return page_row


# def process_auth(page: ft.Page):
#
#     def on_submit_auth_token(event):
#         page.client_storage.set("auth_token", "123")
#         page.
#
#         print("Auth token: ", page.client_storage.get("auth_token"))
#
#     page.views.append(
#         ft.View(
#             route="/auth",
#             controls=[
#                 ft.Column(
#                     [
#                         ft.Text("Auth", size=30, weight=ft.FontWeight.W_700),
#                         ft.Text("Please enter your auth token"),
#                         ft.TextField(
#                             value="Auth token",
#                             on_change=lambda text: page.client_storage.set(
#                                 "auth_token", text
#                             ),
#                         ),
#                         ft.ElevatedButton(
#                             "Submit",
#                             on_click=on_submit_auth_token,
#                             color=ft.colors.BLUE,
#                         ),
#                     ],
#                     alignment=ft.alignment.center,
#                 ),
#             ]
#         )
#     )
#
#     auth_token = page.client_storage.get("auth_token")
#     if not auth_token:
#         page.go("/auth")





def main(page: ft.Page):
    LoadingAnimation.start(page)
    page_row = get_content(page)
    page.add(page_row)
    LoadingAnimation.stop(page)


if __name__ == "__main__":
    try:
        ft.app(
            target=main,
            view=ft.WEB_BROWSER,
            assets_dir="assets",
            port=8080,
            # host="0.0.0.0",
        )
    except Exception as error:
        raise Exception(f"Error while starting app: {error}")
