# Decompiled from: main.pyc
# Python 3.14 | PyInstaller package
# Note: Full source recovery limited; showing structure + strings

import os
import sys
import json
from logo import print_logo, version
from colorama import Fore, Style, init
import locale
import platform
import requests
import subprocess
from config import get_config, force_update_config
import shutil
import re

# Force UTF-8 encoding for Windows console
if platform.system() == 'Windows':
    import ctypes
    from ctypes import windll
    # Set console to UTF-8 mode
    os.system('chcp 65001 >nul 2>&1')
    # Set Python stdout encoding
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8')

init()

EMOJI = {
    'FILE': '📄',
    'BACKUP': '💾',
    'SUCCESS': '✅',
    'ERROR': '❌',
    'INFO': 'ℹ️',
    'RESET': '🔄',
    'MENU': '📋',
    'ARROW': '➜',
    'LANG': '🌐',
    'UPDATE': '🔄',
    'ADMIN': '🔐',
    'AIRDROP': '💰',
    'ROCKET': '🚀',
    'STAR': '⭐',
    'SUN': '🌟',
    'CONTRIBUTE': '🤝',
    'SETTINGS': '⚙️'
}

def is_frozen():
    """Check if the script is running as a frozen executable."""
    return getattr(sys, 'frozen', False)

def is_admin():
    """Check if the script is running with admin privileges (Windows only)."""
    if platform.system() == 'Windows':
        try:
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except Exception:
            return False
    else:
        return True

def run_as_admin():
    """Restart the current script with admin privileges (Windows only)."""
    if platform.system() != 'Windows':
        return False
    try:
        args = [sys.executable] + sys.argv
        print(f"{Fore.YELLOW}{EMOJI['ADMIN']} Requesting administrator privileges...{Style.RESET_ALL}")
        ctypes.windll.shell32.ShellExecuteW(None, 'runas', args[0], ' '.join(f'"{arg}"' for arg in args[1:]), None, 1)
        return True
    except Exception as e:
        print(f"{Fore.RED}{EMOJI['ERROR']} Failed to restart with admin privileges: {e}{Style.RESET_ALL}")
        return False

