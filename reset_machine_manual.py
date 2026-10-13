import os
import sys
import json
import uuid
import hashlib
import shutil
import sqlite3
import platform
import re
import tempfile
import glob
from colorama import Fore, Style, init
from typing import Tuple
import configparser
from new_signup import get_user_documents_path
import traceback
from config import get_config
from datetime import datetime

init()

EMOJI = {
    'FILE': '\U0001f4c4',
    'BACKUP': '\U0001f4be',
    'SUCCESS': '\u2705',
    'ERROR': '\u274c',
    'INFO': '\u2139\ufe0f',
    'RESET': '\U0001f504',
    'WARNING': '\u26a0\ufe0f',
}


def get_cursor_paths(translator) -> Tuple[str, str]:
    system = platform.system()

    config = configparser.ConfigParser()
    config_dir = os.path.join(get_user_documents_path(), '.cursor-free-vip')
    config_file = os.path.join(config_dir, 'config.ini')

    if not os.path.exists(config_dir):
        os.makedirs(config_dir)

    default_paths = {
        'Darwin': '/Applications/Cursor.app/Contents/Resources/app',
        'Windows': os.path.join(os.getenv('LOCALAPPDATA', ''), 'Programs', 'Cursor', 'resources', 'app'),
        'Linux': [
            '/opt/Cursor/resources/app',
            '/usr/share/cursor/resources/app',
            os.path.expanduser('~/.local/share/cursor/resources/app'),
            '/usr/lib/cursor/app/',
        ],
    }

    if system == 'Linux':
        extracted_usr_paths = glob.glob(os.path.expanduser('~/squashfs-root/usr/share/cursor/resources/app'))
        current_dir_paths = glob.glob('squashfs-root/usr/share/cursor/resources/app')
        default_paths['Linux'].extend(extracted_usr_paths)
        default_paths['Linux'].extend(current_dir_paths)

        print(f"{Fore.CYAN}{EMOJI['INFO']} Available paths found:{Style.RESET_ALL}")
        for path in default_paths['Linux']:
            if os.path.exists(path):
                print(f"{Fore.GREEN}{EMOJI['SUCCESS']} {path} (exists){Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}{EMOJI['ERROR']} {path} (not found){Style.RESET_ALL}")

    if not os.path.exists(config_file):
        for section in ('MacPaths', 'WindowsPaths', 'LinuxPaths'):
            if not config.has_section(section):
                config.add_section(section)

        if system == 'Darwin':
            config.set('MacPaths', 'cursor_path', default_paths['Darwin'])
        elif system == 'Windows':
            config.set('WindowsPaths', 'cursor_path', default_paths['Windows'])
        elif system == 'Linux':
            for path in default_paths['Linux']:
                if os.path.exists(path):
                    config.set('LinuxPaths', 'cursor_path', path)
                    break
            else:
                config.set('LinuxPaths', 'cursor_path', default_paths['Linux'][0])

        with open(config_file, 'w', encoding='utf-8') as f:
            config.write(f)
    else:
        config.read(config_file, encoding='utf-8')

    if system == 'Darwin':
        section = 'MacPaths'
    elif system == 'Windows':
        section = 'WindowsPaths'
    elif system == 'Linux':
        section = 'LinuxPaths'
    else:
        if translator:
            raise OSError(translator.get('reset.unsupported_os', system=system))
        raise OSError(f'\u4e0d\u652f\u6301\u7684\u64cd\u4f5c\u7cfb\u7edf: {system}')

    if not config.has_section(section) or not config.has_option(section, 'cursor_path'):
        if translator:
            raise OSError(translator.get('reset.path_not_configured'))
        raise OSError('\u672a\u914d\u7f6e Cursor \u8def\u5f91')

    base_path = config.get(section, 'cursor_path')

    if system == 'Linux' and not os.path.exists(base_path):
        for path in default_paths['Linux']:
            if os.path.exists(path):
                base_path = path
                config.set(section, 'cursor_path', path)
                with open(config_file, 'w', encoding='utf-8') as f:
                    config.write(f)
                break

    if not os.path.exists(base_path):
        if translator:
            raise OSError(translator.get('reset.path_not_found', path=base_path))
        raise OSError(f'\u627e\u4e0d\u5230 Cursor \u8def\u5f91: {base_path}')

    pkg_path = os.path.join(base_path, 'package.json')
    main_path = os.path.join(base_path, 'out/main.js')

    if not os.path.exists(pkg_path):
        if translator:
            raise OSError(translator.get('reset.package_not_found', path=pkg_path))
        raise OSError(f'\u627e\u4e0d\u5230 package.json: {pkg_path}')

    if not os.path.exists(main_path):
        if translator:
            raise OSError(translator.get('reset.main_not_found', path=main_path))
        raise OSError(f'\u627e\u4e0d\u5230 main.js: {main_path}')

    return pkg_path, main_path


