import flet as ft


class LoadingAnimation:
    @classmethod
    def start(cls, page: ft.Page):
        page.splash = ft.ProgressBar(color=ft.colors.GREEN_300)
        page.update()


    @classmethod
    def stop(cls, page: ft.Page):
        page.splash = None
        page.update()