class Translator:
    """Translator"""
    __static_attributes__ = ('current_language', 'fallback_language', 'translations')
    
    def __init__(self):
        self.translations = {}
        self.current_language = self.detect_system_language()
        self.fallback_language = 'en'
        self.load_translations()
    
    def detect_system_language(self):
        """Detect system language and return corresponding language code"""
        try:
            system = platform.system()
            if system == 'Windows':
                return self._detect_windows_language()
            else:
                return self._detect_unix_language()
        except Exception as e:
            print(f"{Fore.YELLOW}{EMOJI['INFO']} Failed to detect system language: {e}{Style.RESET_ALL}")
            return 'en'
    
    def _detect_windows_language(self):
        """Detect language on Windows systems"""
        try:
            if platform.system() != 'Windows':
                return 'en'
            user32 = ctypes.windll.user32
            hwnd = user32.GetForegroundWindow()
            threadid = user32.GetWindowThreadProcessId(hwnd, 0)
            layout_id = user32.GetKeyboardLayout(threadid) & 65535
            language_map = {
                1033: 'en',
                1028: 'zh_tw',
                2052: 'zh_cn',
                1058: 'vi',
                1049: 'ru',
                1045: 'tr',
                1026: 'bg'
            }
            return language_map.get(layout_id, 'en')
        except Exception:
            return self._detect_unix_language()
    
    def _detect_unix_language(self):
        """Detect language on Unix-like systems (Linux, macOS)"""
        try:
            system_locale = locale.getdefaultlocale()[0]
            if not system_locale:
                return 'en'
            system_locale = system_locale.lower()
            if system_locale.startswith('zh_tw') or system_locale.startswith('zh_hk'):
                return 'zh_tw'
            if system_locale.startswith('zh_cn'):
                return 'zh_cn'
            if system_locale.startswith('en'):
                return 'en'
            if system_locale.startswith('vi'):
                return 'vi'
            if system_locale.startswith('nl'):
                return 'nl'
            if system_locale.startswith('de'):
                return 'de'
            if system_locale.startswith('fr'):
                return 'fr'
            if system_locale.startswith('pt'):
                return 'pt'
            if system_locale.startswith('ru'):
                return 'ru'
            if system_locale.startswith('tr'):
                return 'tr'
            if system_locale.startswith('bg'):
                return 'bg'
            env_lang = os.getenv('LANG', '').lower()
            if 'tw' in env_lang or 'hk' in env_lang:
                return 'zh_tw'
            if 'cn' in env_lang:
                return 'zh_cn'
            if 'vi' in env_lang:
                return 'vi'
            if 'nl' in env_lang:
                return 'nl'
            if 'de' in env_lang:
                return 'de'
            if 'fr' in env_lang:
                return 'fr'
            if 'pt' in env_lang:
                return 'pt'
            if 'ru' in env_lang:
                return 'ru'
            if 'tr' in env_lang:
                return 'tr'
            if 'bg' in env_lang:
                return 'bg'
            return 'en'
        except Exception:
            return 'en'
    
    def load_translations(self):
        """Load all available translations"""
        try:
            locales_dir = os.path.join(os.path.dirname(__file__), 'locales')
            if hasattr(sys, '_MEIPASS'):
                locales_dir = os.path.join(sys._MEIPASS, 'locales')
            if not os.path.exists(locales_dir):
                print(f"{Fore.RED}{EMOJI['ERROR']} Locales directory not found{Style.RESET_ALL}")
                return None
            for file in os.listdir(locales_dir):
                if file.endswith('.json'):
                    lang_code = file[:-5]
                    try:
                        with open(os.path.join(locales_dir, file), 'r', encoding='utf-8') as f:
                            self.translations[lang_code] = json.load(f)
                    except (json.JSONDecodeError, UnicodeDecodeError) as e:
                        print(f"{Fore.RED}{EMOJI['ERROR']} Error loading {file}: {e}{Style.RESET_ALL}")
                    except Exception as e:
                        print(f"{Fore.RED}{EMOJI['ERROR']} Failed to load translations: {e}{Style.RESET_ALL}")
                        return None
            return None
        except Exception as e:
            print(f"{Fore.RED}{EMOJI['ERROR']} Failed to load translations: {e}{Style.RESET_ALL}")
            return None
    
    def get(self, key, **kwargs):
        """Get translated text with fallback support"""
        try:
            result = self._get_translation(self.current_language, key)
            if result == key and self.current_language != self.fallback_language:
                result = self._get_translation(self.fallback_language, key)
            if kwargs:
                return result.format(**kwargs)
            return result
        except Exception:
            return key
    
    def _get_translation(self, lang_code, key):
        """Get translation for a specific language"""
        try:
            keys = key.split('.')
            value = self.translations.get(lang_code, {})
            for k in keys:
                if isinstance(value, dict):
                    value = value.get(k, key)
                else:
                    return key
            return value
        except Exception:
            return key
    
    def set_language(self, lang_code):
        """Set current language with validation"""
        if lang_code in self.translations:
            self.current_language = lang_code
            return True
        return False
    
    def get_available_languages(self):
        """Get list of available languages"""
        return list(self.translations.keys())

translator = Translator()

