import os
import sys
import configparser
from colorama import Fore, Style
from utils import get_user_documents_path, get_default_chrome_path, get_linux_cursor_path
import shutil
import datetime

EMOJI = {
    'INFO': '\u2139\ufe0f',
    'WARNING': '\u26a0\ufe0f',
    'ERROR': '\u274c',
    'SUCCESS': '\u2705',
    'ADMIN': '\U0001f512',
    'ARROW': '\u27a1\ufe0f',
    'USER': '\U0001f464',
    'KEY': '\U0001f511',
    'SETTINGS': '\u2699\ufe0f',
}


def setup_config(translator=None):
    try:
        config_dir = os.path.join(get_user_documents_path(), '.cursor-free-vip')
        config_file = os.path.join(config_dir, 'config.ini')

        os.makedirs(config_dir, exist_ok=True)

        config = configparser.ConfigParser()

        default_config = {
            'Chrome': {
                'chromepath': get_default_chrome_path(),
            },
            'Turnstile': {
                'handle_turnstile_time': '2',
                'handle_turnstile_random_time': '1-3',
            },
            'Timing': {
                'min_random_time': '0.1',
                'max_random_time': '0.8',
                'page_load_wait': '0.1-0.8',
                'input_wait': '0.3-0.8',
                'submit_wait': '0.5-1.5',
                'verification_code_input': '0.1-0.3',
                'verification_success_wait': '2-3',
                'verification_retry_wait': '2-3',
                'email_check_initial_wait': '4-6',
                'email_refresh_wait': '2-4',
                'settings_page_load_wait': '1-2',
                'failed_retry_time': '0.5-1',
                'retry_interval': '8-12',
                'max_timeout': '160',
            },
            'Utils': {
                'enabled_update_check': 'True',
                'enabled_force_update': 'False',
                'enabled_account_info': 'True',
            },
        }

        if sys.platform == 'win32':
            appdata = os.getenv('APPDATA')
            localappdata = os.getenv('LOCALAPPDATA', '')

            default_config['WindowsPaths'] = {
                'storage_path': os.path.join(appdata, 'Cursor', 'User', 'globalStorage', 'storage.json'),
                'sqlite_path': os.path.join(appdata, 'Cursor', 'User', 'globalStorage', 'state.vscdb'),
                'machine_id_path': os.path.join(appdata, 'Cursor', 'machineId'),
                'cursor_path': os.path.join(localappdata, 'Programs', 'Cursor', 'resources', 'app'),
                'updater_path': os.path.join(localappdata, 'cursor-updater'),
                'update_yml_path': os.path.join(localappdata, 'Programs', 'Cursor', 'resources', 'app-update.yml'),
                'product_json_path': os.path.join(localappdata, 'Programs', 'Cursor', 'resources', 'app', 'product.json'),
            }

            os.makedirs(os.path.dirname(default_config['WindowsPaths']['storage_path']), exist_ok=True)

        elif sys.platform == 'darwin':
            default_config['MacPaths'] = {
                'storage_path': os.path.abspath(os.path.expanduser('~/Library/Application Support/Cursor/User/globalStorage/storage.json')),
                'sqlite_path': os.path.abspath(os.path.expanduser('~/Library/Application Support/Cursor/User/globalStorage/state.vscdb')),
                'machine_id_path': os.path.expanduser('~/Library/Application Support/Cursor/machineId'),
                'cursor_path': '/Applications/Cursor.app/Contents/Resources/app',
                'updater_path': os.path.expanduser('~/Library/Application Support/cursor-updater'),
                'update_yml_path': '/Applications/Cursor.app/Contents/Resources/app-update.yml',
                'product_json_path': '/Applications/Cursor.app/Contents/Resources/app/product.json',
            }

            os.makedirs(os.path.dirname(default_config['MacPaths']['storage_path']), exist_ok=True)

        elif sys.platform == 'linux':
            sudo_user = os.environ.get('SUDO_USER')
            current_user = sudo_user if sudo_user else os.getenv('USER', '')
            if not current_user:
                current_user = os.path.expanduser('~').split('/')[-1]

            if sudo_user:
                actual_home = f'/home/{sudo_user}'
                root_home = '/root'
            else:
                actual_home = f'/home/{current_user}'
                root_home = None

            if not os.path.exists(actual_home):
                actual_home = os.path.expanduser('~')

            config_base = os.path.join(actual_home, '.config')

            cursor_dir = None

            possible_paths = [
                os.path.join(config_base, 'Cursor'),
                os.path.join(config_base, 'cursor'),
                os.path.join(root_home, '.config', 'Cursor') if root_home else None,
                os.path.join(root_home, '.config', 'cursor') if root_home else None,
            ]

            try:
                for path in possible_paths:
                    if path and os.path.exists(path):
                        cursor_dir = path
                        break
            except (OSError, IOError) as e:
                if translator:
                    print(f"{Fore.RED}{EMOJI['ERROR']} {translator.get('config.error_checking_linux_paths', error=str(e))}{Style.RESET_ALL}")
                else:
                    print(f"{Fore.RED}{EMOJI['ERROR']} Error checking Linux paths: {str(e)}{Style.RESET_ALL}")

            if not cursor_dir:
                if translator:
                    print(f"{Fore.YELLOW}{EMOJI['WARNING']} {translator.get('config.neither_cursor_nor_cursor_directory_found', config_base=config_base)}{Style.RESET_ALL}")
                else:
                    print(f"{Fore.YELLOW}{EMOJI['WARNING']} Neither Cursor nor cursor directory found in {config_base}{Style.RESET_ALL}")

                if root_home:
                    if translator:
                        print(f"{Fore.YELLOW}{EMOJI['INFO']} {translator.get('config.also_checked', path=f'{root_home}/.config')}{Style.RESET_ALL}")
                    else:
                        print(f"{Fore.YELLOW}{EMOJI['INFO']} Also checked {root_home}/.config{Style.RESET_ALL}")

                if translator:
                    print(f"{Fore.YELLOW}{EMOJI['INFO']} {translator.get('config.please_make_sure_cursor_is_installed_and_has_been_run_at_least_once')}{Style.RESET_ALL}")
                else:
                    print(f"{Fore.YELLOW}{EMOJI['INFO']} Please make sure Cursor is installed and has been run at least once{Style.RESET_ALL}")

            if cursor_dir:
                storage_path = os.path.abspath(os.path.join(cursor_dir, 'User/globalStorage/storage.json'))
            else:
                storage_path = ''

            if storage_path:
                storage_dir = os.path.dirname(storage_path)
            else:
                storage_dir = ''

            if storage_dir and not os.path.exists(storage_dir):
                if translator:
                    print(f"{Fore.YELLOW}{EMOJI['WARNING']} {translator.get('config.storage_directory_not_found', storage_dir=storage_dir)}{Style.RESET_ALL}")
                else:
                    print(f"{Fore.YELLOW}{EMOJI['WARNING']} Storage directory not found: {storage_dir}{Style.RESET_ALL}")

                if translator:
                    print(f"{Fore.YELLOW}{EMOJI['INFO']} {translator.get('config.please_make_sure_cursor_is_installed_and_has_been_run_at_least_once')}{Style.RESET_ALL}")
                else:
                    print(f"{Fore.YELLOW}{EMOJI['INFO']} Please make sure Cursor is installed and has been run at least once{Style.RESET_ALL}")

            if storage_path and os.path.exists(storage_path):
                try:
                    stat = os.stat(storage_path)

                    if translator:
                        print(f"{Fore.GREEN}{EMOJI['INFO']} {translator.get('config.storage_file_found', storage_path=storage_path)}{Style.RESET_ALL}")
                    else:
                        print(f"{Fore.GREEN}{EMOJI['INFO']} Storage file found: {storage_path}{Style.RESET_ALL}")

                    if translator:
                        print(f"{Fore.GREEN}{EMOJI['INFO']} {translator.get('config.file_size', size=stat.st_size)}{Style.RESET_ALL}")
                    else:
                        print(f"{Fore.GREEN}{EMOJI['INFO']} File size: {stat.st_size} bytes{Style.RESET_ALL}")

                    if translator:
                        print(f"{Fore.GREEN}{EMOJI['INFO']} {translator.get('config.file_permissions', permissions=oct(stat.st_mode & 511))}{Style.RESET_ALL}")
                    else:
                        print(f"{Fore.GREEN}{EMOJI['INFO']} File permissions: {oct(stat.st_mode & 511)}{Style.RESET_ALL}")

                    if translator:
                        print(f"{Fore.GREEN}{EMOJI['INFO']} {translator.get('config.file_owner', owner=stat.st_uid)}{Style.RESET_ALL}")
                    else:
                        print(f"{Fore.GREEN}{EMOJI['INFO']} File owner: {stat.st_uid}{Style.RESET_ALL}")

                    if translator:
                        print(f"{Fore.GREEN}{EMOJI['INFO']} {translator.get('config.file_group', group=stat.st_gid)}{Style.RESET_ALL}")
                    else:
                        print(f"{Fore.GREEN}{EMOJI['INFO']} File group: {stat.st_gid}{Style.RESET_ALL}")
                except Exception as e:
                    if translator:
                        print(f"{Fore.RED}{EMOJI['ERROR']} {translator.get('config.error_getting_file_stats', error=str(e))}{Style.RESET_ALL}")
                    else:
                        print(f"{Fore.RED}{EMOJI['ERROR']} Error getting file stats: {str(e)}{Style.RESET_ALL}")

                if not os.access(storage_path, os.R_OK | os.W_OK):
                    if translator:
                        print(f"{Fore.RED}{EMOJI['ERROR']} {translator.get('config.permission_denied', storage_path=storage_path)}{Style.RESET_ALL}")
                    else:
                        print(f"{Fore.RED}{EMOJI['ERROR']} Permission denied: {storage_path}{Style.RESET_ALL}")

                    if sudo_user:
                        if translator:
                            print(f"{Fore.YELLOW}{EMOJI['INFO']} {translator.get('config.try_running', command=f'chown {sudo_user}:{sudo_user} {storage_path}')}{Style.RESET_ALL}")
                        else:
                            print(f"{Fore.YELLOW}{EMOJI['INFO']} Try running: chown {sudo_user}:{sudo_user} {storage_path}{Style.RESET_ALL}")

                        if translator:
                            print(f"{Fore.YELLOW}{EMOJI['INFO']} {translator.get('config.and')}: chmod 644 {storage_path}{Style.RESET_ALL}")
                        else:
                            print(f"{Fore.YELLOW}{EMOJI['INFO']} And: chmod 644 {storage_path}{Style.RESET_ALL}")
                    else:
                        if translator:
                            print(f"{Fore.YELLOW}{EMOJI['INFO']} {translator.get('config.try_running', command=f'chown {current_user}:{current_user} {storage_path}')}{Style.RESET_ALL}")
                        else:
                            print(f"{Fore.YELLOW}{EMOJI['INFO']} Try running: chown {current_user}:{current_user} {storage_path}{Style.RESET_ALL}")

                        if translator:
                            print(f"{Fore.YELLOW}{EMOJI['INFO']} {translator.get('config.and')}: chmod 644 {storage_path}{Style.RESET_ALL}")
                        else:
                            print(f"{Fore.YELLOW}{EMOJI['INFO']} And: chmod 644 {storage_path}{Style.RESET_ALL}")

                try:
                    with open(storage_path, 'r') as f:
                        content = f.read()

                    if not content.strip():
                        if translator:
                            print(f"{Fore.YELLOW}{EMOJI['WARNING']} {translator.get('config.storage_file_is_empty', storage_path=storage_path)}{Style.RESET_ALL}")
                        else:
                            print(f"{Fore.YELLOW}{EMOJI['WARNING']} Storage file is empty: {storage_path}{Style.RESET_ALL}")

                        if translator:
                            print(f"{Fore.YELLOW}{EMOJI['INFO']} {translator.get('config.the_file_might_be_corrupted_please_reinstall_cursor')}{Style.RESET_ALL}")
                        else:
                            print(f"{Fore.YELLOW}{EMOJI['INFO']} The file might be corrupted, please reinstall Cursor{Style.RESET_ALL}")
                    else:
                        if translator:
                            print(f"{Fore.GREEN}{EMOJI['SUCCESS']} {translator.get('config.storage_file_is_valid_and_contains_data')}{Style.RESET_ALL}")
                        else:
                            print(f"{Fore.GREEN}{EMOJI['SUCCESS']} Storage file is valid and contains data{Style.RESET_ALL}")
                except Exception as e:
                    if translator:
                        print(f"{Fore.RED}{EMOJI['ERROR']} {translator.get('config.error_reading_storage_file', error=str(e))}{Style.RESET_ALL}")
                    else:
                        print(f"{Fore.RED}{EMOJI['ERROR']} Error reading storage file: {str(e)}{Style.RESET_ALL}")

                    if translator:
                        print(f"{Fore.YELLOW}{EMOJI['INFO']} {translator.get('config.the_file_might_be_corrupted_please_reinstall_cursor')}{Style.RESET_ALL}")
                    else:
                        print(f"{Fore.YELLOW}{EMOJI['INFO']} The file might be corrupted. Please reinstall Cursor{Style.RESET_ALL}")

            else:
                if storage_path:
                    if translator:
                        print(f"{Fore.YELLOW}{EMOJI['WARNING']} {translator.get('config.storage_file_not_found', storage_path=storage_path)}{Style.RESET_ALL}")
                    else:
                        print(f"{Fore.YELLOW}{EMOJI['WARNING']} Storage file not found: {storage_path}{Style.RESET_ALL}")

                    if translator:
                        print(f"{Fore.YELLOW}{EMOJI['INFO']} {translator.get('config.please_make_sure_cursor_is_installed_and_has_been_run_at_least_once')}{Style.RESET_ALL}")
                    else:
                        print(f"{Fore.YELLOW}{EMOJI['INFO']} Please make sure Cursor is installed and has been run at least once{Style.RESET_ALL}")

            default_config['LinuxPaths'] = {
                'storage_path': storage_path,
                'sqlite_path': os.path.abspath(os.path.join(cursor_dir, 'User/globalStorage/state.vscdb')) if cursor_dir else '',
                'machine_id_path': os.path.join(cursor_dir, 'machineid') if cursor_dir else '',
                'cursor_path': get_linux_cursor_path(),
                'updater_path': os.path.join(config_base, 'cursor-updater'),
                'update_yml_path': os.path.join(cursor_dir, 'resources/app-update.yml') if cursor_dir else '',
                'product_json_path': os.path.join(cursor_dir, 'resources/app/product.json') if cursor_dir else '',
            }

        if os.path.exists(config_file):
            config.read(config_file, encoding='utf-8')

            config_modified = False

            for section, options in default_config.items():
                if not config.has_section(section):
                    config.add_section(section)
                    config_modified = True

                for option, value in options.items():
                    if config.has_option(section, option):
                        continue

                    config.set(section, option, str(value))
                    config_modified = True

                    if translator:
                        print(f"{Fore.YELLOW}{EMOJI['INFO']} {translator.get('config.config_option_added', option=f'{section}.{option}')}{Style.RESET_ALL}")

            if config_modified:
                with open(config_file, 'w', encoding='utf-8') as f:
                    config.write(f)

                if translator:
                    print(f"{Fore.GREEN}{EMOJI['SUCCESS']} {translator.get('config.config_updated')}{Style.RESET_ALL}")
                else:
                    print(f"{Fore.GREEN}{EMOJI['SUCCESS']} Config updated{Style.RESET_ALL}")

            return config
        else:
            for section, options in default_config.items():
                config.add_section(section)
                for option, value in options.items():
                    config.set(section, option, str(value))

            with open(config_file, 'w', encoding='utf-8') as f:
                config.write(f)

            if translator:
                print(f"{Fore.GREEN}{EMOJI['SUCCESS']} {translator.get('config.config_created', config_file=config_file)}{Style.RESET_ALL}")
            else:
                print(f"{Fore.GREEN}{EMOJI['SUCCESS']} Config created: {config_file}{Style.RESET_ALL}")

            return config
    except Exception as e:
        if translator:
            print(f"{Fore.RED}{EMOJI['ERROR']} {translator.get('config.config_setup_error', error=str(e))}{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}{EMOJI['ERROR']} Error setting up config: {str(e)}{Style.RESET_ALL}")
        return None


