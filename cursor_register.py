import os
from colorama import Fore, Style, init
import time
import random
from cursor_auth import CursorAuth
from reset_machine_manual import MachineIDResetter

os.environ['PYTHONVERBOSE'] = '0'
os.environ['PYINSTALLER_VERBOSE'] = '0'

init()

EMOJI = {
    'START': '🚀',
    'FORM': '📝',
    'VERIFY': '🔄',
    'PASSWORD': '🔑',
    'CODE': '📱',
    'DONE': '✨',
    'ERROR': '❌',
    'WAIT': '⏳',
    'SUCCESS': '✅',
    'MAIL': '📧',
    'KEY': '🔐',
    'UPDATE': '🔄',
    'INFO': 'ℹ️',
}


class CursorRegistration:

    def __init__(self, translator=None):
        self.translator = translator

        os.environ['BROWSER_HEADLESS'] = 'False'

        self.browser = None
        self.controller = None
        self.mail_url = 'https://yopmail.com/zh/email-generator'
        self.sign_up_url = 'https://authenticator.cursor.sh/sign-up'
        self.settings_url = 'https://www.cursor.com/settings'
        self.email_address = None
        self.signup_tab = None
        self.email_tab = None

        self.password = self._generate_password()

        first_name = random.choice([
            'James', 'John', 'Robert', 'Michael', 'William', 'David', 'Joseph', 'Thomas',
            'Emma', 'Olivia', 'Ava', 'Isabella', 'Sophia', 'Mia', 'Charlotte', 'Amelia',
            'Liam', 'Noah', 'Oliver', 'Elijah', 'Lucas', 'Mason', 'Logan', 'Alexander',
        ])
        self.last_name = random.choice([
            'Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis',
            'Anderson', 'Wilson', 'Taylor', 'Thomas', 'Moore', 'Martin', 'Jackson', 'Lee',
            'Thompson', 'White', 'Harris', 'Clark', 'Lewis', 'Walker', 'Hall', 'Young',
        ])

        new_first_letter = random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
        self.first_name = new_first_letter + first_name[1:]

        print(f'\n{Fore.CYAN}{EMOJI["PASSWORD"]} {self.translator.get("register.password")}: {self.password} {Style.RESET_ALL}')
        print(f'{Fore.CYAN}{EMOJI["FORM"]} {self.translator.get("register.first_name")}: {self.first_name} {Style.RESET_ALL}')
        print(f'{Fore.CYAN}{EMOJI["FORM"]} {self.translator.get("register.last_name")}: {self.last_name} {Style.RESET_ALL}')

    def _generate_password(self, length=12):
        chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*'
        return ''.join(random.choices(chars, k=length))

    def setup_email(self):
        try:
            print(f'{Fore.CYAN}{EMOJI["START"]} {self.translator.get("register.browser_start")}{Style.RESET_ALL}...')

            from new_tempemail import NewTempEmail
            self.temp_email = NewTempEmail(self.translator)

            email_address = self.temp_email.create_email()

            if not email_address:
                print(f'{Fore.RED}{EMOJI["ERROR"]} {self.translator.get("register.email_create_failed")}{Style.RESET_ALL}')
                return False

            self.email_address = email_address
            self.email_tab = self.temp_email

            return True
        except Exception as e:
            print(f'{Fore.RED}{EMOJI["ERROR"]} {self.translator.get("register.email_setup_failed", error=str(e))}{Style.RESET_ALL}')
            return False

    def register_cursor(self):
        browser_tab = None
        try:
            print(f'{Fore.CYAN}{EMOJI["START"]} {self.translator.get("register.register_start")}{Style.RESET_ALL}...')

            from new_signup import main as new_signup_main

            result, browser_tab = new_signup_main(
                email=self.email_address,
                password=self.password,
                first_name=self.first_name,
                last_name=self.last_name,
                email_tab=self.email_tab,
                controller=self.controller,
                translator=self.translator,
            )

            if result:
                self.signup_tab = browser_tab
                success = self._get_account_info()
            else:
                success = False

            return success
        except Exception as e:
            print(f'{Fore.RED}{EMOJI["ERROR"]} {self.translator.get("register.register_process_error", error=str(e))}{Style.RESET_ALL}')
            return False
        finally:
            if browser_tab:
                browser_tab.quit()

    def _get_account_info(self):
        try:
            self.signup_tab.get(self.settings_url)
            time.sleep(2)

            usage_selector = 'css:div.col-span-2 > div > div > div > div > div:nth-child(1) > div.flex.items-center.justify-between.gap-2 > span.font-mono.text-sm\\/\\[0\\.875rem\\]'
            usage_ele = self.signup_tab.ele(usage_selector)
            total_usage = '未知'
            if usage_ele:
                total_usage = usage_ele.text.split('/')[-1].strip()

            print(f'{Fore.CYAN}{EMOJI["INFO"]} {self.translator.get("register.total_usage", usage=total_usage)}{Style.RESET_ALL}')
            print(f'{Fore.CYAN}{EMOJI["WAIT"]} {self.translator.get("register.get_token")}{Style.RESET_ALL}...')

            max_attempts = 30
            retry_interval = 2
            attempts = 0

            while attempts < max_attempts:
                try:
                    cookies = self.signup_tab.cookies()
                    for cookie in cookies:
                        if cookie.get('name') == 'WorkosCursorSessionToken':
                            token = cookie['value'].split('%3A%3A')[1]
                            print(f'{Fore.GREEN}{EMOJI["SUCCESS"]} {self.translator.get("register.token_success")}{Style.RESET_ALL}')
                            self._save_account_info(token, total_usage)
                            return True

                    attempts += 1
                    if attempts < max_attempts:
                        print(f'{Fore.YELLOW}{EMOJI["WAIT"]} {self.translator.get("register.token_attempt", attempt=attempts, time=retry_interval)}{Style.RESET_ALL}')
                        time.sleep(retry_interval)
                except Exception:
                    attempts += 1
                    if attempts < max_attempts:
                        print(f'{Fore.YELLOW}{EMOJI["WAIT"]} {self.translator.get("register.token_attempt", attempt=attempts, time=retry_interval)}{Style.RESET_ALL}')
                        time.sleep(retry_interval)

            print(f'{Fore.RED}{EMOJI["ERROR"]} {self.translator.get("register.token_max_attempts", max=max_attempts)}{Style.RESET_ALL}')
            return False
        except Exception as e:
            print(f'{Fore.RED}{EMOJI["ERROR"]} {self.translator.get("register.token_failed", error=str(e))}{Style.RESET_ALL}')
            return False

    def _save_account_info(self, token, total_usage):
        try:
            print(f'{Fore.CYAN}{EMOJI["KEY"]} {self.translator.get("register.update_cursor_auth_info")}{Style.RESET_ALL}...')

            if self.update_cursor_auth(email=self.email_address, access_token=token, refresh_token=token):
                print(f'{Fore.GREEN}{EMOJI["SUCCESS"]} {self.translator.get("register.cursor_auth_info_updated")}{Style.RESET_ALL}...')
            else:
                print(f'{Fore.RED}{EMOJI["ERROR"]} {self.translator.get("register.cursor_auth_info_update_failed")}{Style.RESET_ALL}...')

            print(f'{Fore.CYAN}{EMOJI["UPDATE"]} {self.translator.get("register.reset_machine_id")}{Style.RESET_ALL}...')
            resetter = MachineIDResetter(self.translator)
            if not resetter.reset_machine_ids():
                raise Exception('Failed to reset machine ID')

            with open('cursor_accounts.txt', 'a', encoding='utf-8') as f:
                f.write(f'\n{"=" * 50}\n')
                f.write(f'Email: {self.email_address}\n')
                f.write(f'Password: {self.password}\n')
                f.write(f'Token: {token}\n')
                f.write(f'Usage Limit: {total_usage}\n')
                f.write(f'{"=" * 50}\n')

            print(f'{Fore.GREEN}{EMOJI["SUCCESS"]} {self.translator.get("register.account_info_saved")}{Style.RESET_ALL}...')
            return True
        except Exception as e:
            print(f'{Fore.RED}{EMOJI["ERROR"]} {self.translator.get("register.save_account_info_failed", error=str(e))}{Style.RESET_ALL}')
            return False

    def start(self):
        try:
            if self.setup_email():
                if self.register_cursor():
                    print(f'\n{Fore.GREEN}{EMOJI["DONE"]} {self.translator.get("register.cursor_registration_completed")}{Style.RESET_ALL}...')
                    if hasattr(self, 'temp_email'):
                        self.temp_email.close()
                    return True
            if hasattr(self, 'temp_email'):
                self.temp_email.close()
            return False
        finally:
            if hasattr(self, 'temp_email'):
                self.temp_email.close()

    def update_cursor_auth(self, email=None, access_token=None, refresh_token=None):
        auth_manager = CursorAuth(translator=self.translator)
        return auth_manager.update_auth(email, access_token, refresh_token)


def main(translator=None):
    print(f'\n{Fore.CYAN}{"=" * 50}{Style.RESET_ALL}')
    print(f'{Fore.CYAN}{EMOJI["START"]} {translator.get("register.title")}{Style.RESET_ALL}')
    print(f'{Fore.CYAN}{"=" * 50}{Style.RESET_ALL}')

    registration = CursorRegistration(translator)
    registration.start()

    print(f'\n{Fore.CYAN}{"=" * 50}{Style.RESET_ALL}')
    input(f'{EMOJI["INFO"]} {translator.get("register.press_enter")}{Style.RESET_ALL}...')


if __name__ == '__main__':
    from main import translator as main_translator
    main(main_translator)
