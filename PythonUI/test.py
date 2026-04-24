import flet as ft

def main(page: ft.Page):
    page.add(
        ft.SafeArea(
                content=ft.Container(
                    width = 480,
                    padding = 10,
                    border = ft.Border.all(2, ft.Colors.BLUE_GREY_200),
                    # border=ft.Border.all(2, ft.Colors.BLUE_GREY_200),
                    border_radius = 10, 
                    content = ft.Row(
                    controls=[
                        ft.TextField(hint_text = "Enter control Code", expand=True),
                        ft.Button("Confirm"),
                                ]
                        ),
                ),
        )          
    )
    def on_keyboard(e: ft.KeyboardEvent):
        page.add(
            ft.Text(
                f"Key: {e.key}, Shift: {e.shift}, Control: {e.ctrl}, Alt: {e.alt}, Meta: {e.meta}"
            )
        )

    page.on_keyboard_event = on_keyboard
    page.add(
        ft.Text("Press any key with a combination of CTRL, ALT, SHIFT and META keys...")
    )  



if __name__ == "__main__":
    ft.run(main)