def print_config(config, translator):
    if not config:
        if translator:
            print(f"{Fore.YELLOW}{EMOJI['WARNING']} {translator.get('config.config_not_available')}{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}{EMOJI['WARNING']} Configuration not available{Style.RESET_ALL}")
        return None

    print(f"\n{Fore.CYAN}{EMOJI['INFO']} {translator.get('config.configuration') if translator else 'Configuration'}:{Style.RESET_ALL}")
    print(f"\n{Fore.CYAN}{'──────────────────────────────────────────────────────────────────────'}{Style.RESET_ALL}")

    for section in config.sections():
        print(f"{Fore.GREEN}[{section}]{Style.RESET_ALL}")

        for key, value in config.items(section):
            if value.lower() in ('true', 'yes', 'on', '1'):
                value_display = f"{Fore.GREEN}{translator.get('config.enabled') if translator else 'Enabled'}{Style.RESET_ALL}"
            elif value.lower() in ('false', 'no', 'off', '0'):
                value_display = f"{Fore.RED}{translator.get('config.disabled') if translator else 'Disabled'}{Style.RESET_ALL}"
            else:
                value_display = value

            print(f"  {key} = {value_display}")

    print(f"\n{Fore.CYAN}{'──────────────────────────────────────────────────────────────────────'}{Style.RESET_ALL}")

    config_dir = os.path.join(get_user_documents_path(), '.cursor-free-vip', 'config.ini')
    if translator:
        print(f"{Fore.CYAN}{EMOJI['INFO']} {translator.get('config.config_directory')}: {config_dir}{Style.RESET_ALL}")
    else:
        print(f"{Fore.CYAN}{EMOJI['INFO']} Config Directory: {config_dir}{Style.RESET_ALL}")

    print()
    return None


