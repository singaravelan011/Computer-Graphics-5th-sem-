

import turtle
import math
import time


# =====================================================================
# ALGORITHM 1: DDA (Digital Differential Analyzer)
# =====================================================================
def dda_line(x1, y1, x2, y2):
    dx, dy = x2 - x1, y2 - y1
    steps = int(max(abs(dx), abs(dy)))
    if steps == 0:
        return [(x1, y1)]
    x_inc, y_inc = dx / steps, dy / steps
    points, x, y = [], x1, y1
    for _ in range(steps + 1):
        points.append((round(x), round(y)))
        x += x_inc
        y += y_inc
    return points


# =====================================================================
# ALGORITHM 2: Bresenham's Line Algorithm
# =====================================================================
def bresenham_line(x1, y1, x2, y2):
    x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
    points = []
    dx, dy = abs(x2 - x1), abs(y2 - y1)
    sx = 1 if x1 < x2 else -1
    sy = 1 if y1 < y2 else -1
    if dx > dy:
        p, x, y = 2 * dy - dx, x1, y1
        for _ in range(dx + 1):
            points.append((x, y))
            if p >= 0:
                y += sy
                p -= 2 * dx
            x += sx
            p += 2 * dy
    else:
        p, x, y = 2 * dx - dy, x1, y1
        for _ in range(dy + 1):
            points.append((x, y))
            if p >= 0:
                x += sx
                p -= 2 * dy
            y += sy
            p += 2 * dx
    return points


# =====================================================================
# ALGORITHM 3: Midpoint Circle Algorithm
# =====================================================================
def midpoint_circle(xc, yc, r):
    points = []

    def plot(x, y):
        points.extend([
            (xc + x, yc + y), (xc - x, yc + y), (xc + x, yc - y), (xc - x, yc - y),
            (xc + y, yc + x), (xc - y, yc + x), (xc + y, yc - x), (xc - y, yc - x),
        ])

    r = max(1, int(r))
    x, y, p = 0, r, 1 - r
    plot(x, y)
    while x < y:
        x += 1
        if p < 0:
            p += 2 * x + 1
        else:
            y -= 1
            p += 2 * x - 2 * y + 1
        plot(x, y)
    return points


# =====================================================================
# ALGORITHM 4: Midpoint Ellipse Algorithm
# =====================================================================
def midpoint_ellipse(xc, yc, rx, ry):
    points = []

    def plot(x, y):
        points.extend([(xc + x, yc + y), (xc - x, yc + y), (xc + x, yc - y), (xc - x, yc - y)])

    rx, ry = max(1, int(rx)), max(1, int(ry))
    x, y = 0, ry
    rx2, ry2 = rx * rx, ry * ry
    two_rx2, two_ry2 = 2 * rx2, 2 * ry2

    p1 = ry2 - rx2 * ry + 0.25 * rx2
    dx, dy = two_ry2 * x, two_rx2 * y
    plot(x, y)
    while dx < dy:
        x += 1
        dx += two_ry2
        if p1 < 0:
            p1 += dx + ry2
        else:
            y -= 1
            dy -= two_rx2
            p1 += dx - dy + ry2
        plot(x, y)

    p2 = ry2 * (x + 0.5) ** 2 + rx2 * (y - 1) ** 2 - rx2 * ry2
    while y > 0:
        y -= 1
        dy -= two_rx2
        if p2 > 0:
            p2 += rx2 - dy
        else:
            x += 1
            dx += two_ry2
            p2 += dx - dy + rx2
        plot(x, y)
    return points


# =====================================================================
# ALGORITHM 5: Cohen-Sutherland Line Clipping
# =====================================================================
_LEFT, _RIGHT, _BOTTOM, _TOP = 1, 2, 4, 8


def _outcode(x, y, xmin, ymin, xmax, ymax):
    code = 0
    if x < xmin:
        code |= _LEFT
    elif x > xmax:
        code |= _RIGHT
    if y < ymin:
        code |= _BOTTOM
    elif y > ymax:
        code |= _TOP
    return code


