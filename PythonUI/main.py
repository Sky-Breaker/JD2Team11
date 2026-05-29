import flet as ft
import flet.canvas as cv
import math
import asyncio

#CANVAS CONSTANTS
CANVAS_W = 560
CANVAS_H = 340

#Where are should be at the beginning, left edge of canvas
ARM_ORIGIN_X = 80
ARM_ORIGIN_Y = CANVAS_H - 60

#Segments for the arms and their lengths (SUBJECT TO CHANGE)
ARM_SEG1 = 130
ARM_SEG2 = 100

#General specs
LINE_SPACING = 28
SCALE        = 10
ANIM_STEPS   = 40
STEP_MS      = 30

#Hex color determinations

BG         = "#0d0f14"
PANEL      = "#13161e"
BORDER     = "#1e2330"
ACCENT     = "#9f00d4"
TEXT_PRI   = "#e8eaf0"
TEXT_SEC   = "#6b7280"
ARM_COLOR  = "#d5d5d5"
ARM_JOINT  = "#d40000"
ARM_TIP    = "#53ff35"
LINE_DRAWN = "#bf00ff"
LINE_GHOST = "#3f0253"
ERR_COLOR  = "#710101"

#MATH FOR ARM CALCULATIONS

#Function: ik
#Description: Calculates shoulder and elbow joint angles
#Inputs: target x and y, both arm segments
#Outputs: angle both need to move
#Effects: Output new variables
def ik(tx, ty, l1=ARM_SEG1, l2=ARM_SEG2):
    #When y goes up, x goes down, so that needs to be tended to 
    dx, dy = tx - ARM_ORIGIN_X, ARM_ORIGIN_Y - ty 
    #Distance formula for each dist called elsewhere
    dist2  = dx*dx + dy*dy
    #Calculating the angle using law of cosines
    cos2   = max(-1.0, min(1.0, (dist2 - l1*l1 - l2*l2) / (2*l1*l2)))
    #Elbow joint calculation
    t2     = math.acos(cos2)
    #Shoulder joint angle
    t1     = math.atan2(dy, dx) - math.atan2(l2*math.sin(t2), l1 + l2*math.cos(t2))
    return t1, t2
#Function: fk
#Description: Takes joint angles and calculates where the two joints end up
#Inputs: angles of elbow and shoulder and both arm segments
#Outputs: both end coordinates for tip and elbow
#Effects:Creates new variables
def fk(t1, t2, l1=ARM_SEG1, l2=ARM_SEG2):
    #Horizontal travel distance added to the arm length
    ex = ARM_ORIGIN_X + l1 * math.cos(t1)
    #elbow y position
    ey = ARM_ORIGIN_Y - l1 * math.sin(t1)
    #Tip x position
    tx = ex + l2 * math.cos(t1 + t2)
    #Tip y position
    ty = ey - l2 * math.sin(t1 + t2)
    return ex, ey, tx, ty
#Function: line_endpoints
#Description: Calculates where coordinates for elbow and tip will be on canvas
#Inputs: index and length given in inches
#Outputs:Calculated positions
#Effects: none
def line_endpoints(index, length_in):
    #convert into pixels
    length_px = length_in * SCALE
    #horizontal position
    x0 = ARM_ORIGIN_X + 30 + index * LINE_SPACING
    #Vertical start pos
    y0 = ARM_ORIGIN_Y - 80
    return (x0, y0), (x0, y0 - length_px)

#CREATE SHAPES FOR CANVAS

def arm_shapes(t1, t2):
    ex, ey, tx, ty = fk(t1, t2)
    return [
        cv.Line(ARM_ORIGIN_X, ARM_ORIGIN_Y, ex, ey,
                paint=ft.Paint(color=ARM_COLOR, stroke_width=10,
                               stroke_cap=ft.StrokeCap.ROUND)),
        cv.Line(ex, ey, tx, ty,
                paint=ft.Paint(color=ARM_COLOR, stroke_width=8,
                               stroke_cap=ft.StrokeCap.ROUND)),
        cv.Circle(ARM_ORIGIN_X, ARM_ORIGIN_Y, 9,  paint=ft.Paint(color=ARM_JOINT)),
        cv.Circle(ex, ey, 8,                       paint=ft.Paint(color=ARM_JOINT)),
        cv.Circle(tx, ty, 5,                       paint=ft.Paint(color=ARM_TIP)),
    ]