def get_cursor_machine_id_path(translator=None) -> str:
    config_dir = os.path.join(get_user_documents_path(), '.cursor-free-vip')
    config_file = os.path.join(config_dir, 'config.ini')
    config = configparser.ConfigParser()

    if os.path.exists(config_file):
        config.read(config_file)

    if sys.platform == 'win32':
        if not config.has_section('WindowsPaths'):
            config.add_section('WindowsPaths')
            config.set('WindowsPaths', 'machine_id_path',
                       os.path.join(os.getenv('APPDATA'), 'Cursor', 'machineId'))
        return config.get('WindowsPaths', 'machine_id_path')

    if sys.platform == 'linux':
        if not config.has_section('LinuxPaths'):
            config.add_section('LinuxPaths')
            config.set('LinuxPaths', 'machine_id_path',
                       os.path.expanduser('~/.config/cursor/machineid'))
        return config.get('LinuxPaths', 'machine_id_path')

    if sys.platform == 'darwin':
        if not config.has_section('MacPaths'):
            config.add_section('MacPaths')
            config.set('MacPaths', 'machine_id_path',
                       os.path.expanduser('~/Library/Application Support/Cursor/machineId'))
        return config.get('MacPaths', 'machine_id_path')

    raise OSError(f'Unsupported operating system: {sys.platform}')


def get_workbench_cursor_path(translator=None) -> str:
    system = platform.system()

    config_dir = os.path.join(get_user_documents_path(), '.cursor-free-vip')
    config_file = os.path.join(config_dir, 'config.ini')
    config = configparser.ConfigParser()

    if os.path.exists(config_file):
        config.read(config_file)

    paths_map = {
        'Darwin': {
            'base': '/Applications/Cursor.app/Contents/Resources/app',
            'main': 'out/vs/workbench/workbench.desktop.main.js',
        },
        'Windows': {
            'main': 'out\\vs\\workbench\\workbench.desktop.main.js',
        },
        'Linux': {
            'bases': [
                '/opt/Cursor/resources/app',
                '/usr/share/cursor/resources/app',
                '/usr/lib/cursor/app/',
            ],
            'main': 'out/vs/workbench/workbench.desktop.main.js',
        },
    }

    if system == 'Linux':
        extracted_usr_paths = glob.glob(os.path.expanduser('~/squashfs-root/usr/share/cursor/resources/app'))
        paths_map['Linux']['bases'].extend(extracted_usr_paths)

    if system not in paths_map:
        if translator:
            raise OSError(translator.get('reset.unsupported_os', system=system))
        raise OSError(f'\u4e0d\u652f\u6301\u7684\u64cd\u4f5c\u7cfb\u7edf: {system}')

    if system == 'Linux':
        for base in paths_map['Linux']['bases']:
            main_path = os.path.join(base, paths_map['Linux']['main'])
            print(f"{Fore.CYAN}{EMOJI['INFO']} Checking path: {main_path}{Style.RESET_ALL}")
            if os.path.exists(main_path):
                return main_path

    if system == 'Windows':
        base_path = config.get('WindowsPaths', 'cursor_path')
    elif system == 'Darwin':
        base_path = paths_map[system]['base']
    else:
        base_path = paths_map[system]['bases'][0]

    main_path = os.path.join(base_path, paths_map[system]['main'])

    if not os.path.exists(main_path):
        if translator:
            raise OSError(translator.get('reset.file_not_found', path=main_path))
        raise OSError(f'\u672a\u627e\u5230 Cursor main.js \u6587\u4ef6: {main_path}')

    return main_path