def print_menu():
    """Print menu options"""
    try:
        config = get_config(translator)
        if config.getboolean('Utils', 'enabled_account_info'):
            try:
                import cursor_acc_info
                cursor_acc_info.display_account_info(translator)
            except ImportError:
                pass
        print(f"\n{Fore.CYAN}{EMOJI['MENU']} {translator.get('menu.title')}:{Style.RESET_ALL}")
        if translator.current_language == 'zh_cn' or translator.current_language == 'zh_tw':
            print(f"{Fore.YELLOW}──────────────────────────────────────────────────────────────────────{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}──────────────────────────────────────────────────────────────────────────────────────────────────────────────{Style.RESET_ALL}")
        try:
            terminal_width = shutil.get_terminal_size().columns
        except Exception:
            terminal_width = 80
        menu_items = {
            0: f"{Fore.GREEN}0{Style.RESET_ALL}. {EMOJI['ERROR']} {translator.get('menu.exit')}",
            1: f"{Fore.GREEN}1{Style.RESET_ALL}. {EMOJI['RESET']} {translator.get('menu.reset')}",
            2: f"{Fore.GREEN}2{Style.RESET_ALL}. {EMOJI['SUCCESS']} {translator.get('menu.register')} ({Fore.RED}{translator.get('menu.outdate')}{Style.RESET_ALL})",
            3: f"{Fore.GREEN}3{Style.RESET_ALL}. {EMOJI['SUN']} {translator.get('menu.register_google')} {EMOJI['ROCKET']} ({Fore.YELLOW}{translator.get('menu.lifetime_access_enabled')}{Style.RESET_ALL})",
            4: f"{Fore.GREEN}4{Style.RESET_ALL}. {EMOJI['STAR']} {translator.get('menu.register_github')} {EMOJI['ROCKET']} ({Fore.YELLOW}{translator.get('menu.lifetime_access_enabled')}{Style.RESET_ALL})",
            5: f"{Fore.GREEN}5{Style.RESET_ALL}. {EMOJI['SUCCESS']} {translator.get('menu.register_manual')}",
            6: f"{Fore.GREEN}6{Style.RESET_ALL}. {EMOJI['RESET']} {translator.get('menu.temp_github_register')}",
            7: f"{Fore.GREEN}7{Style.RESET_ALL}. {EMOJI['ERROR']} {translator.get('menu.quit')}",
            8: f"{Fore.GREEN}8{Style.RESET_ALL}. {EMOJI['LANG']} {translator.get('menu.select_language')}",
            9: f"{Fore.GREEN}9{Style.RESET_ALL}. {EMOJI['UPDATE']} {translator.get('menu.disable_auto_update')}",
            10: f"{Fore.GREEN}10{Style.RESET_ALL}. {EMOJI['RESET']} {translator.get('menu.totally_reset')}",
            11: f"{Fore.GREEN}11{Style.RESET_ALL}. {EMOJI['CONTRIBUTE']} {translator.get('menu.contribute')}",
            12: f"{Fore.GREEN}12{Style.RESET_ALL}. {EMOJI['SETTINGS']}  {translator.get('menu.config')}",
            13: f"{Fore.GREEN}13{Style.RESET_ALL}. {EMOJI['SETTINGS']}  {translator.get('menu.select_chrome_profile')}",
            14: f"{Fore.GREEN}14{Style.RESET_ALL}. {EMOJI['ERROR']}  {translator.get('menu.delete_google_account', fallback='Delete Cursor Google Account')}",
            15: f"{Fore.GREEN}15{Style.RESET_ALL}. {EMOJI['UPDATE']}  {translator.get('menu.bypass_version_check', fallback='Bypass Cursor Version Check')}",
            16: f"{Fore.GREEN}16{Style.RESET_ALL}. {EMOJI['UPDATE']}  {translator.get('menu.check_user_authorized', fallback='Check User Authorized')}",
            17: f"{Fore.GREEN}17{Style.RESET_ALL}. {EMOJI['UPDATE']}  {translator.get('menu.bypass_token_limit', fallback='Bypass Token Limit')}"
        }
        total_items = len(menu_items)
        left_column_count = (total_items + 1) // 2
        sorted_indices = sorted(menu_items.keys())
        left_menu = [menu_items[i] for i in sorted_indices[:left_column_count]]
        right_menu = [menu_items[i] for i in sorted_indices[left_column_count:]]
        ansi_escape = re.compile('\\x1B(?:[@-Z\\\\-_]|\\[[0-?]*[ -/]*[@-~])')
        def get_display_width(s):
            """Calculate the display width of a string, considering Chinese characters and emojis"""
            clean_s = ansi_escape.sub('', s)
            width = 0
            for c in clean_s:
                if ord(c) > 127:
                    width += 2
                else:
                    width += 1
            return width
        max_left_width = 0
        for item in left_menu:
            width = get_display_width(item)
            max_left_width = max(max_left_width, width)
        fixed_spacing = 4
        right_start = max_left_width + fixed_spacing
        spaces_list = []
        for i in range(len(left_menu)):
            if i < len(left_menu):
                left_item = left_menu[i]
                left_width = get_display_width(left_item)
                spaces = right_start - left_width
                spaces_list.append(spaces)
        max_rows = max(len(left_menu), len(right_menu))
        for i in range(max_rows):
            if i < len(left_menu):
                left_item = left_menu[i]
                print(left_item, end='')
                spaces = spaces_list[i]
            else:
                spaces = right_start
                print('', end='')
            if i < len(right_menu):
                print(' ' * spaces + right_menu[i])
            else:
                print()
        if translator.current_language == 'zh_cn' or translator.current_language == 'zh_tw':
            print(f"{Fore.YELLOW}──────────────────────────────────────────────────────────────────────{Style.RESET_ALL}")
            return None
        else:
            print(f"{Fore.YELLOW}──────────────────────────────────────────────────────────────────────────────────────────────────────────────{Style.RESET_ALL}")
            return None
    except Exception as e:
        print(f"{Fore.YELLOW}{EMOJI['INFO']} {translator.get('menu.account_info_error', error=str(e))}{Style.RESET_ALL}")