def ghost_shapes(lines_in):
    out = []
    #Loop over each line's length
    for i, lin in enumerate(lines_in):
        #Get canvas coordinates
        (x0, y0), (x1, y1) = line_endpoints(i, lin)
        #Add coordinates and create dotted line
        out.append(cv.Line(x0, y0, x1, y1,
                           paint=ft.Paint(color=LINE_GHOST, stroke_width=3,
                                          stroke_dash_pattern=[6, 4])))
    return out

def drawn_shapes(done):
    return [cv.Line(x0, y0, x1, y1,
                    paint=ft.Paint(color=LINE_DRAWN, stroke_width=3,
                                   stroke_cap=ft.StrokeCap.ROUND))
            for x0, y0, x1, y1 in done]

# ─── TextField factory ────────────────────────────────────────────────────────
# font_family and text_size were removed from TextField in 0.80+.
# All text styling goes through text_style / label_style.

def make_textfield(label, value, on_change=None, keyboard_type=None):
    return ft.TextField(
        label=label,
        value=value,
        width=200,
        height=52,
        label_style=ft.TextStyle(color=TEXT_SEC, size=11),
        text_style=ft.TextStyle(color=TEXT_PRI, size=13),
        bgcolor=BG,
        border_color=BORDER,
        focused_border_color=ACCENT,
        cursor_color=ACCENT,
        border_radius=6,
        content_padding=ft.Padding.symmetric(horizontal=12, vertical=8),
        on_change=on_change,
        keyboard_type=keyboard_type,
    )

#MAIN

