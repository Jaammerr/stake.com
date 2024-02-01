from concurrent.futures import ThreadPoolExecutor
from typing import Tuple, Any

import flet as ft
import requests
from flet_core import ControlEvent
from utils import is_float, LoadingAnimation
from loader import api


class ChannelFilters(ft.UserControl):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.channel_title = None
        self.channel_button = None
        self.page = page
        self.channel_id = 0
        self.filters = {}
        self.sports_filters = []

        self.flow = ft.ResponsiveRow()
        self.row = ft.Column(spacing=40)
        self.container = ft.Container(
            bgcolor=ft.colors.BLACK38,
            border_radius=10,
            padding=ft.padding.all(20),
            visible=False,
        )


    def get_sports_filters_container(self, sports: list[str], search_bar: ft.SearchBar, container: ft.Container) -> None:
        new_sports_filters = []

        def get_old_sport_data(_sport: str) -> dict:
            for sport_data in self.sports_filters:
                if sport_data.get("sport") == _sport:
                    return sport_data

            return {}


        def on_change(event: ControlEvent):
            changed_sport = event.control.hint_text
            changed_value_name = event.control.label.lower().replace(" ", "_")
            changed_value = event.control.value

            if not is_float(changed_value):
                event.control.error_text = "Value must be a number"
                event.control.update()
                return

            event.control.error_text = ""
            event.control.border_color = ft.colors.GREEN_900
            event.control.update()

            if changed_sport in [sport_data.get("sport") for sport_data in self.sports_filters]:
                for sport_data in self.sports_filters:
                    if sport_data.get("sport") == changed_sport:
                        sport_data[changed_value_name] = changed_value
                        return

            else:
                if changed_sport not in [sport_data.get("sport") for sport_data in new_sports_filters]:
                    new_sports_filters.append({
                        "sport": changed_sport,
                        changed_value_name: changed_value
                    })
                else:
                    for sport_data in new_sports_filters:
                        if sport_data.get("sport") == changed_sport:
                            sport_data[changed_value_name] = changed_value
                            return

            container.border = ft.border.all(color=ft.colors.GREEN_900, width=2)
            container.update()


        def on_submit_values(event: ControlEvent):
            self.page.views.pop()
            top_view = self.page.views[-1]
            self.page.go(top_view.route)

            search_bar.close_view(text=search_bar.value)
            for sport_data in new_sports_filters:
                old_data = get_old_sport_data(sport_data.get("sport"))
                if old_data:
                    if old_data.get("filter_uuid") and not sport_data.get("filter_uuid"):
                        sport_data["filter_uuid"] = old_data.get("filter_uuid")

                    if old_data.get("min_multiplier") and not sport_data.get("min_multiplier"):
                        sport_data["min_multiplier"] = old_data.get("min_multiplier")

                    if old_data.get("max_multiplier") and not sport_data.get("max_multiplier"):
                        sport_data["max_multiplier"] = old_data.get("max_multiplier")

                    if old_data.get("min_amount") and not sport_data.get("min_amount"):
                        sport_data["min_amount"] = old_data.get("min_amount")

                    if old_data.get("max_amount") and not sport_data.get("max_amount"):
                        sport_data["max_amount"] = old_data.get("max_amount")


            if new_sports_filters:
                for _sport in sports:
                    if _sport not in [sport_data.get("sport") for sport_data in new_sports_filters]:
                        new_sports_filters.append(get_old_sport_data(_sport))

                self.sports_filters = new_sports_filters

            else:
                for _sport in sports:
                    if _sport not in [sport_data.get("sport") for sport_data in self.sports_filters]:
                        self.sports_filters.append({"sport": _sport})

                # delete all sports from self.sports_filters except those that are in sports
                for sport_data in self.sports_filters:
                    if sport_data.get("sport") not in sports:
                        self.sports_filters.remove(sport_data)


            for sport_data in self.sports_filters:
                if not sport_data:
                    self.sports_filters.remove(sport_data)


            # clear duplicates in self.sports_filters
            self.sports_filters = list({v['sport']: v for v in self.sports_filters}.values())



        sports_filters = ft.Column(scroll=ft.ScrollMode.ALWAYS, spacing=30)
        for sport in sports:
            old_sport_data = get_old_sport_data(sport)

            sport_container = ft.Container(
                ft.Column(
                    [
                        ft.Container(ft.Text(sport, size=25, weight=ft.FontWeight.W_500, font_family="Exo1"), alignment=ft.alignment.top_left),
                        ft.Row(
                            [
                                ft.TextField(label="Min multiplier", hint_text=sport, border_radius=15, border_color=ft.colors.GREY_700, border_width=2, value=old_sport_data.get("min_multiplier") if old_sport_data.get("min_multiplier") else "0", on_change=on_change),
                                ft.TextField(label="Max multiplier", hint_text=sport, border_radius=15, border_color=ft.colors.GREY_700, border_width=2, value=old_sport_data.get("max_multiplier") if old_sport_data.get("max_multiplier") else "0", on_change=on_change),
                            ],
                            spacing=30
                        ),
                        ft.Row(
                            [
                                ft.TextField(label="Min amount", hint_text=sport, border_radius=15, border_color=ft.colors.GREY_700, border_width=2, value=old_sport_data.get("min_amount") if old_sport_data.get("min_amount") else "0", on_change=on_change),
                                ft.TextField(label="Max amount", hint_text=sport, border_radius=15, border_color=ft.colors.GREY_700, border_width=2, value=old_sport_data.get("max_amount") if old_sport_data.get("max_amount") else "0", on_change=on_change),
                            ],
                            spacing=30
                        )
                    ],
                    scroll=ft.ScrollMode.ALWAYS,
                    spacing=30
                ),
                bgcolor=ft.colors.GREY_900,
                padding=ft.padding.all(20),
                border_radius=10,
            )

            sports_filters.controls.append(sport_container)

        self.page.views.append(ft.View(
            route="/full",
            appbar=ft.AppBar(title=ft.Text("Sports Filters")),
            floating_action_button=ft.FloatingActionButton(width=70, height=70, on_click=on_submit_values, bgcolor=ft.colors.BLACK, content=ft.Container(border=ft.border.all(color=ft.colors.GREEN_700, width=2), padding=ft.padding.all(10), border_radius=10, content=ft.Icon(ft.icons.ARROW_UPWARD_SHARP))),
            floating_action_button_location=ft.FloatingActionButtonLocation.MINI_CENTER_TOP,
            controls=[
                ft.Container(
                    ft.Column(
                        [
                            sports_filters
                        ],
                    ),
                    padding=ft.padding.only(top=40, left=20, right=20, bottom=40),
                )
            ],
            bgcolor=ft.colors.BLACK,
            fullscreen_dialog=True,
            scroll=ft.ScrollMode.ALWAYS,
        ))


    def get_filters(self) -> None:
        # response = requests.post('http://api:8000/channel/get_filters', json={
        #     'channel_id': self.channel_id
        # })
        json_data = api.get_channel_filters(self.channel_id)

        if json_data['status'] == 'ok':
            filters = json_data['result']['filters']
            if not filters:
                self.filters = {}
            else:
                self.filters = filters

            sports_filters = json_data['result']['sports_filters']
            if not sports_filters:
                self.sports_filters = []
            else:
                self.sports_filters = sports_filters

    def update_sports_filter(self):

        def handle_click(event: ControlEvent):
            sport = event.control.data
            old_sports = search_bar.value

            if sport == "All":
                search_bar.value = "All"
            else:
                if sport not in old_sports:
                    search_bar.value = f"{old_sports}, {sport}" if old_sports else sport

                else:
                    if old_sports.startswith(f"{sport}, "):
                        search_bar.value = old_sports[len(f"{sport}, "):]
                    else:
                        search_bar.value = old_sports.replace(f", {sport}", "")

            search_bar.value = search_bar.value.replace("All, ", "")
            container.border = ft.border.all(color=ft.colors.GREEN_900, width=2)

            search_bar.update()
            container.update()

        def process_submit(event: ControlEvent):
            sports = search_bar.value

            if not sports or sports == "All":
                self.sports_filters = [{"sport": "All"}]
                search_bar.close_view(text="All")
                container.border = ft.border.all(color=ft.colors.GREEN_900, width=2)
                container.update()
                return

            list_sports = sports.split(", ")
            # удалить все спорты с self.sports_filters кроме тех, которые есть в list_sports
            # for sport_data in self.sports_filters:
            #     if sport_data.get("sport") not in list_sports:
            #         self.sports_filters.remove(sport_data)

            self.get_sports_filters_container(list_sports, search_bar, container)
            self.page.go("/full")
            self.page.update()


        values = ["All", "Soccer", "Tennis", "Basketball", "American Football", "Ice Hockey", "Table Tennis", "Cricket", "CS2", "League of Legends", "Dota 2", "Alpine Skiing", "Aussie Rules", "Badminton", "Bandy", "Baseball", "Biathlon", "Bowls", "Boxing", "Cross-Country", "Cycling", "Darts", "Field Hockey", "Floorball", "Formula 1", "Futsal", "Gaelic Football", "Golf", "Handball", "Kabaddi", "Lacrosse", "MMA", "Motorsport", "Olympics", "Rugby", "Snooker", "Stock Car Racing", "Volleyball",
                  "Waterpolo"]
        values = sorted(values)


        submit_button = ft.ElevatedButton(
            content=ft.Text("Submit", size=20, weight=ft.FontWeight.W_500, font_family="Exo1"),
            color=ft.colors.WHITE,
            style=ft.ButtonStyle(
                shape=ft.ContinuousRectangleBorder(radius=15),
            ),
            width=6000,
            height=55,
            on_click=process_submit
        )
        sports_controls = ft.Column([submit_button])
        for sport in values:
            sports_controls.controls.append(ft.ListTile(title=ft.Text(sport), data=sport, on_click=handle_click))


        search_bar = ft.SearchBar(
            view_elevation=4,
            divider_color=ft.colors.GREY_900,
            bar_hint_text="Select sports..." if not self.sports_filters else None,
            value=", ".join([
                sport.get("sport") for sport in self.sports_filters
            ]) if self.sports_filters else "All",
            view_hint_text="Choose a sport from the suggestions...",
            controls=[
                sports_controls
            ],
            bar_bgcolor=ft.colors.BLACK87,
        )


        container = ft.Container(
            search_bar,
            border=ft.border.all(color=ft.colors.GREY_700, width=2),
            border_radius=20,
            bgcolor=ft.colors.BLACK38,
        )

        anchor = ft.Container(
            ft.Column(
                [
                    ft.Container(ft.Text("Sports", size=25, weight=ft.FontWeight.W_500, font_family="Exo1"), alignment=ft.alignment.top_left),
                    ft.Container(container, width=6000, bgcolor=ft.colors.BLACK26, padding=ft.padding.all(20), border_radius=6)
                ],
                spacing=10
            )
        )

        self.row.controls.append(anchor)


    def update_users_filter(self):

        def on_change_users(event: ControlEvent):
            users = input_field.value
            if users:
                users = users.split(", ")
                users = [user for user in users if user]

                input_field.error_text = ""
                input_field.border_color = ft.colors.GREEN_900

                self.filters["users"]["values"] = users
            else:
                input_field.error_text = "Users field can't be empty"

            input_field.update()


        input_field = ft.TextField(label="Users", hint_text="Enter users..", border_radius=15, border_color=ft.colors.GREY_700, border_width=2, on_change=on_change_users)

        if self.filters.get("users"):
            if self.filters.get("users").get("values"):
                input_field.value = ", ".join(self.filters.get("users").get("values"))
            else:
                input_field.value = "All"


        anchor = ft.Container(
            ft.Column(
                [
                    ft.Container(ft.Text("Users", size=25, weight=ft.FontWeight.W_500, font_family="Exo1"), alignment=ft.alignment.top_left),
                    ft.Container(input_field, bgcolor=ft.colors.BLACK26, padding=ft.padding.all(20), border_radius=6)
                ],
                spacing=10
            )
        )
        self.row.controls.append(anchor)



    def update_min_max_multiplier(self):
        min_multiplier = ft.TextField(label="Min multiplier", hint_text="Enter min multiplier..", border_radius=15, border_color=ft.colors.GREY_700, border_width=2)
        max_multiplier = ft.TextField(label="Max multiplier", hint_text="Enter max multiplier..", border_radius=15, border_color=ft.colors.GREY_700, border_width=2)

        if self.filters.get("min_multiplier"):
            min_multiplier.value = self.filters.get("min_multiplier")

        if self.filters.get("max_multiplier"):
            max_multiplier.value = self.filters.get("max_multiplier")

        anchor = ft.Container(
            ft.Column(
                [
                    ft.Container(ft.Text("Total Multiplier", size=25, weight=ft.FontWeight.W_500, font_family="Exo1"), alignment=ft.alignment.top_left),
                    ft.Row(
                        [
                            min_multiplier,
                            max_multiplier
                        ]
                    )
                ],
                spacing=10
            )
        )
        self.row.controls.append(anchor)


    def update_min_max_amount(self):
        min_amount = ft.TextField(label="Min amount", hint_text="Enter min amount..", border_radius=15, border_color=ft.colors.GREY_700, border_width=2)
        max_amount = ft.TextField(label="Max amount", hint_text="Enter max amount..", border_radius=15, border_color=ft.colors.GREY_700, border_width=2)

        if self.filters.get("min_amount"):
            min_amount.value = self.filters.get("min_amount")

        if self.filters.get("max_amount"):
            max_amount.value = self.filters.get("max_amount")

        anchor = ft.Container(
            ft.Column(
                [
                    ft.Container(ft.Text("Bet Amount", size=25, weight=ft.FontWeight.W_500, font_family="Exo1"), alignment=ft.alignment.top_left),
                    ft.Row(
                        [
                            min_amount,
                            max_amount
                        ]
                    )
                ]
            )
        )
        self.row.controls.append(anchor)


    def update_type_of_bet_and_count_of_outcomes(self):

        def on_submit_count_of_outcomes(event: ControlEvent):
            self.filters["count_of_outcomes"] = count_of_outcomes.value.replace("+", "")
            count_of_outcomes.border_color = ft.colors.GREEN_900
            count_of_outcomes.update()

        def on_submit_include_sports(event: ControlEvent):
            self.filters["include_sports"] = include_sports_checkbox.value

            include_sports_container.border_color = ft.colors.GREEN_900
            include_sports_container.update()

        def on_submit_bet_type(event: ControlEvent):
            if type_of_bet_field.value == "Multiple":
                container.visible = True
                include_sports_container.visible = True
            else:
                container.visible = False
                include_sports_container.visible = False

            self.filters["type_of_bet"] = type_of_bet_field.value

            type_of_bet_field.border_color = ft.colors.GREEN_900
            type_of_bet_field.update()
            container.update()
            include_sports_container.update()

        type_of_bet_field = ft.Dropdown(
            value=self.filters.get("type_of_bet") if self.filters.get("type_of_bet") else "All",
            options=[
                ft.dropdown.Option("All"),
                ft.dropdown.Option("Single"),
                ft.dropdown.Option("Multiple"),
            ],
            border_color=ft.colors.GREY_700,
            border_radius=15,
            border_width=2,
            on_change=on_submit_bet_type
        )


        outcomes_value = self.filters.get('count_of_outcomes')
        if outcomes_value:
            if int(outcomes_value) > 3:
                outcomes_value = "4+"
        else:
            outcomes_value = str(outcomes_value)

        count_of_outcomes = ft.Dropdown(
            value=outcomes_value,
            options=[
                ft.dropdown.Option("2"),
                ft.dropdown.Option("3"),
                ft.dropdown.Option("4+"),
            ],
            border_color=ft.colors.GREY_700,
            border_radius=15,
            border_width=2,
            on_change=on_submit_count_of_outcomes
        )

        container = ft.Container(
            count_of_outcomes,
            bgcolor=ft.colors.BLACK26,
            padding=ft.padding.all(20),
            border_radius=6,
            visible=True if self.filters.get("type_of_bet") == "Multiple" else False
        )

        include_sports_checkbox = ft.Checkbox(
            label="Include all sports",
            on_change=on_submit_include_sports,
            value=True if self.filters.get("include_sports") else False,
            expand=True,
            animate_size=50
        )

        include_sports_container = ft.Container(
            include_sports_checkbox,
            visible=True if self.filters.get("type_of_bet") == "Multiple" else False,
            bgcolor=ft.colors.BLACK26,
            padding=ft.padding.all(20),
        )

        anchor = ft.Container(
            ft.Column(
                [
                    ft.Container(ft.Text("Type Of Bet", size=25, weight=ft.FontWeight.W_500, font_family="Exo1", ), alignment=ft.alignment.top_left),
                    ft.Column(
                        [
                            ft.Container(type_of_bet_field, width=6000, bgcolor=ft.colors.BLACK26, padding=ft.padding.all(20), border_radius=6),
                            container,
                            include_sports_container
                        ],
                        spacing=30
                    )
                ],
                spacing=10
            )
        )

        self.row.controls.append(anchor)

        # if self.filters.get("count_of_outcomes"):
        #     count_of_outcomes.value = self.filters.get("count_of_outcomes")
        #     container.visible = True
        #     container.update()



    def update_all_filters(self):
        self.update_sports_filter()
        self.update_users_filter()
        self.update_type_of_bet_and_count_of_outcomes()

        self.flow.controls = [self.row]



    def update_all_filters_in_db(self, event: ControlEvent):
        self.close_filters()
        LoadingAnimation.start(self.page)

        with ThreadPoolExecutor() as executor:
            future1 = executor.submit(api.update_channel_filters, self.channel_id, self.filters)
            future2 = executor.submit(api.update_sports_filters, self.channel_id, self.sports_filters)

            result1 = future1.result()
            result2 = future2.result()

            print(result1, result2)

            if result1['status'] == 'ok' and result2['status'] == 'ok':
                success_snack_bar = ft.SnackBar(
                    ft.Text("Filters updated successfully", text_align=ft.TextAlign.CENTER, size=17, weight=ft.FontWeight.W_500),
                    behavior=ft.SnackBarBehavior.FLOATING,
                    duration=3000,
                    bgcolor=ft.colors.GREEN_300,
                    show_close_icon=True,
                    width=250,
                )
                self.page.snack_bar = success_snack_bar

            else:
                error_snack_bar = ft.SnackBar(
                    ft.Text(f"Error: Failed to update filters", text_align=ft.TextAlign.LEFT, size=17, weight=ft.FontWeight.W_500),
                    behavior=ft.SnackBarBehavior.FLOATING,
                    duration=3000,
                    bgcolor=ft.colors.RED_300,
                    show_close_icon=True,
                    width=250,
                )
                self.page.snack_bar = error_snack_bar

            self.page.snack_bar.open = True
            self.open_filters(self.channel_id, self.channel_button, self.channel_title)
            LoadingAnimation.stop(self.page)

    def open_filters(self, channel_id: int, channel_button, channel_title: str = None):
        LoadingAnimation.start(self.page)
        self.row.controls.clear()

        self.channel_id = channel_id
        self.channel_title = channel_title
        self.channel_button = channel_button

        self.get_filters()
        self.update_all_filters()

        def process_delete_channel(event: ControlEvent):
            close_dlg(event)
            LoadingAnimation.start(self.page)

            # response = requests.post('http://api:8000/channel/delete', json={
            #     'channel_id': self.channel_id
            # })
            json_data = api.delete_channel(self.channel_id)

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
                self.page.snack_bar.open = True
                self.channel_button.visible = False
                self.channel_button.disabled = True
                self.channel_button.update()
                self.close_filters()

            else:
                error_snack_bar = ft.SnackBar(
                    ft.Text(json_data["message"], text_align=ft.TextAlign.LEFT, size=17, weight=ft.FontWeight.W_500),
                    behavior=ft.SnackBarBehavior.FLOATING,
                    duration=3000,
                    bgcolor=ft.colors.RED_300,
                    show_close_icon=True,
                    width=250,
                )
                self.page.snack_bar = error_snack_bar
                self.page.snack_bar.open = True

            LoadingAnimation.stop(self.page)



        def open_dlg(event: ControlEvent):
            self.page.dialog = dlg_delete_channel
            dlg_delete_channel.open = True
            self.page.update()

        def close_dlg(event: ControlEvent):
            dlg_delete_channel.open = False
            self.page.update()

        dlg_delete_channel = ft.AlertDialog(
            modal=True,
            title=ft.Text("Please confirm"),
            content=ft.Text("Do you really want to delete this channel ?"),
            actions=[
                ft.TextButton("No", on_click=close_dlg),
                ft.TextButton("Yes", on_click=process_delete_channel),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        title_ct = ft.Row(
            [
                ft.Container(
                    ft.Row(
                        [
                            ft.Container(),
                            ft.Text(
                                f"Channel: {self.channel_title}", size=25, weight=ft.FontWeight.W_500, color=ft.colors.WHITE, font_family="Exo1",
                            ),
                            ft.Container(
                                ft.IconButton(
                                    icon=ft.icons.DELETE_FOREVER_OUTLINED,
                                    icon_color=ft.colors.RED_900,
                                    icon_size=30,
                                    on_click=open_dlg,
                                ),
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    bgcolor=ft.colors.GREY_900,
                    border_radius=10,
                    height=60,
                    border=ft.border.all(color=ft.colors.CYAN_900, width=2),
                    padding=ft.padding.only(right=15),
                ),

            ],
            wrap=True
        )

        self.container.content = ft.Column(
            [
                title_ct,
                self.flow,
                ft.Container(
                    ft.ElevatedButton(
                        content=ft.Text("Update", size=20, weight=ft.FontWeight.W_500, font_family="Exo1"),
                        color=ft.colors.WHITE,
                        style=ft.ButtonStyle(
                            side={
                                ft.MaterialState.DEFAULT: ft.BorderSide(3, ft.colors.CYAN_900),
                                ft.MaterialState.HOVERED: ft.BorderSide(4, ft.colors.CYAN_700),
                            },
                            shape=ft.ContinuousRectangleBorder(radius=15),
                        ),
                        height=45,
                        width=200,
                        on_click=self.update_all_filters_in_db
                    ),
                    padding=ft.padding.all(10),
                    alignment=ft.alignment.center
                )
            ],
            # height=self.page.height
        )

        self.container.visible = True
        self.container.update()
        LoadingAnimation.stop(self.page)



    def is_activated(self) -> bool:
        return self.container.visible


    def close_filters(self):
        self.container.visible = False
        self.container.update()


    def build(self):
        return self.container