def select_language():
    """Language selection menu"""
    print(f"\n{Fore.CYAN}{EMOJI['LANG']} {translator.get('menu.select_language')}:{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}────────────────────────────────────────{Style.RESET_ALL}")
    languages = translator.get_available_languages()
    for i, lang in enumerate(languages):
        lang_name = translator.get(f'languages.{lang}')
        print(f"{Fore.GREEN}{i}{Style.RESET_ALL}. {lang_name}")
    try:
        choice = input(f"\n{EMOJI['ARROW']} {Fore.CYAN}{translator.get('menu.input_choice', choices='0-' + str(len(languages) - 1))}{Style.RESET_ALL}: ")
        if choice.isdigit() and 0 <= int(choice) < len(languages):
            translator.set_language(languages[int(choice)])
            return True
        else:
            print(f"{Fore.RED}{EMOJI['ERROR']} {translator.get('menu.invalid_choice')}{Style.RESET_ALL}")
            return False
    except (ValueError, IndexError):
        print(f"{Fore.RED}{EMOJI['ERROR']} {translator.get('menu.invalid_choice')}{Style.RESET_ALL}")
        return False

def safe_print(text):
    """Safely print text, handling UnicodeEncodeError by encoding/decoding"""
    try:
        print(text)
    except UnicodeEncodeError:
        # Try to encode to UTF-8 and handle errors
        import sys
        if hasattr(sys.stdout, 'buffer'):
            try:
                encoded = text.encode('utf-8', errors='replace').decode('utf-8')
                print(encoded)
                return
            except:
                pass
        
        # Fallback: Remove emoji and ANSI codes, keep only the text content
        import re
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        clean_text = ansi_escape.sub('', text)
        # Remove common emoji characters
        emoji_map = {
            'ℹ️': '[INFO]', '❌': '[ERROR]', '✅': '[OK]', 
            '🔄': '[UPDATE]', '⚠️': '[WARN]', '📄': '[FILE]',
            '💾': '[BACKUP]', '📋': '[MENU]', '➜': '->',
            '🌐': '[LANG]', '🔐': '[ADMIN]', '💰': '[AIRDROP]',
            '🚀': '[ROCKET]', '⭐': '[STAR]', '🌟': '[SUN]',
            '🤝': '[CONTRIBUTE]', '⚙️': '[SETTINGS]'
        }
        for emoji, replacement in emoji_map.items():
            clean_text = clean_text.replace(emoji, replacement)
        
        # Final fallback: encode to ASCII with replacement
        try:
            clean_text = clean_text.encode('gbk', errors='replace').decode('gbk')
        except:
            clean_text = clean_text.encode('ascii', errors='replace').decode('ascii')
        
        print(clean_text)

