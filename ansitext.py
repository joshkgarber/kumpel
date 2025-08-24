from enum import Enum


class Style(Enum):
    NONE = "0"
    BOLD = "1"
    ITALIC = "3"
    UNDERLINE = "4"


class Color(Enum):
    RED = "31"
    GREEN = "32"
    BLUE = "34"
    YELLOW = "33"
    MAGENTA = "35"
    CYAN = "36"


def stylize(style, color, content):
    style_code = style.value
    color_code = color.value
    return f"\033[{style_code};{color_code}m{content}\033[0m"
