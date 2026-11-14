
import ast
import math
import operator

from kivy.app import App
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.utils import get_color_from_hex


# -----------------------------
# ONYX CALCULATOR
# -----------------------------

BG = "#101116"
PANEL = "#1B1D25"
NUMBER = "#292C35"
ORANGE = "#FF9F32"
WHITE = "#FFFFFF"
GREY = "#9297A5"

Window.clearcolor = get_color_from_hex(BG)


def evaluate(expression):

    operations = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
    }

    def solve(node):

        if isinstance(node, ast.Expression):
            return solve(node.body)

        if isinstance(node, ast.Constant):
            if type(node.value) not in (int, float):
                raise ValueError("Invalid")
            return node.value

        if isinstance(node, ast.BinOp):

            operation = type(node.op)

            if operation not in operations:
                raise ValueError("Invalid")

            left = solve(node.left)
            right = solve(node.right)

            result = operations[operation](left, right)

            if not math.isfinite(result):
                raise ValueError("Invalid")

            return result

        if isinstance(node, ast.UnaryOp):

            value = solve(node.operand)

            if isinstance(node.op, ast.USub):
                return -value

            if isinstance(node.op, ast.UAdd):
                return value

            raise ValueError("Invalid")

        raise ValueError("Invalid")

    return solve(ast.parse(expression, mode="eval"))


# -----------------------------
# CUSTOM ROUNDED BUTTON
# -----------------------------

class CalcButton(Button):

    def __init__(self, bg_color, **kwargs):

        super().__init__(**kwargs)

        self.bg_color = get_color_from_hex(bg_color)

        self.background_normal = ""
        self.background_down = ""
        self.background_color = (0, 0, 0, 0)

        self.color = get_color_from_hex(WHITE)
        self.bold = True
        self.font_size = "22sp"

        with self.canvas.before:
            self.canvas_color = Color(*self.bg_color)
            self.rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(20)]
            )

        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, *args):

        self.rect.pos = self.pos
        self.rect.size = self.size


# -----------------------------
# MAIN APP
# -----------------------------

class OnyxCalculator(App):

    def build(self):

        self.title = "ONYX CALCULATOR"
        self.expression = ""
        self.just_calculated = False

        root = BoxLayout(
            orientation="vertical",
            padding=dp(18),
            spacing=dp(14)
        )

        # Background
        with root.canvas.before:
            Color(*get_color_from_hex(BG))
            self.bg_rect = RoundedRectangle(
                pos=root.pos,
                size=root.size
            )

        root.bind(
            pos=self.update_bg,
            size=self.update_bg
        )

        # Header
        header = Label(
            text="[b]ONYX[/b]  [color=ff9f32]CALCULATOR[/color]",
            markup=True,
            font_size="20sp",
            halign="left",
            size_hint_y=0.09
        )

        root.add_widget(header)

        # Display
        display = BoxLayout(
            orientation="vertical",
            padding=[dp(15), dp(15)],
            spacing=dp(8),
            size_hint_y=0.25
        )

        with display.canvas.before:
            Color(*get_color_from_hex(PANEL))
            self.display_rect = RoundedRectangle(
                pos=display.pos,
                size=display.size,
                radius=[dp(22)]
            )

        display.bind(
            pos=lambda obj, value: setattr(
                self.display_rect, "pos", value
            ),
            size=lambda obj, value: setattr(
                self.display_rect, "size", value
            )
        )

        self.expression_label = Label(
            text="",
            color=get_color_from_hex(GREY),
            font_size="20sp",
            halign="right",
            valign="center",
            size_hint_y=0.4
        )

        self.expression_label.bind(
            size=lambda obj, value:
            setattr(obj, "text_size", value)
        )

        self.result_label = Label(
            text="0",
            color=get_color_from_hex(WHITE),
            font_size="44sp",
            halign="right",
            valign="center",
            size_hint_y=0.6
        )

        self.result_label.bind(
            size=lambda obj, value:
            setattr(obj, "text_size", value)
        )

        display.add_widget(self.expression_label)
        display.add_widget(self.result_label)

        root.add_widget(display)

        # Buttons
        grid = GridLayout(
            cols=4,
            spacing=dp(10),
            size_hint_y=0.66
        )

        buttons = [
            ["AC", "DEL", "%", "÷"],
            ["7", "8", "9", "×"],
            ["4", "5", "6", "-"],
            ["1", "2", "3", "+"],
            ["±", "0", ".", "="]
        ]

        for row in buttons:

            for symbol in row:

                if symbol in ["÷", "×", "-", "+", "="]:
                    bg = ORANGE

                elif symbol in ["AC", "DEL", "%", "±"]:
                    bg = PANEL

                else:
                    bg = NUMBER

                btn = CalcButton(
                    bg_color=bg,
                    text=symbol
                )

                if bg == PANEL:
                    btn.color = get_color_from_hex(ORANGE)

                btn.bind(
                    on_release=lambda instance, s=symbol:
                    self.press(s)
                )

                grid.add_widget(btn)

        root.add_widget(grid)

        return root

    def update_bg(self, instance, value):

        self.bg_rect.pos = instance.pos
        self.bg_rect.size = instance.size

    # -----------------------------
    # CALCULATOR FUNCTIONS
    # -----------------------------

    def format_result(self, value):

        if isinstance(value, float) and value.is_integer():
            return str(int(value))

        return f"{value:.10g}"

    def preview(self):

        if not self.expression:
            return "0"

        try:

            exp = self.expression.replace("×", "*")
            exp = exp.replace("÷", "/")

            result = evaluate(exp)

            return self.format_result(result)

        except Exception:
            return ""

    def refresh(self):

        self.expression_label.text = self.expression
        self.result_label.text = self.preview()

    def press(self, key):

        if key == "AC":

            self.expression = ""
            self.just_calculated = False

        elif key == "DEL":

            self.expression = self.expression[:-1]
            self.just_calculated = False

        elif key == "=":

            if not self.expression:
                return

            try:

                exp = self.expression.replace("×", "*")
                exp = exp.replace("÷", "/")

                result = evaluate(exp)

                self.expression = self.format_result(result)
                self.expression_label.text = "="
                self.result_label.text = self.expression

                self.just_calculated = True
                return

            except Exception:

                self.expression_label.text = self.expression
                self.result_label.text = "Error"
                self.expression = ""
                self.just_calculated = False
                return

        elif key == "±":

            if self.expression:

                if self.expression.startswith("-(") and self.expression.endswith(")"):
                    self.expression = self.expression[2:-1]
                else:
                    self.expression = "-(" + self.expression + ")"

            self.just_calculated = False

        elif key == "%":

            if self.expression:
                self.expression += "/100"

            self.just_calculated = False

        else:

            if self.just_calculated and key not in ["+", "-", "×", "÷"]:
                self.expression = ""

            self.expression += key
            self.just_calculated = False

        self.refresh()


# -----------------------------
# START APPLICATION
# -----------------------------

if __name__ == "__main__":
    OnyxCalculator().run()