def cohen_sutherland_clip(x1, y1, x2, y2, xmin, ymin, xmax, ymax):
    code1 = _outcode(x1, y1, xmin, ymin, xmax, ymax)
    code2 = _outcode(x2, y2, xmin, ymin, xmax, ymax)
    for _ in range(10):  # hard iteration cap: never loop forever on bad input
        if code1 == 0 and code2 == 0:
            return (x1, y1, x2, y2)
        if code1 & code2 != 0:
            return None
        code_out = code1 if code1 != 0 else code2
        if code_out & _TOP and y2 != y1:
            x = x1 + (x2 - x1) * (ymax - y1) / (y2 - y1)
            y = ymax
        elif code_out & _BOTTOM and y2 != y1:
            x = x1 + (x2 - x1) * (ymin - y1) / (y2 - y1)
            y = ymin
        elif code_out & _RIGHT and x2 != x1:
            y = y1 + (y2 - y1) * (xmax - x1) / (x2 - x1)
            x = xmax
        elif code_out & _LEFT and x2 != x1:
            y = y1 + (y2 - y1) * (xmin - x1) / (x2 - x1)
            x = xmin
        else:
            return None  # degenerate segment (zero-length or axis-aligned edge case)
        if code_out == code1:
            x1, y1 = x, y
            code1 = _outcode(x1, y1, xmin, ymin, xmax, ymax)
        else:
            x2, y2 = x, y
            code2 = _outcode(x2, y2, xmin, ymin, xmax, ymax)
    return None


# =====================================================================
# ALGORITHM 6: Scan-line Polygon Fill
# =====================================================================
def scanline_fill_spans(vertices):
    if not vertices:
        return []
    ys = [v[1] for v in vertices]
    ymin, ymax = int(min(ys)), int(max(ys))
    n = len(vertices)
    spans = []
    for y in range(ymin, ymax + 1):
        x_ints = []
        for i in range(n):
            x1, y1 = vertices[i]
            x2, y2 = vertices[(i + 1) % n]
            if y1 == y2:
                continue
            if min(y1, y2) <= y < max(y1, y2):
                x = x1 + (y - y1) * (x2 - x1) / (y2 - y1)
                x_ints.append(x)
        x_ints.sort()
        for i in range(0, len(x_ints) - 1, 2):
            spans.append((y, round(x_ints[i]), round(x_ints[i + 1])))
    return spans


def star_polygon(cx, cy, outer_r, inner_r, points):
    verts = []
    for i in range(points * 2):
        angle = math.pi * i / points
        r = outer_r if i % 2 == 0 else inner_r
        verts.append((cx + r * math.sin(angle), cy + r * math.cos(angle)))
    return verts


def lerp_color(c1, c2, t):
    t = max(0.0, min(1.0, t))
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))