def main(page: ft.Page):
    page.title   = "Robot Arm Controller"
    page.bgcolor = BG
    page.window.width     = 980
    page.window.height    = 760
    #Don't want it to break on resizing
    page.window.resizable = False
    page.padding = 0
    page.fonts = {
        "Mono": "https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&display=swap",
        "Sans": "https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&display=swap",
    }
    page.theme = ft.Theme(font_family="Sans")

    #MUTABLE THINGS
    line_fields: list[ft.TextField] = []
    anim_running = False

   #WIDGETS
    canvas = cv.Canvas(shapes=[], width=CANVAS_W, height=CANVAS_H,
                       content=ft.GestureDetector(mouse_cursor=ft.MouseCursor.BASIC))

    status = ft.Text("Configure lines and press Run →",
                     style=ft.TextStyle(color=TEXT_SEC, size=11))

    lines_col = ft.Column(spacing=8, scroll=ft.ScrollMode.AUTO)

    #CANVAS REFRESHING

    def refresh(lines_in, t1, t2, done=None, partial=None):
        shapes = ghost_shapes(lines_in) + drawn_shapes(done or [])
        if partial:
            shapes.append(partial)
        shapes += arm_shapes(t1, t2)
        canvas.shapes = shapes
        canvas.update()

   #ANIMS

    async def sweep(lines_in, done, t1a, t2a, tx, ty, steps=20):
        t1b, t2b = ik(tx, ty)
        for s in range(steps + 1):
            f = s / steps
            refresh(lines_in, t1a + (t1b - t1a)*f, t2a + (t2b - t2a)*f, done)
            await asyncio.sleep(STEP_MS / 1000)
        return t1b, t2b

    async def run_animation(lines_in):
        nonlocal anim_running
        anim_running = True
        status.value = "Running…"
        status.style = ft.TextStyle(color=ACCENT, size=11)
        status.update()

        done = []
        t1, t2 = ik(ARM_ORIGIN_X + 30, ARM_ORIGIN_Y - 80)

        for i, lin in enumerate(lines_in):
            (x0, y0), (x1, y1) = line_endpoints(i, lin)
            t1, t2 = await sweep(lines_in, done, t1, t2, x0, y0)

            for s in range(ANIM_STEPS + 1):
                frac = s / ANIM_STEPS
                px, py = x0 + (x1-x0)*frac, y0 + (y1-y0)*frac
                t1, t2 = ik(px, py)
                partial = cv.Line(x0, y0, px, py,
                                  paint=ft.Paint(color=ACCENT, stroke_width=3,
                                                 stroke_cap=ft.StrokeCap.ROUND))
                refresh(lines_in, t1, t2, done, partial)
                await asyncio.sleep(STEP_MS / 1000)

            done.append((x0, y0, x1, y1))
            t1, t2 = ik(x1, y1)

        tr1, tr2 = ik(ARM_ORIGIN_X + 30, ARM_ORIGIN_Y - 100)
        refresh(lines_in, tr1, tr2, done)
        anim_running = False
        status.value = f"Done — {len(lines_in)} line(s) drawn"
        status.style = ft.TextStyle(color=ACCENT, size=11)
        status.update()

   #INPUT HELP

    def parse_lines():
        vals = []
        ok = True
        for tf in line_fields:
            try:
                v = float(tf.value)
                if v <= 0:
                    raise ValueError
                vals.append(v)
                tf.border_color = BORDER
            except ValueError:
                tf.border_color = ERR_COLOR
                ok = False
            tf.update()
        return vals if ok else None

    def build_fields(n):
        line_fields.clear()
        for i in range(n):
            line_fields.append(make_textfield(f"Line {i+1} length (in)", "5"))
        lines_col.controls = list(line_fields)

    #NUM OF LINES

    def on_num_change(e):
        try:
            n = int(num_field.value)
            if not 1 <= n <= 5:
                raise ValueError
        except (ValueError, AttributeError):
            return
        build_fields(n)
        t1h, t2h = ik(ARM_ORIGIN_X + 30, ARM_ORIGIN_Y - 80)
        refresh([5.0] * n, t1h, t2h)
        page.update()

    num_field = make_textfield("Number of lines (1–5)", "3",
                               on_change=on_num_change,
                               keyboard_type=ft.KeyboardType.NUMBER)

    #CALL BACKS 

    def on_preview(e):
        lines_in = parse_lines()
        if lines_in is None:
            status.value = "Fix invalid lengths above"
            status.style = ft.TextStyle(color=ERR_COLOR, size=11)
            status.update()
            return
        t1h, t2h = ik(ARM_ORIGIN_X + 30, ARM_ORIGIN_Y - 80)
        refresh(lines_in, t1h, t2h)
        status.value = f"Preview: {len(lines_in)} parallel line(s)"
        status.style = ft.TextStyle(color=TEXT_SEC, size=11)
        status.update()

    def on_run(e):
        if anim_running:
            return
        lines_in = parse_lines()
        if lines_in is None:
            status.value = " Fix invalid lengths above"
            status.style = ft.TextStyle(color=ERR_COLOR, size=11)
            status.update()
            return
        page.run_task(run_animation, lines_in)

    def on_reset(e):
        try:
            n = int(num_field.value)
        except ValueError:
            n = 3
        build_fields(n)
        t1h, t2h = ik(ARM_ORIGIN_X + 30, ARM_ORIGIN_Y - 80)
        refresh([5.0] * n, t1h, t2h)
        status.value = "Reset — configure and press Run →"
        status.style = ft.TextStyle(color=TEXT_SEC, size=11)
        status.update()
        page.update()

    #BUTTONS

    preview_btn = ft.OutlinedButton(
        "Preview", icon=ft.Icons.VISIBILITY_OUTLINED, on_click=on_preview,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=6),
            side=ft.BorderSide(1, ACCENT),
            color=ACCENT,
            padding=ft.Padding.symmetric(horizontal=20, vertical=12),
        ), width=140,
    )

    run_btn = ft.Button(
        "Run", icon=ft.Icons.PLAY_ARROW_ROUNDED, on_click=on_run,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=6),
            bgcolor=ACCENT,
            color="#000000",
            padding=ft.Padding.symmetric(horizontal=20, vertical=12),
        ), width=130,
    )

    reset_btn = ft.TextButton(
        "Reset", icon=ft.Icons.REFRESH_ROUNDED, on_click=on_reset,
        style=ft.ButtonStyle(
            color=TEXT_SEC,
            padding=ft.Padding.symmetric(horizontal=16, vertical=12),
        ),
    )

    #LEFT SIDE

    left_panel = ft.Container(
        width=270,
        bgcolor=PANEL,
        border=ft.Border.only(right=ft.BorderSide(1, BORDER)),
        padding=ft.Padding.all(24),
        content=ft.Column(spacing=0, controls=[
            ft.Text("ROBOT ARM", style=ft.TextStyle(color=ACCENT, size=10),
                    font_family="Mono"),
            ft.Text("Line Controller", style=ft.TextStyle(color=TEXT_PRI, size=20,
                    weight=ft.FontWeight.W_600)),
            ft.Container(height=4),
            ft.Divider(height=1, color=BORDER),
            ft.Container(height=20),

            ft.Text("CONFIGURATION", font_family="Mono",
                    style=ft.TextStyle(color=TEXT_SEC, size=9)),
            ft.Container(height=12),
            num_field,
            ft.Container(height=20),

            ft.Text("LINE LENGTHS", font_family="Mono",
                    style=ft.TextStyle(color=TEXT_SEC, size=9)),
            ft.Container(height=12),
            ft.Container(height=300,
                         content=ft.Column(controls=[lines_col],
                                           scroll=ft.ScrollMode.AUTO, spacing=8)),
            ft.Container(height=20),
            ft.Divider(height=1, color=BORDER),
            ft.Container(height=16),

            ft.Row([preview_btn, reset_btn], spacing=8),
            ft.Container(height=10),
            run_btn,
            ft.Container(height=16),
            status,
        ]),
    )

    #;EGEND

    def legend_item(color, label, dashed=False):
        swatch = ft.Container(width=20, height=3, bgcolor=color if not dashed else None,
                              border=ft.Border.all(1, color) if dashed else None)
        return ft.Row([swatch,
                       ft.Text(label, style=ft.TextStyle(color=TEXT_SEC, size=10))],
                      spacing=6)

    legend = ft.Row(spacing=20, controls=[
        legend_item(ACCENT,     "Drawn"),
        legend_item(LINE_GHOST, "Target", dashed=True),
        ft.Row([ft.Container(width=10, height=10, bgcolor=ARM_TIP, border_radius=5),
                ft.Text("Tool tip", style=ft.TextStyle(color=TEXT_SEC, size=10))],
               spacing=6),
        ft.Row([ft.Container(width=10, height=10, bgcolor=ARM_JOINT, border_radius=5),
                ft.Text("Pivot Point", style=ft.TextStyle(color=TEXT_SEC, size=10))],
               spacing=6),
    ])

    #SPECS BOX|DEBUGGING|

    def spec_row(label, value):
        ts_sec = ft.TextStyle(color=TEXT_SEC, size=11)
        ts_pri = ft.TextStyle(color=TEXT_PRI, size=11)
        return ft.Row([ft.Text(label, style=ts_sec), ft.Text(value, style=ts_pri)],
                      alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

    specs = ft.Container(
        padding=ft.Padding.all(12), bgcolor=PANEL,
        border_radius=6, border=ft.Border.all(1, BORDER),
        content=ft.Column(spacing=4, controls=[
            ft.Text("ARM SPECS", font_family="Mono",
                    style=ft.TextStyle(color=TEXT_SEC, size=9)),
            ft.Container(height=4),
            spec_row("Segment 1",   f"{ARM_SEG1} units"),
            spec_row("Segment 2",   f"{ARM_SEG2} units"),
            spec_row("Scale",       f"{SCALE} px/in"),
            spec_row("Line spacing",f"{LINE_SPACING} px"),
        ]),
    )

    #RIGHT SIDE

    right_panel = ft.Container(
        expand=True, bgcolor=BG, padding=ft.Padding.all(28),
        content=ft.Column(spacing=16, controls=[
            ft.Text("WORKSPACE PREVIEW", font_family="Mono",
                    style=ft.TextStyle(color=TEXT_SEC, size=9)),
            ft.Container(content=canvas, border=ft.Border.all(1, BORDER),
                         border_radius=8, bgcolor=PANEL,
                         clip_behavior=ft.ClipBehavior.HARD_EDGE),
            legend,
            specs,
        ]),
    )

    #LAYOUT 

    page.add(ft.Row(expand=True, spacing=0, controls=[left_panel, right_panel]))
    on_num_change(None)
    on_preview(None)


ft.run(main)