def check_latest_version():
    """Check if current version matches the latest release version"""
    try:
        safe_print(f"\n{Fore.CYAN}{EMOJI['UPDATE']} {translator.get('updater.checking')}{Style.RESET_ALL}")
        headers = {
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'CursorCLTO-Updater'
        }
        response = requests.get('https://api.github.com/repos/clto/cursor-clto/releases/latest', headers=headers, timeout=10)
        if response.status_code == 403 and 'rate limit exceeded' in response.text.lower():
            print(f"{Fore.YELLOW}{EMOJI['INFO']} {translator.get('updater.rate_limit_exceeded', fallback='GitHub API rate limit exceeded. Skipping update check.')}{Style.RESET_ALL}")
            return None
        if response.status_code != 200:
            raise Exception('GitHub API returned status code ' + str(response.status_code))
        response_data = response.json()
        if 'tag_name' not in response_data:
            raise Exception('No version tag found in GitHub response')
        latest_version = response_data['tag_name'].lstrip('v')
        if not latest_version:
            raise Exception('Invalid version format received')
        def parse_version(version_str):
            """Parse version string into tuple for proper comparison"""
            try:
                return tuple(map(int, version_str.split('.')))
            except ValueError:
                return version_str
        current_version_tuple = parse_version(version)
        latest_version_tuple = parse_version(latest_version)
        is_newer_version_available = False
        if isinstance(current_version_tuple, tuple) and isinstance(latest_version_tuple, tuple):
            is_newer_version_available = current_version_tuple < latest_version_tuple
        else:
            is_newer_version_available = version != latest_version
        if is_newer_version_available:
            print(f"\n{Fore.YELLOW}{EMOJI['INFO']} {translator.get('updater.new_version_available', current=version, latest=latest_version)}{Style.RESET_ALL}")
            try:
                changelog_url = 'https://raw.githubusercontent.com/clto/cursor-clto/main/CHANGELOG.md'
                changelog_response = requests.get(changelog_url, timeout=10)
                if changelog_response.status_code == 200:
                    changelog_content = changelog_response.text
                    latest_version_pattern = f'## v{latest_version}'
                    changelog_sections = changelog_content.split('## v')
                    latest_changes = None
                    for section in changelog_sections:
                        if section.startswith(latest_version):
                            latest_changes = section
                            break
                    if latest_changes:
                        print(f"\n{Fore.CYAN}────────────────────────────────────────{Style.RESET_ALL}")
                        print(f"{Fore.CYAN}{translator.get('updater.changelog_title')}:{Style.RESET_ALL}")
                        changes_lines = latest_changes.strip().split('\n')
                        for i, line in enumerate(changes_lines[1:11]):
                            if line.strip():
                                print(f"{Fore.WHITE}{line.strip()}{Style.RESET_ALL}")
                        if len(changes_lines) > 11:
                            print(f"{Fore.WHITE}...{Style.RESET_ALL}")
                        print(f"{Fore.CYAN}────────────────────────────────────────{Style.RESET_ALL}")
            except Exception as changelog_error:
                pass
            choice = input(f"\n{EMOJI['ARROW']} {Fore.CYAN}{translator.get('updater.update_confirm', choices='Y/n')}{Style.RESET_ALL}: ").lower()
            if choice in ('', 'y', 'yes'):
                pass
            elif choice in ('n', 'no'):
                print(f"\n{Fore.YELLOW}{EMOJI['INFO']} {translator.get('updater.update_skipped')}{Style.RESET_ALL}")
                return None
            else:
                print(f"{Fore.RED}{EMOJI['ERROR']} {translator.get('menu.invalid_choice')}{Style.RESET_ALL}")
            try:
                if platform.system() == 'Windows':
                    update_command = 'irm https://raw.githubusercontent.com/clto/cursor-clto/main/scripts/install.ps1 | iex'
                    subprocess.run(['powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-Command', update_command], check=True)
                else:
                    install_script_url = 'https://raw.githubusercontent.com/clto/cursor-clto/main/scripts/install.sh'
                    script_response = requests.get(install_script_url, timeout=5)
                    if script_response.status_code != 200:
                        raise Exception('Installation script not found')
                    with open('install.sh', 'wb') as f:
                        f.write(script_response.content)
                    os.chmod('install.sh', 493)
                    subprocess.run(['./install.sh'], check=True)
                    if os.path.exists('install.sh'):
                        os.remove('install.sh')
                print(f"\n{Fore.GREEN}{EMOJI['SUCCESS']} {translator.get('updater.updating')}{Style.RESET_ALL}")
                sys.exit(0)
                return None
            except Exception as update_error:
                print(f"{Fore.RED}{EMOJI['ERROR']} {translator.get('updater.update_failed', error=str(update_error))}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}{EMOJI['INFO']} {translator.get('updater.manual_update_required')}{Style.RESET_ALL}")
                return None
        elif current_version_tuple > latest_version_tuple:
            print(f"{Fore.GREEN}{EMOJI['SUCCESS']} {translator.get('updater.development_version', current=version, latest=latest_version)}{Style.RESET_ALL}")
            return None
        else:
            print(f"{Fore.GREEN}{EMOJI['SUCCESS']} {translator.get('updater.up_to_date')}{Style.RESET_ALL}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"{Fore.RED}{EMOJI['ERROR']} {translator.get('updater.network_error', error=str(e))}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}{EMOJI['INFO']} {translator.get('updater.continue_anyway')}{Style.RESET_ALL}")
        return None
    except Exception as e:
        print(f"{Fore.RED}{EMOJI['ERROR']} {translator.get('updater.check_failed', error=str(e))}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}{EMOJI['INFO']} {translator.get('updater.continue_anyway')}{Style.RESET_ALL}")
        return None