def force_update_config(translator):
    try:
        config_dir = os.path.join(get_user_documents_path(), '.cursor-free-vip')
        config_file = os.path.join(config_dir, 'config.ini')
        current_time = datetime.datetime.now()

        if os.path.exists(config_file):
            try:
                existing_config = configparser.ConfigParser()
                existing_config.read(config_file, encoding='utf-8')

                update_enabled = True

                if existing_config.has_section('Utils') and existing_config.has_option('Utils', 'enabled_force_update'):
                    update_enabled = existing_config.get('Utils', 'enabled_force_update').strip().lower() in ('true', 'yes', '1', 'on')

                if update_enabled:
                    try:
                        backup_file = f"{config_file}.bak.{current_time.strftime('%Y%m%d_%H%M%S')}"
                        shutil.copy2(config_file, backup_file)

                        if translator:
                            print(f"\n{Fore.CYAN}{EMOJI['INFO']} {translator.get('config.backup_created', path=backup_file)}{Style.RESET_ALL}")

                        print(f"\n{Fore.CYAN}{EMOJI['INFO']} {translator.get('config.config_force_update_enabled') if translator else 'Config file force update enabled'}{Style.RESET_ALL}")

                        os.remove(config_file)

                        if translator:
                            print(f"{Fore.CYAN}{EMOJI['INFO']} {translator.get('config.config_removed')}{Style.RESET_ALL}")
                        else:
                            print(f"{Fore.CYAN}{EMOJI['INFO']} Config file removed for forced update{Style.RESET_ALL}")
                    except Exception as e:
                        if translator:
                            print(f"{Fore.RED}{EMOJI['ERROR']} {translator.get('config.backup_failed', error=str(e))}{Style.RESET_ALL}")
                        else:
                            print(f"{Fore.RED}{EMOJI['ERROR']} Failed to backup config: {str(e)}{Style.RESET_ALL}")
                else:
                    if translator:
                        try:
                            print(f"\n{Fore.CYAN}{EMOJI['INFO']} {translator.get('config.config_force_update_disabled', fallback='Config file force update disabled by configuration. Keeping existing config file.')}{Style.RESET_ALL}")
                        except UnicodeEncodeError:
                            print(f"\n{Fore.CYAN}[INFO] {translator.get('config.config_force_update_disabled', fallback='Config file force update disabled by configuration. Keeping existing config file.')}{Style.RESET_ALL}")
                    else:
                        print(f"\n{Fore.CYAN}[INFO] Config file force update disabled by configuration. Keeping existing config file.{Style.RESET_ALL}")
            except Exception as e:
                if translator:
                    try:
                        print(f"{Fore.RED}{EMOJI['ERROR']} {translator.get('config.force_update_failed', error=str(e))}{Style.RESET_ALL}")
                    except UnicodeEncodeError:
                        print(f"{Fore.RED}[ERROR] {translator.get('config.force_update_failed', error=str(e))}{Style.RESET_ALL}")
                else:
                    print(f"{Fore.RED}[ERROR] Force update config failed: {str(e)}{Style.RESET_ALL}")
                return None

        return setup_config(translator)
    except Exception as e:
        if translator:
            try:
                print(f"{Fore.RED}{EMOJI['ERROR']} {translator.get('config.config_setup_error', error=str(e))}{Style.RESET_ALL}")
            except UnicodeEncodeError:
                print(f"{Fore.RED}[ERROR] {translator.get('config.config_setup_error', error=str(e))}{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}[ERROR] Error setting up config: {str(e)}{Style.RESET_ALL}")
        return None


def get_config(translator):
    return setup_config(translator)
