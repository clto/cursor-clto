import colorama
from colorama import Fore, Style, init
from dotenv import load_dotenv
import os
import re
import shutil

# Get current directory and load .env file
current_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(current_dir, '.env')
load_dotenv(env_path)

# Get version from environment or default to 1.0.0
version = os.getenv('VERSION', '1.0.0')

# Initialize colorama
init()

def get_terminal_width():
    try:
        columns, _ = shutil.get_terminal_size()
        return columns
    except Exception:
        return 80

def center_multiline_text(text, handle_chinese=False):
    width = get_terminal_width()
    lines = text.split('\n')
    centered_lines = []

    for line in lines:
        clean_line = line

        # Remove color codes
        colors = (Fore.CYAN, Fore.YELLOW, Fore.GREEN, Fore.RED, Fore.BLUE, Style.RESET_ALL)
        for color in colors:
            clean_line = clean_line.replace(color, '')

        # Remove ANSI escape codes
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        clean_line = ansi_escape.sub('', clean_line)

        # Calculate display width
        if handle_chinese:
            display_width = 0
            for char in clean_line:
                if ord(char) > 127:
                    display_width += 2
                else:
                    display_width += 1
        else:
            display_width = len(clean_line)

        padding = max(0, (width - display_width) // 2)
        centered_lines.append(' ' * padding + line)

    return '\n'.join(centered_lines)

# Build logo text with colors
LOGO_TEXT = Fore.CYAN + '\n   ██████╗██╗   ██╗██████╗ ███████╗ ██████╗ ██████╗      ██████╗ ██████╗  ██████╗   \n  ██╔════╝██║   ██║██╔══██╗██╔════╝██╔═══██╗██╔══██╗     ██╔══██╗██╔══██╗██╔═══██╗  \n  ██║     ██║   ██║██████╔╝███████╗██║   ██║██████╔╝     ██████╔╝██████╔╝██║   ██║  \n  ██║     ██║   ██║██╔══██╗╚════██║██║   ██║██╔══██╗     ██╔═══╝ ██╔══██╗██║   ██║  \n  ╚██████╗╚██████╔╝██║  ██║███████║╚██████╔╝██║  ██║     ██║     ██║  ██║╚██████╔╝  \n   ╚═════╝ ╚═════╝ ╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═╝  ╚═╝     ╚═╝     ╚═╝  ╚═╝ ╚═════╝  \n' + Style.RESET_ALL

DESCRIPTION_TEXT = Fore.YELLOW + '\nCursor CLTO v' + version + Fore.GREEN + '\nAuthor: clto' + Style.RESET_ALL

CONTRIBUTORS_TEXT = Fore.BLUE + '\nPowered by CLTO Studio\n' + Style.RESET_ALL

OTHER_INFO_TEXT = Fore.YELLOW + '\nGithub: https://github.com/clto/cursor-clto' + Fore.RED + '\nPress 8 to change language | 按下 8 键切换语言' + Style.RESET_ALL

CURSOR_LOGO = center_multiline_text(LOGO_TEXT, handle_chinese=False)
CURSOR_DESCRIPTION = center_multiline_text(DESCRIPTION_TEXT, handle_chinese=False)
CURSOR_CONTRIBUTORS = center_multiline_text(CONTRIBUTORS_TEXT, handle_chinese=False)
CURSOR_OTHER_INFO = center_multiline_text(OTHER_INFO_TEXT, handle_chinese=True)

def print_logo():
    print(CURSOR_LOGO)
    print(CURSOR_DESCRIPTION)
    print(CURSOR_OTHER_INFO)

if __name__ == '__main__':
    print_logo()
