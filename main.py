import os
import json
import flet as ft
import firebase_admin
from firebase_admin import credentials, db
import datetime

if not firebase_admin._apps:
    firebase_key = os.environ.get("FIREBASE_KEY")
    if firebase_key:
        key_dict = json.loads(firebase_key)
        cred = credentials.Certificate(key_dict)
        firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://status-app-e6835-default-rtdb.asia-southeast1.firebasedatabase.app/'
        })
    else:
        firebase_admin.initialize_app(options={
            'databaseURL': 'https://status-app-e6835-default-rtdb.asia-southeast1.firebasedatabase.app/'
        })

ref = db.reference('my_status')

def main(page: ft.Page):
    page.title = "ステータス共有"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.bgcolor = ft.Colors.BLUE_GREY_50
    page.padding = 30

    status_icon = ft.Icon(ft.Icons.HOME_ROUNDED, size=80, color=ft.Colors.BLUE_400)
    status_text = ft.Text("在宅中", size=28, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK87)

    status_display = ft.Container(
        content=ft.Column(
            controls=[status_icon, status_text],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
        ),
        margin=ft.margin.only(bottom=30),
    )

    def on_click(e):
        val = e.control.data
        status_text.value = val
        try:
            ref.set({
                'status': val,
                'updated_at': datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
            })
        except Exception as err:
            print(f"❌ 書き込みエラー: {err}")

        if val == "在宅中":
            status_icon.icon = ft.Icons.HOME_ROUNDED
            status_icon.color = ft.Colors.BLUE_400
        elif val == "外出中":
            status_icon.icon = ft.Icons.DIRECTIONS_RUN_ROUNDED
            status_icon.color = ft.Colors.GREEN_400
        elif val == "取り込み中":
            status_icon.icon = ft.Icons.DO_NOT_DISTURB_ON_TOTAL_SILENCE_ROUNDED
            status_icon.color = ft.Colors.RED_400

        page.update()

    def on_status_change(event):
        print(f"信号受信: {event.data}")
        if isinstance(event.data, dict):
            new_status = event.data.get('status', "在宅中")
        else:
            new_status = event.data

        if new_status is None or not isinstance(new_status, str):
            return

        status_text.value = new_status

        if new_status == "在宅中":
            status_icon.icon = ft.Icons.HOME_ROUNDED
            status_icon.color = ft.Colors.BLUE_400
        elif new_status == "外出中":
            status_icon.icon = ft.Icons.DIRECTIONS_RUN_ROUNDED
            status_icon.color = ft.Colors.GREEN_400
        elif new_status == "取り込み中":
            status_icon.icon = ft.Icons.DO_NOT_DISTURB_ON_TOTAL_SILENCE_ROUNDED
            status_icon.color = ft.Colors.RED_400

        page.update()

    ref.listen(on_status_change)

    def create_status_button(label, icon_name):
        return ft.OutlinedButton(
            content=ft.Row(
                [ft.Icon(icon_name), ft.Text(label)],
                alignment=ft.MainAxisAlignment.CENTER,
                tight=True,
            ),
            data=label,
            on_click=on_click,
            width=250,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=10),
                padding=ft.padding.all(20),
            ),
        )

    main_card = ft.Container(
        content=ft.Column(
            controls=[
                status_display,
                ft.Column(
                    controls=[
                        create_status_button("在宅中", ft.Icons.HOME_ROUNDED),
                        create_status_button("外出中", ft.Icons.DIRECTIONS_RUN_ROUNDED),
                        create_status_button("取り込み中", ft.Icons.DO_NOT_DISTURB_ON_TOTAL_SILENCE_ROUNDED),
                    ],
                    spacing=15,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        bgcolor=ft.Colors.WHITE,
        padding=40,
        border_radius=20,
        width=350,
    )

    page.add(main_card)

port = int(os.environ.get("PORT", 8550))
ft.app(target=main, view=ft.AppView.WEB_BROWSER, port=port, host="0.0.0.0")