def run_game():
    APERTURE = dict(xmin=-180, xmax=180, ymin=-120, ymax=120)

   
    CONSTELLATIONS = [
        {"name": "The Serpent", "stars": [(-320, 180), (-140, 70), (70, -40), (260, -170)],
         "glyph": (6, (70, 60, 130), (210, 210, 235))},

        {"name": "The Loom", "stars": [(-300, -60), (-100, -180), (120, -140), (310, -20)],
         "glyph": (4, (40, 90, 110), (200, 230, 235))},

        {"name": "The Anchor", "stars": [(-260, 250), (-30, 140), (160, 230), (330, 90)],
         "glyph": (3, (90, 50, 100), (230, 200, 230))},

        {"name": "The Phoenix", "stars": [(-350, 40), (-190, -70), (-20, 20), (150, 100)],
         "glyph": (5, (130, 50, 60), (240, 180, 120))},

        {"name": "The Crown", "stars": [(-300, -230), (-160, -120), (0, -210), (180, -100)],
         "glyph": (5, (110, 70, 40), (245, 220, 150))},

        {"name": "The Arrow", "stars": [(-340, 250), (-170, 160), (20, 120), (300, 230)],
         "glyph": (4, (60, 100, 150), (180, 220, 250))},

        {"name": "The River", "stars": [(-330, -170), (-210, -40), (-40, -90), (130, -230)],
         "glyph": (5, (40, 100, 90), (170, 230, 200))},

        {"name": "The Dragon", "stars": [(250, 250), (120, 170), (210, 40), (340, -100)],
         "glyph": (7, (100, 50, 130), (220, 180, 240))},

        {"name": "The Compass", "stars": [(-80, 250), (60, 150), (240, 170), (320, 20)],
         "glyph": (4, (50, 80, 130), (190, 210, 245))},

        {"name": "The Celestial Key", "stars": [(-340, -250), (-180, -170), (-30, -250), (150, -190)],
         "glyph": (6, (120, 80, 50), (245, 210, 160))},
    ]

    if len(CONSTELLATIONS) < 10:
        raise ValueError("Celestial Loom requires at least 10 constellations.")

    turtle.colormode(255)
    screen = turtle.Screen()
    screen.title("Celestial Loom")
    screen.bgcolor((6, 6, 16))
    screen.setup(width=800, height=600)
    screen.tracer(0)

    pen = turtle.Turtle()
    pen.hideturtle()
    pen.penup()
    pen.speed(0)

    hud = turtle.Turtle()
    hud.hideturtle()
    hud.penup()
    hud.color((200, 200, 225))
    hud.goto(-380, 260)

    msg = turtle.Turtle()
    msg.hideturtle()
    msg.penup()

    # mutable game state, kept in a dict so nested functions can update
    # it via closures without needing module-level globals
    state = {"active_index": 0, "active_star": 1,
             "completed": [False] * len(CONSTELLATIONS)}

    def plot_points(points, color, size=2):
        pen.color(color)
        for (x, y) in points:
            pen.goto(x, y)
            pen.dot(size)

    def draw_aperture():
        pen.color((90, 90, 130))
        pen.goto(APERTURE["xmin"], APERTURE["ymin"])
        pen.pendown()
        for (x, y) in [(APERTURE["xmax"], APERTURE["ymin"]), (APERTURE["xmax"], APERTURE["ymax"]),
                       (APERTURE["xmin"], APERTURE["ymax"]), (APERTURE["xmin"], APERTURE["ymin"])]:
            pen.goto(x, y)
        pen.penup()

    def draw_stars():
        ai, as_ = state["active_index"], state["active_star"]
        for i, c in enumerate(CONSTELLATIONS):
            dim = (220, 220, 240) if i == ai else (70, 70, 90)
            for j, (sx, sy) in enumerate(c["stars"]):
                if i == ai and j == as_:
                    plot_points(midpoint_circle(sx, sy, 6), (255, 240, 180), 2)
                else:
                    plot_points(midpoint_circle(sx, sy, 3), dim, 1)

    def draw_halo():
        ai = state["active_index"]
        if ai >= len(CONSTELLATIONS) or state["completed"][ai]:
            return
        stars = CONSTELLATIONS[ai]["stars"]
        xs, ys = [s[0] for s in stars], [s[1] for s in stars]
        cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
        rx, ry = (max(xs) - min(xs)) / 2 + 30, (max(ys) - min(ys)) / 2 + 30
        plot_points(midpoint_ellipse(int(cx), int(cy), int(rx), int(ry)), (55, 55, 85), 1)

    def connect(p1, p2):
        dim_pts = dda_line(p1[0], p1[1], p2[0], p2[1])
        plot_points(dim_pts, (60, 60, 95), 1)
        clipped = cohen_sutherland_clip(p1[0], p1[1], p2[0], p2[1],
                                         APERTURE["xmin"], APERTURE["ymin"],
                                         APERTURE["xmax"], APERTURE["ymax"])
        if clipped:
            cx1, cy1, cx2, cy2 = clipped
            plot_points(bresenham_line(cx1, cy1, cx2, cy2), (225, 225, 250), 2)

    def draw_progress_lines():
        ai, as_ = state["active_index"], state["active_star"]
        for i, c in enumerate(CONSTELLATIONS):
            stars = c["stars"]
            if i == ai:
                limit = min(as_, len(stars))
            elif state["completed"][i]:
                limit = len(stars)
            else:
                limit = 0
            for j in range(1, limit):
                connect(stars[j - 1], stars[j])

    def glyph_bloom(constellation):
        stars = constellation["stars"]
        if not stars:
            return
        cx = sum(s[0] for s in stars) / len(stars)
        cy = sum(s[1] for s in stars) / len(stars)
        points, c1, c2 = constellation["glyph"]
        shape = star_polygon(cx, cy, 30, 12, points)
        spans = scanline_fill_spans(shape)
        if not spans:
            return
        ys = [s[0] for s in spans]
        ymin, ymax = min(ys), max(ys)
        for (y, xs, xe) in spans:
            t = (y - ymin) / max(1, (ymax - ymin))
            pen.color(lerp_color(c1, c2, t))
            pen.goto(xs, y)
            pen.pendown()
            pen.goto(xe, y)
            pen.penup()
        plot_points(midpoint_circle(int(cx), int(cy), 40), c2, 1)

    def redraw_scene():
        pen.clear()
        draw_aperture()
        draw_halo()
        draw_progress_lines()
        for i, c in enumerate(CONSTELLATIONS):
            if state["completed"][i]:
                glyph_bloom(c)
        draw_stars()
        screen.update()

    def update_hud():
        hud.clear()
        names = ", ".join(c["name"] for i, c in enumerate(CONSTELLATIONS) if state["completed"][i])
        hud.write(f"Constellations traced: {sum(state['completed'])}/{len(CONSTELLATIONS)}   {names}",
                   font=("Georgia", 13, "italic"))

    def flash_message(text, color, x=0, y=0, pause=0.35):
        msg.clear()
        msg.color(color)
        msg.goto(x, y)
        msg.write(text, align="center", font=("Georgia", 14, "italic"))
        screen.update()
        time.sleep(pause)
        msg.clear()
        screen.update()

    def handle_click(x, y):
        ai = state["active_index"]
        if ai >= len(CONSTELLATIONS):
            return  # game already complete — clicks are safely ignored

        stars = CONSTELLATIONS[ai]["stars"]
        as_ = state["active_star"]
        if as_ >= len(stars):
            # defensive: should not happen, but never let a bad index reach here
            state["active_star"] = 1
            return

        target = stars[as_]
        if math.hypot(x - target[0], y - target[1]) <= 18:
            prev = stars[as_ - 1]
            connect(prev, target)
            state["active_star"] += 1

            just_completed = None
            if state["active_star"] >= len(stars):
                state["completed"][ai] = True
                just_completed = CONSTELLATIONS[ai]
                state["active_index"] += 1
                state["active_star"] = 1

            redraw_scene()
            update_hud()
            screen.update()

            if just_completed:
                cx = sum(s[0] for s in just_completed["stars"]) / len(just_completed["stars"])
                cy = sum(s[1] for s in just_completed["stars"]) / len(just_completed["stars"])
                flash_message(f'"{just_completed["name"]}" is traced', (230, 230, 250), cx, cy + 50)

            if state["active_index"] >= len(CONSTELLATIONS):
                msg.color((235, 235, 255))
                msg.goto(0, 0)
                msg.write("THE SKY REMEMBERS ITS SHAPE", align="center", font=("Georgia", 24, "italic"))
                screen.update()
                screen.onscreenclick(None)
        else:
            flash_message("...not the pattern", (140, 140, 165), x, y + 20, 0.3)

    def on_click_safe(x, y):
       
        try:
            handle_click(x, y)
        except Exception as exc:  # noqa: BLE001 - intentional catch-all guard
            print(f"[celestial_loom] click handler error (ignored, game continues): {exc}")

    redraw_scene()
    update_hud()
    screen.update()
    screen.onscreenclick(on_click_safe)
    turtle.mainloop()


if __name__ == "__main__":
    run_game()