def version_check(version: str, min_version: str = '', max_version: str = '', translator=None) -> bool:
    version_pattern = '^\\d+\\.\\d+\\.\\d+$'

    try:
        if not re.match(version_pattern, version):
            print(f"{Fore.RED}{EMOJI['ERROR']} {translator.get('reset.invalid_version_format', version=version)}{Style.RESET_ALL}")
            return False

        def parse_version(ver: str) -> Tuple[int, ...]:
            return tuple(map(int, ver.split('.')))

        current = parse_version(version)

        if min_version and current < parse_version(min_version):
            print(f"{Fore.RED}{EMOJI['ERROR']} {translator.get('reset.version_too_low', version=version, min_version=min_version)}{Style.RESET_ALL}")
            return False

        if max_version and current > parse_version(max_version):
            print(f"{Fore.RED}{EMOJI['ERROR']} {translator.get('reset.version_too_high', version=version, max_version=max_version)}{Style.RESET_ALL}")
            return False

        return True
    except Exception as e:
        print(f"{Fore.RED}{EMOJI['ERROR']} {translator.get('reset.version_check_error', error=str(e))}{Style.RESET_ALL}")
        return False


def check_cursor_version(translator) -> bool:
    try:
        pkg_path, _ = get_cursor_paths(translator)

        print(f"{Fore.CYAN}{EMOJI['INFO']} {translator.get('reset.reading_package_json', path=pkg_path)}{Style.RESET_ALL}")

        try:
            with open(pkg_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except UnicodeDecodeError:
            with open(pkg_path, 'r', encoding='latin-1') as f:
                data = json.load(f)

        if not isinstance(data, dict):
            print(f"{Fore.RED}{EMOJI['ERROR']} {translator.get('reset.invalid_json_object')}{Style.RESET_ALL}")
            return False

        if 'version' not in data:
            print(f"{Fore.RED}{EMOJI['ERROR']} {translator.get('reset.no_version_field')}{Style.RESET_ALL}")
            return False

        version = str(data['version']).strip()

        if not version:
            print(f"{Fore.RED}{EMOJI['ERROR']} {translator.get('reset.version_field_empty')}{Style.RESET_ALL}")
            return False

        print(f"{Fore.CYAN}{EMOJI['INFO']} {translator.get('reset.found_version', version=version)}{Style.RESET_ALL}")

        if not re.match('^\\d+\\.\\d+\\.\\d+$', version):
            print(f"{Fore.RED}{EMOJI['ERROR']} {translator.get('reset.invalid_version_format', version=version)}{Style.RESET_ALL}")
            return False

        try:
            current = tuple(map(int, version.split('.')))
            min_ver = (0, 45, 0)

            if current >= min_ver:
                print(f"{Fore.GREEN}{EMOJI['SUCCESS']} {translator.get('reset.version_check_passed', version=version, min_version='0.45.0')}{Style.RESET_ALL}")
                return True

            print(f"{Fore.YELLOW}{EMOJI['INFO']} {translator.get('reset.version_too_low', version=version, min_version='0.45.0')}{Style.RESET_ALL}")
            return False
        except ValueError as e:
            print(f"{Fore.RED}{EMOJI['ERROR']} {translator.get('reset.version_parse_error', error=str(e))}{Style.RESET_ALL}")
            return False
    except FileNotFoundError as e:
        print(f"{Fore.RED}{EMOJI['ERROR']} {translator.get('reset.package_not_found', path=pkg_path)}{Style.RESET_ALL}")
        return False
    except json.JSONDecodeError as e:
        print(f"{Fore.RED}{EMOJI['ERROR']} {translator.get('reset.invalid_json_object')}{Style.RESET_ALL}")
        return False
    except Exception as e:
        print(f"{Fore.RED}{EMOJI['ERROR']} {translator.get('reset.check_version_failed', error=str(e))}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}{EMOJI['INFO']} {translator.get('reset.stack_trace')}: {traceback.format_exc()}{Style.RESET_ALL}")
        return False


def modify_workbench_js(file_path: str, translator) -> bool:
    try:
        original_stat = os.stat(file_path)
        original_mode = original_stat.st_mode
        original_uid = original_stat.st_uid
        original_gid = original_stat.st_gid

        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', errors='ignore', delete=False) as tmp_file:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as main_file:
                content = main_file.read()

            patterns = {
                'B(k,D(Ln,{title:"Upgrade to Pro",size:"small",get codicon(){return A.rocket},get onClick(){return t.pay}}),null)': 'B(k,D(Ln,{title:"hovanhoa GitHub",size:"small",get codicon(){return A.github},get onClick(){return function(){window.open("https://github.com/hovanhoa/cursor-free-vip","_blank")}}}),null)',
                'M(x,I(as,{title:"Upgrade to Pro",size:"small",get codicon(){return $.rocket},get onClick(){return t.pay}}),null)': 'M(x,I(as,{title:"hovanhoa GitHub",size:"small",get codicon(){return $.rocket},get onClick(){return function(){window.open("https://github.com/hovanhoa/cursor-free-vip","_blank")}}}),null)',
                '<div>Pro Trial': '<div>Pro',
                'py-1">Auto-select': 'py-1">Bypass-Version-Pin',
                'async getEffectiveTokenLimit(e){const n=e.modelName;if(!n)return 2e5;': 'async getEffectiveTokenLimit(e){return 9000000;const n=e.modelName;if(!n)return 9e5;',
                'var DWr=ne("<div class=settings__item_description>You are currently signed in with <strong></strong>.");': 'var DWr=ne("<div class=settings__item_description>You are currently signed in with <strong></strong>. <h1>Pro</h1>");',
                'notifications-toasts': 'notifications-toasts hidden',
            }

            for old_pattern, new_pattern in patterns.items():
                content = content.replace(old_pattern, new_pattern)

            tmp_file.write(content)
            tmp_path = tmp_file.name

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = f"{file_path}.backup.{timestamp}"
        shutil.copy2(file_path, backup_path)
        print(f"{Fore.GREEN}{EMOJI['SUCCESS']} {translator.get('reset.backup_created', path=backup_path)}{Style.RESET_ALL}")

        if os.path.exists(file_path):
            os.remove(file_path)

        shutil.move(tmp_path, file_path)

        os.chmod(file_path, original_mode)
        if os.name != 'nt':
            os.chown(file_path, original_uid, original_gid)

        print(f"{Fore.GREEN}{EMOJI['SUCCESS']} {translator.get('reset.file_modified')}{Style.RESET_ALL}")
        return True
    except Exception as e:
        print(f"{Fore.RED}{EMOJI['ERROR']} {translator.get('reset.modify_file_failed', error=str(e))}{Style.RESET_ALL}")
        if 'tmp_path' in locals():
            try:
                os.unlink(tmp_path)
            except:
                pass
        return False


def modify_main_js(main_path: str, translator) -> bool:
    try:
        original_stat = os.stat(main_path)
        original_mode = original_stat.st_mode
        original_uid = original_stat.st_uid
        original_gid = original_stat.st_gid

        with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp_file:
            with open(main_path, 'r', encoding='utf-8') as main_file:
                content = main_file.read()

            patterns = {
                'async getMachineId\\(\\)\\{return [^??]+\\?\\?([^}]+)\\}': 'async getMachineId(){return \\1}',
                'async getMacMachineId\\(\\)\\{return [^??]+\\?\\?([^}]+)\\}': 'async getMacMachineId(){return \\1}',
            }

            for pattern, replacement in patterns.items():
                content = re.sub(pattern, replacement, content)

            tmp_file.write(content)
            tmp_path = tmp_file.name

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = f"{main_path}.old.{timestamp}"
        shutil.copy2(main_path, backup_path)
        print(f"{Fore.GREEN}{EMOJI['SUCCESS']} {translator.get('reset.backup_created', path=backup_path)}{Style.RESET_ALL}")

        shutil.move(tmp_path, main_path)

        os.chmod(main_path, original_mode)
        if os.name != 'nt':
            os.chown(main_path, original_uid, original_gid)

        print(f"{Fore.GREEN}{EMOJI['SUCCESS']} {translator.get('reset.file_modified')}{Style.RESET_ALL}")
        return True
    except Exception as e:
        print(f"{Fore.RED}{EMOJI['ERROR']} {translator.get('reset.modify_file_failed', error=str(e))}{Style.RESET_ALL}")
        if 'tmp_path' in locals():
            os.unlink(tmp_path)
        return False


def patch_cursor_get_machine_id(translator) -> bool:
    try:
        print(f"{Fore.CYAN}{EMOJI['INFO']} {translator.get('reset.start_patching')}...{Style.RESET_ALL}")

        pkg_path, main_path = get_cursor_paths(translator)

        for file_path in (pkg_path, main_path):
            if not os.path.isfile(file_path):
                print(f"{Fore.RED}{EMOJI['ERROR']} {translator.get('reset.file_not_found', path=file_path)}{Style.RESET_ALL}")
                return False
            if not os.access(file_path, os.W_OK):
                print(f"{Fore.RED}{EMOJI['ERROR']} {translator.get('reset.no_write_permission', path=file_path)}{Style.RESET_ALL}")
                return False

        try:
            with open(pkg_path, 'r', encoding='utf-8') as f:
                version = json.load(f)['version']

            print(f"{Fore.CYAN}{EMOJI['INFO']} {translator.get('reset.current_version', version=version)}{Style.RESET_ALL}")

            if not version_check(version, '0.45.0', translator=translator):
                print(f"{Fore.RED}{EMOJI['ERROR']} {translator.get('reset.version_not_supported')}{Style.RESET_ALL}")
                return False

            print(f"{Fore.CYAN}{EMOJI['INFO']} {translator.get('reset.version_check_passed')}{Style.RESET_ALL}")

            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = f"{main_path}.bak.{timestamp}"

            if not os.path.exists(backup_path):
                shutil.copy2(main_path, backup_path)
                print(f"{Fore.GREEN}{EMOJI['SUCCESS']} {translator.get('reset.backup_created', path=backup_path)}{Style.RESET_ALL}")

            if not modify_main_js(main_path, translator):
                return False

            print(f"{Fore.GREEN}{EMOJI['SUCCESS']} {translator.get('reset.patch_completed')}{Style.RESET_ALL}")
            return True
        except Exception as e:
            print(f"{Fore.RED}{EMOJI['ERROR']} {translator.get('reset.read_version_failed', error=str(e))}{Style.RESET_ALL}")
            return False
    except Exception as e:
        print(f"{Fore.RED}{EMOJI['ERROR']} {translator.get('reset.patch_failed', error=str(e))}{Style.RESET_ALL}")
        return False


class MachineIDResetter:
    __static_attributes__ = ('db_path', 'sqlite_path', 'translator')

    def __init__(self, translator=None):
        self.translator = translator

        config_dir = os.path.join(get_user_documents_path(), '.cursor-free-vip')
        config_file = os.path.join(config_dir, 'config.ini')
        config = configparser.ConfigParser()

        if not os.path.exists(config_file):
            raise FileNotFoundError(f'Config file not found: {config_file}')

        config.read(config_file, encoding='utf-8')

        if sys.platform == 'win32':
            appdata = os.getenv('APPDATA')
            if appdata is None:
                raise EnvironmentError('APPDATA Environment Variable Not Set')

            if not config.has_section('WindowsPaths'):
                config.add_section('WindowsPaths')
                config.set('WindowsPaths', 'storage_path',
                           os.path.join(appdata, 'Cursor', 'User', 'globalStorage', 'storage.json'))
                config.set('WindowsPaths', 'sqlite_path',
                           os.path.join(appdata, 'Cursor', 'User', 'globalStorage', 'state.vscdb'))

            self.db_path = config.get('WindowsPaths', 'storage_path')
            self.sqlite_path = config.get('WindowsPaths', 'sqlite_path')

        elif sys.platform == 'darwin':
            if not config.has_section('MacPaths'):
                config.add_section('MacPaths')
                config.set('MacPaths', 'storage_path',
                           os.path.abspath(os.path.expanduser('~/Library/Application Support/Cursor/User/globalStorage/storage.json')))
                config.set('MacPaths', 'sqlite_path',
                           os.path.abspath(os.path.expanduser('~/Library/Application Support/Cursor/User/globalStorage/state.vscdb')))

            self.db_path = config.get('MacPaths', 'storage_path')
            self.sqlite_path = config.get('MacPaths', 'sqlite_path')

        elif sys.platform == 'linux':
            if not config.has_section('LinuxPaths'):
                sudo_user = os.environ.get('SUDO_USER')
                if sudo_user:
                    actual_home = f'/home/{sudo_user}'
                else:
                    actual_home = os.path.expanduser('~')

                config.set('LinuxPaths', 'storage_path',
                           os.path.abspath(os.path.join(actual_home, '.config/cursor/User/globalStorage/storage.json')))
                config.set('LinuxPaths', 'sqlite_path',
                           os.path.abspath(os.path.join(actual_home, '.config/cursor/User/globalStorage/state.vscdb')))

            self.db_path = config.get('LinuxPaths', 'storage_path')
            self.sqlite_path = config.get('LinuxPaths', 'sqlite_path')

        else:
            raise NotImplementedError(f'Not Supported OS: {sys.platform}')

        with open(config_file, 'w', encoding='utf-8') as f:
            config.write(f)

    def generate_new_ids(self):
        dev_device_id = str(uuid.uuid4())

        machine_id = hashlib.sha256(os.urandom(32)).hexdigest()

        mac_machine_id = hashlib.sha512(os.urandom(64)).hexdigest()

        sqm_id = '{' + str(uuid.uuid4()).upper() + '}'

        self.update_machine_id_file(dev_device_id)

        return {
            'telemetry.devDeviceId': dev_device_id,
            'telemetry.macMachineId': mac_machine_id,
            'telemetry.machineId': machine_id,
            'telemetry.sqmId': sqm_id,
            'storage.serviceMachineId': dev_device_id,
        }

    def update_sqlite_db(self, new_ids):
        try:
            print(f"{Fore.CYAN}{EMOJI['INFO']} {self.translator.get('reset.updating_sqlite')}...{Style.RESET_ALL}")

            conn = sqlite3.connect(self.sqlite_path)
            cursor = conn.cursor()

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ItemTable (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
            ''')

            updates = [(key, value) for key, value in new_ids.items()]

            for key, value in updates:
                cursor.execute('''
                    INSERT OR REPLACE INTO ItemTable (key, value) 
                    VALUES (?, ?)
                ''', (key, value))
                print(f"{EMOJI['INFO']} {Fore.CYAN} {self.translator.get('reset.updating_pair')}: {key}{Style.RESET_ALL}")

            conn.commit()
            conn.close()

            print(f"{Fore.GREEN}{EMOJI['SUCCESS']} {self.translator.get('reset.sqlite_success')}{Style.RESET_ALL}")
            return True
        except Exception as e:
            print(f"{Fore.RED}{EMOJI['ERROR']} {self.translator.get('reset.sqlite_error', error=str(e))}{Style.RESET_ALL}")
            return False

    def update_system_ids(self, new_ids):
        try:
            print(f"{Fore.CYAN}{EMOJI['INFO']} {self.translator.get('reset.updating_system_ids')}...{Style.RESET_ALL}")

            if sys.platform.startswith('win'):
                self._update_windows_machine_guid()
                self._update_windows_machine_id()
            elif sys.platform == 'darwin':
                self._update_macos_platform_uuid(new_ids)

            print(f"{Fore.GREEN}{EMOJI['SUCCESS']} {self.translator.get('reset.system_ids_updated')}{Style.RESET_ALL}")
            return True
        except Exception as e:
            print(f"{Fore.RED}{EMOJI['ERROR']} {self.translator.get('reset.system_ids_update_failed', error=str(e))}{Style.RESET_ALL}")
            return False

    def _update_windows_machine_guid(self):
        try:
            import winreg

            key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                'SOFTWARE\\Microsoft\\Cryptography',
                0,
                winreg.KEY_WRITE | winreg.KEY_WOW64_64KEY
            )

            new_guid = str(uuid.uuid4())

            winreg.SetValueEx(key, 'MachineGuid', 0, winreg.REG_SZ, new_guid)
            winreg.CloseKey(key)

            print(f"{Fore.GREEN}{EMOJI['SUCCESS']} {self.translator.get('reset.windows_machine_guid_updated')}{Style.RESET_ALL}")
            return None
        except PermissionError as e:
            print(f"{Fore.RED}{EMOJI['ERROR']} {self.translator.get('reset.permission_denied', error=str(e))}{Style.RESET_ALL}")
            raise
        except Exception as e:
            print(f"{Fore.RED}{EMOJI['ERROR']} {self.translator.get('reset.update_windows_machine_guid_failed', error=str(e))}{Style.RESET_ALL}")
            raise

    def _update_windows_machine_id(self):
        try:
            import winreg

            new_guid = '{' + str(uuid.uuid4()).upper() + '}'

            print(f"{Fore.CYAN}{EMOJI['INFO']} {self.translator.get('reset.new_machine_id')}: {new_guid}{Style.RESET_ALL}")

            try:
                key = winreg.OpenKey(
                    winreg.HKEY_LOCAL_MACHINE,
                    'SOFTWARE\\Microsoft\\SQMClient',
                    0,
                    winreg.KEY_WRITE | winreg.KEY_WOW64_64KEY
                )
            except FileNotFoundError:
                key = winreg.CreateKey(
                    winreg.HKEY_LOCAL_MACHINE,
                    'SOFTWARE\\Microsoft\\SQMClient'
                )

            winreg.SetValueEx(key, 'MachineId', 0, winreg.REG_SZ, new_guid)
            winreg.CloseKey(key)

            print(f"{Fore.GREEN}{EMOJI['SUCCESS']} {self.translator.get('reset.windows_machine_id_updated')}{Style.RESET_ALL}")
            return True
        except PermissionError:
            print(f"{Fore.RED}{EMOJI['ERROR']} {self.translator.get('reset.permission_denied')}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}{EMOJI['WARNING']} {self.translator.get('reset.run_as_admin')}{Style.RESET_ALL}")
            return False
        except Exception as e:
            print(f"{Fore.RED}{EMOJI['ERROR']} {self.translator.get('reset.update_windows_machine_id_failed', error=str(e))}{Style.RESET_ALL}")
            return False

    def _update_macos_platform_uuid(self, new_ids):
        try:
            uuid_file = '/var/root/Library/Preferences/SystemConfiguration/com.apple.platform.uuid.plist'

            if os.path.exists(uuid_file):
                cmd = f'sudo plutil -replace "UUID" -string "{new_ids["telemetry.macMachineId"]}" "{uuid_file}"'
                result = os.system(cmd)

                if result == 0:
                    print(f"{Fore.GREEN}{EMOJI['SUCCESS']} {self.translator.get('reset.macos_platform_uuid_updated')}{Style.RESET_ALL}")
                    return None
                else:
                    raise Exception(f"{Fore.RED}{EMOJI['ERROR']} {self.translator.get('reset.failed_to_execute_plutil_command')}{Style.RESET_ALL}")

            return None
        except Exception as e:
            print(f"{Fore.RED}{EMOJI['ERROR']} {self.translator.get('reset.update_macos_platform_uuid_failed', error=str(e))}{Style.RESET_ALL}")
            raise

    def reset_machine_ids(self):
        try:
            print(f"{Fore.CYAN}{EMOJI['INFO']} {self.translator.get('reset.checking')}...{Style.RESET_ALL}")

            if not os.path.exists(self.db_path):
                print(f"{Fore.RED}{EMOJI['ERROR']} {self.translator.get('reset.not_found')}: {self.db_path}{Style.RESET_ALL}")
                return False

            if not os.access(self.db_path, os.R_OK | os.W_OK):
                print(f"{Fore.RED}{EMOJI['ERROR']} {self.translator.get('reset.no_permission')}{Style.RESET_ALL}")
                return False

            print(f"{Fore.CYAN}{EMOJI['FILE']} {self.translator.get('reset.reading')}...{Style.RESET_ALL}")

            with open(self.db_path, 'r', encoding='utf-8') as f:
                config = json.load(f)

            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = f"{self.db_path}.bak.{timestamp}"

            print(f"{Fore.YELLOW}{EMOJI['BACKUP']} {self.translator.get('reset.creating_backup')}: {backup_path}{Style.RESET_ALL}")
            shutil.copy2(self.db_path, backup_path)

            print(f"{Fore.CYAN}{EMOJI['RESET']} {self.translator.get('reset.generating')}...{Style.RESET_ALL}")
            new_ids = self.generate_new_ids()

            config.update(new_ids)

            print(f"{Fore.CYAN}{EMOJI['FILE']} {self.translator.get('reset.saving_json')}...{Style.RESET_ALL}")
            with open(self.db_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4)

            self.update_sqlite_db(new_ids)

            self.update_system_ids(new_ids)

            workbench_path = get_workbench_cursor_path(self.translator)
            modify_workbench_js(workbench_path, self.translator)

            greater_than_0_45 = check_cursor_version(self.translator)
            if greater_than_0_45:
                print(f"{Fore.CYAN}{EMOJI['INFO']} {self.translator.get('reset.detecting_version')} >= 0.45.0\uff0c{self.translator.get('reset.patching_getmachineid')}{Style.RESET_ALL}")
                patch_cursor_get_machine_id(self.translator)
            else:
                print(f"{Fore.YELLOW}{EMOJI['INFO']} {self.translator.get('reset.version_less_than_0_45')}{Style.RESET_ALL}")

            print(f"{Fore.GREEN}{EMOJI['SUCCESS']} {self.translator.get('reset.success')}{Style.RESET_ALL}")

            print(f"\n{Fore.CYAN}{self.translator.get('reset.new_id')}:{Style.RESET_ALL}")
            for key, value in new_ids.items():
                print(f"{EMOJI['INFO']} {key}: {Fore.GREEN}{value}{Style.RESET_ALL}")

            return True
        except PermissionError as e:
            print(f"{Fore.RED}{EMOJI['ERROR']} {self.translator.get('reset.permission_error', error=str(e))}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}{EMOJI['INFO']} {self.translator.get('reset.run_as_admin')}{Style.RESET_ALL}")
            return False
        except Exception as e:
            print(f"{Fore.RED}{EMOJI['ERROR']} {self.translator.get('reset.process_error', error=str(e))}{Style.RESET_ALL}")
            return False

    def update_machine_id_file(self, machine_id: str) -> bool:
        try:
            machine_id_path = get_cursor_machine_id_path()

            os.makedirs(os.path.dirname(machine_id_path), exist_ok=True)

            if os.path.exists(machine_id_path):
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                backup_path = f"{machine_id_path}.backup.{timestamp}"

                try:
                    shutil.copy2(machine_id_path, backup_path)
                    print(f"{Fore.GREEN}{EMOJI['INFO']} {'reset.backup_created' if not self.translator else self.translator.get('reset.backup_created', path=backup_path)}{Style.RESET_ALL}")
                except Exception as e:
                    print(f"{Fore.YELLOW}{EMOJI['INFO']} {'reset.backup_creation_failed' if not self.translator else self.translator.get('reset.backup_creation_failed', error=str(e))}{Style.RESET_ALL}")

            with open(machine_id_path, 'w', encoding='utf-8') as f:
                f.write(machine_id)

            print(f"{Fore.GREEN}{EMOJI['SUCCESS']} {'Successfully updated machineId file' if not self.translator else self.translator.get('reset.update_success')}{Style.RESET_ALL}")
            return True
        except Exception as e:
            error_msg = f'Failed to update machineId file: {str(e)}'
            if self.translator:
                error_msg = self.translator.get('reset.update_failed', error=str(e))
            print(f"{Fore.RED}{EMOJI['ERROR']} {error_msg}{Style.RESET_ALL}")
            return False


def run(translator=None):
    config = get_config(translator)

    if not config:
        return False

    print(f"\n{Fore.CYAN}{'=' * 50}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{EMOJI['RESET']} {translator.get('reset.title')}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'=' * 50}{Style.RESET_ALL}")

    resetter = MachineIDResetter(translator)
    resetter.reset_machine_ids()

    print(f"\n{Fore.CYAN}{'=' * 50}{Style.RESET_ALL}")
    input(f"{EMOJI['INFO']} {translator.get('reset.press_enter')}...")


if __name__ == '__main__':
    from main import translator as main_translator
    run(main_translator)