def main():
    """Windows"""
    if platform.system() == 'Windows' and is_frozen() and not is_admin():
        print(f"{Fore.YELLOW}{EMOJI['ADMIN']} {translator.get('menu.admin_required')}{Style.RESET_ALL}")
        if run_as_admin():
            sys.exit(0)
        else:
            print(f"{Fore.YELLOW}{EMOJI['INFO']} {translator.get('menu.admin_required_continue')}{Style.RESET_ALL}")
    print_logo()
    config = get_config(translator)
    if not config:
        print(f"{Fore.RED}{EMOJI['ERROR']} {translator.get('menu.config_init_failed')}{Style.RESET_ALL}")
        return None
    force_update_config(translator)
    if config.getboolean('Utils', 'enabled_update_check'):
        check_latest_version()
    print_menu()
    try:
        while True:
            choice_num = 17
            choice = input(f"\n{EMOJI['ARROW']} {Fore.CYAN}{translator.get('menu.input_choice', choices='0-' + str(choice_num))}{Style.RESET_ALL}: ")
            if choice == '0':
                print(f"\n{Fore.YELLOW}{EMOJI['INFO']} {translator.get('menu.exit')}...{Style.RESET_ALL}")
                print(f"{Fore.CYAN}══════════════════════════════════════════════════{Style.RESET_ALL}")
                return None
            elif choice == '1':
                import reset_machine_manual
                reset_machine_manual.run(translator)
                print_menu()
            elif choice == '2':
                import cursor_register
                cursor_register.main(translator)
                print_menu()
            elif choice == '3':
                import cursor_register_google
                cursor_register_google.main(translator)
                print_menu()
            elif choice == '4':
                import cursor_register_github
                cursor_register_github.main(translator)
                print_menu()
            elif choice == '5':
                import cursor_register_manual
                cursor_register_manual.main(translator)
                print_menu()
            elif choice == '6':
                import github_cursor_register
                print(f"{Fore.YELLOW}{EMOJI['INFO']} {translator.get('menu.coming_soon')}{Style.RESET_ALL}")
                print_menu()
            elif choice == '7':
                import quit_cursor
                quit_cursor.quit_cursor(translator)
                print_menu()
            elif choice == '8':
                if select_language():
                    print_menu()
            elif choice == '9':
                import disable_auto_update
                disable_auto_update.run(translator)
                print_menu()
            elif choice == '10':
                import totally_reset_cursor
                totally_reset_cursor.run(translator)
                print_menu()
            elif choice == '11':
                import logo
                print(logo.CURSOR_CONTRIBUTORS)
                print_menu()
            elif choice == '12':
                from config import print_config
                print_config(get_config(), translator)
                print_menu()
            elif choice == '13':
                from oauth_auth import OAuthHandler
                oauth = OAuthHandler(translator)
                oauth._select_profile()
                print_menu()
            elif choice == '14':
                import delete_cursor_google
                delete_cursor_google.main(translator)
                print_menu()
            elif choice == '15':
                import bypass_version
                bypass_version.main(translator)
                print_menu()
            elif choice == '16':
                import check_user_authorized
                check_user_authorized.main(translator)
                print_menu()
            elif choice == '17':
                import bypass_token_limit
                bypass_token_limit.run(translator)
                print_menu()
            else:
                print(f"{Fore.RED}{EMOJI['ERROR']} {translator.get('menu.invalid_choice')}{Style.RESET_ALL}")
                print_menu()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}{EMOJI['INFO']} {translator.get('menu.program_terminated')}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}══════════════════════════════════════════════════{Style.RESET_ALL}")
        return None
    except Exception as e:
        print(f"{Fore.RED}{EMOJI['ERROR']} {translator.get('menu.error_occurred', error=str(e))}{Style.RESET_ALL}")
        print_menu()

if __name__ == '__main__':
    main()
