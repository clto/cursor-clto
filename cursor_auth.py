import sqlite3
import os
import sys
from colorama import Fore, Style, init
from config import get_config

init()

EMOJI = {
    'DB': '\U0001f5c4\ufe0f',
    'UPDATE': '\U0001f504',
    'SUCCESS': '\u2705',
    'ERROR': '\u274c',
    'WARN': '\u26a0\ufe0f',
    'INFO': '\u2139\ufe0f',
    'FILE': '\U0001f4c4',
    'KEY': '\U0001f510',
}


class CursorAuth:
    __static_attributes__ = ('conn', 'db_path', 'translator')

    def __init__(self, translator=None):
        self.translator = translator

        config = get_config(translator)
        if not config:
            print(
                f"{Fore.RED}{EMOJI['ERROR']} "
                f"{self.translator.get('auth.config_error') if self.translator else 'Failed to load configuration'}"
                f"{Style.RESET_ALL}"
            )
            sys.exit(1)

        try:
            if sys.platform == 'win32':
                if not config.has_section('WindowsPaths'):
                    raise ValueError('Windows paths not configured')
                self.db_path = config.get('WindowsPaths', 'sqlite_path')
            elif sys.platform == 'linux':
                if not config.has_section('LinuxPaths'):
                    raise ValueError('Linux paths not configured')
                self.db_path = config.get('LinuxPaths', 'sqlite_path')
            elif sys.platform == 'darwin':
                if not config.has_section('MacPaths'):
                    raise ValueError('macOS paths not configured')
                self.db_path = config.get('MacPaths', 'sqlite_path')
            else:
                print(
                    f"{Fore.RED}{EMOJI['ERROR']} "
                    f"{self.translator.get('auth.unsupported_platform') if self.translator else 'Unsupported platform'}"
                    f"{Style.RESET_ALL}"
                )
                sys.exit(1)

            if not os.path.exists(os.path.dirname(self.db_path)):
                raise FileNotFoundError(f'Database directory not found: {os.path.dirname(self.db_path)}')

            if not os.path.exists(self.db_path):
                print(
                    f"{Fore.RED}{EMOJI['ERROR']} "
                    f"{self.translator.get('auth.db_not_found', path=self.db_path)}"
                    f"{Style.RESET_ALL}"
                )
                return None

            if not os.access(self.db_path, os.R_OK | os.W_OK):
                print(
                    f"{Fore.RED}{EMOJI['ERROR']} "
                    f"{self.translator.get('auth.db_permission_error')}"
                    f"{Style.RESET_ALL}"
                )
                return None

            try:
                self.conn = sqlite3.connect(self.db_path)
                print(
                    f"{Fore.GREEN}{EMOJI['SUCCESS']} "
                    f"{self.translator.get('auth.connected_to_database')}"
                    f"{Style.RESET_ALL}"
                )
                return None
            except sqlite3.Error as e:
                print(
                    f"{Fore.RED}{EMOJI['ERROR']} "
                    f"{self.translator.get('auth.db_connection_error', error=str(e))}"
                    f"{Style.RESET_ALL}"
                )
                return None
        except Exception as e:
            print(
                f"{Fore.RED}{EMOJI['ERROR']} "
                f"{self.translator.get('auth.path_error', error=str(e)) if self.translator else 'Error getting database path: ' + str(e)}"
                f"{Style.RESET_ALL}"
            )
            sys.exit(1)

    def update_auth(self, email=None, access_token=None, refresh_token=None):
        conn = None

        try:
            db_dir = os.path.dirname(self.db_path)
            if not os.path.exists(db_dir):
                os.makedirs(db_dir, mode=493, exist_ok=True)

            if not os.path.exists(self.db_path):
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute(
                    '''
                    CREATE TABLE IF NOT EXISTS ItemTable (
                        key TEXT PRIMARY KEY,
                        value TEXT
                    )
                '''
                )
                conn.commit()
                if sys.platform != 'win32':
                    os.chmod(self.db_path, 420)
                conn.close()

            conn = sqlite3.connect(self.db_path)
            print(
                f"{EMOJI['INFO']} "
                f"{Fore.GREEN} "
                f"{self.translator.get('auth.connected_to_database')}"
                f"{Style.RESET_ALL}"
            )

            cursor = conn.cursor()

            conn.execute('PRAGMA busy_timeout = 5000')
            conn.execute('PRAGMA journal_mode = WAL')
            conn.execute('PRAGMA synchronous = NORMAL')

            updates = []
            updates.append(('cursorAuth/cachedSignUpType', 'Auth_0'))

            if email is not None:
                updates.append(('cursorAuth/cachedEmail', email))

            if access_token is not None:
                updates.append(('cursorAuth/accessToken', access_token))

            if refresh_token is not None:
                updates.append(('cursorAuth/refreshToken', refresh_token))

            cursor.execute('BEGIN TRANSACTION')

            try:
                for key, value in updates:
                    cursor.execute('SELECT COUNT(*) FROM ItemTable WHERE key = ?', (key,))
                    if cursor.fetchone()[0] == 0:
                        cursor.execute(
                            '''
                            INSERT INTO ItemTable (key, value) 
                            VALUES (?, ?)
                        ''',
                            (key, value),
                        )
                    else:
                        cursor.execute(
                            '''
                            UPDATE ItemTable SET value = ?
                            WHERE key = ?
                        ''',
                            (value, key),
                        )
                    print(
                        f"{EMOJI['INFO']} "
                        f"{Fore.CYAN} "
                        f"{self.translator.get('auth.updating_pair')} "
                        f"{key.split('/')[-1]}"
                        f"..."
                        f"{Style.RESET_ALL}"
                    )

                cursor.execute('COMMIT')
                print(
                    f"{EMOJI['SUCCESS']} "
                    f"{Fore.GREEN}"
                    f"{self.translator.get('auth.database_updated_successfully')}"
                    f"{Style.RESET_ALL}"
                )
            except Exception as e:
                cursor.execute('ROLLBACK')
                raise

            if conn:
                conn.close()
                print(
                    f"{EMOJI['DB']} "
                    f"{Fore.CYAN} "
                    f"{self.translator.get('auth.database_connection_closed')}"
                    f"{Style.RESET_ALL}"
                )
            return True
        except sqlite3.Error as e:
            print(
                f"\n{EMOJI['ERROR']} "
                f"{Fore.RED} "
                f"{self.translator.get('auth.database_error', error=str(e))}"
                f"{Style.RESET_ALL}"
            )
            if conn:
                conn.close()
                print(
                    f"{EMOJI['DB']} "
                    f"{Fore.CYAN} "
                    f"{self.translator.get('auth.database_connection_closed')}"
                    f"{Style.RESET_ALL}"
                )
            return False
        except Exception as e:
            print(
                f"\n{EMOJI['ERROR']} "
                f"{Fore.RED} "
                f"{self.translator.get('auth.an_error_occurred', error=str(e))}"
                f"{Style.RESET_ALL}"
            )
            if conn:
                conn.close()
                print(
                    f"{EMOJI['DB']} "
                    f"{Fore.CYAN} "
                    f"{self.translator.get('auth.database_connection_closed')}"
                    f"{Style.RESET_ALL}"
                )
            return False
