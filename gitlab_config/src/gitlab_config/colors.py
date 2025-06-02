import logging

logger = logging.getLogger(__name__)

class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    WHITE = '\033[97m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    RESET = '\033[0m'


def color_cell(value: str, changed: bool, fix: bool) -> str:

    logger.debug(f"color_cell: {value}, {changed}, {fix}")

    style = Colors.WHITE
    if changed and fix:
        style = Colors.GREEN
    elif changed:
        style = Colors.YELLOW

    return colorize(value, style)


def colorize(string, color: str):
    return f"{color}{string}{Colors.RESET}"
