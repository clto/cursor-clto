from DrissionPage import ChromiumOptions, ChromiumPage
import time
import os
import signal
import random
from colorama import Fore, Style
import configparser
from pathlib import Path
import sys
from config import get_config

_translator = None
_chrome_process_ids = []


def cleanup_chrome_processes(translator=None):
    """Clean only Chrome processes launched by this script"""
    if not _chrome_process_ids:
        print('\nNo Chrome processes to clean...')
        return

    print('\nCleaning Chrome processes launched by this script...')

    try:
        if os.name == 'nt':
            for pid in _chrome_process_ids:
                try:
                    os.system(f'taskkill /F /PID {pid} /T 2>nul')
                except Exception:
                    pass
        else:
            for pid in _chrome_process_ids:
                try:
                    os.kill(pid, signal.SIGTERM)
                except Exception:
                    pass
    except Exception as e:
        if translator:
            print(Fore.RED + '\u274c ' + translator.get('register.cleanup_error', error=str(e)) + Style.RESET_ALL)
        else:
            print(f'\u6e05\u7406\u8fdb\u7a0b\u65f6\u51fa\u9519: {e}')
        return

    _chrome_process_ids = []


def signal_handler(signum, frame):
    """Handle Ctrl+C signal"""
    if _translator:
        print(Fore.CYAN + _translator.get('register.exit_signal') + Style.RESET_ALL)
    else:
        print('\n\u6536\u5230\u9000\u51fa\u4fe1\u53f7\uff0c\u6b63\u5728\u5173\u95ed...')

    cleanup_chrome_processes(_translator)
    os._exit(0)


def simulate_human_input(page, url, config=None, translator=None):
    """Visit URL"""
    if translator:
        print(Fore.CYAN + '\U0001f680 ' + translator.get('register.visiting_url') + ': ' + url + Style.RESET_ALL)

    page.get('about:blank')
    time.sleep(get_random_wait_time(config, 'page_load_wait'))

    page.get(url)
    time.sleep(get_random_wait_time(config, 'page_load_wait'))


def fill_signup_form(page, first_name, last_name, email, config=None, translator=None):
    """Fill signup form"""
    try:
        if translator:
            print(Fore.CYAN + '\U0001f4e7 ' + translator.get('register.filling_form') + Style.RESET_ALL)
        else:
            print('\n\u6b63\u5728\u586b\u5199\u6ce8\u518c\u8868\u5355...')

        first_name_input = page.ele('@name=first_name')
        if first_name_input:
            first_name_input.input(first_name)
            time.sleep(get_random_wait_time(config, 'input_wait'))

        last_name_input = page.ele('@name=last_name')
        if last_name_input:
            last_name_input.input(last_name)
            time.sleep(get_random_wait_time(config, 'input_wait'))

        email_input = page.ele('@name=email')
        if email_input:
            email_input.input(email)
            time.sleep(get_random_wait_time(config, 'input_wait'))

        submit_button = page.ele('@type=submit')
        if submit_button:
            submit_button.click()
            time.sleep(get_random_wait_time(config, 'submit_wait'))

        if translator:
            print(Fore.GREEN + '\u2705 ' + translator.get('register.form_success') + Style.RESET_ALL)
        else:
            print('Form filled successfully')

        return True

    except Exception as e:
        if translator:
            print(Fore.RED + '\u274c ' + translator.get('register.form_error', error=str(e)) + Style.RESET_ALL)
        else:
            print(f'Error filling form: {e}')
        return False


def get_default_chrome_path():
    """Get default Chrome path"""
    if sys.platform == 'win32':
        paths = [
            os.path.join(os.environ.get('PROGRAMFILES', ''), 'Google/Chrome/Application/chrome.exe'),
            os.path.join(os.environ.get('PROGRAMFILES(X86)', ''), 'Google/Chrome/Application/chrome.exe'),
            os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Google/Chrome/Application/chrome.exe'),
        ]
    elif sys.platform == 'darwin':
        paths = ['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome']
    else:
        paths = ['/usr/bin/google-chrome', '/usr/bin/google-chrome-stable']

    for path in paths:
        if os.path.exists(path):
            return path

    return ''


def get_user_documents_path():
    """Get user Documents folder path"""
    if sys.platform == 'win32':
        return os.path.join(os.path.expanduser('~'), 'Documents')

    if sys.platform == 'darwin':
        return os.path.join(os.path.expanduser('~'), 'Documents')

    sudo_user = os.environ.get('SUDO_USER')
    if sudo_user:
        return os.path.join('/home', sudo_user, 'Documents')

    return os.path.join(os.path.expanduser('~'), 'Documents')


def get_random_wait_time(config=None, timing_type='page_load_wait'):
    """
    Get random wait time from config
    Args:
        config: ConfigParser object
        timing_type: Type of timing to get (page_load_wait, input_wait, submit_wait)
    Returns:
        float: Random wait time or fixed time
    """
    try:
        if not config.has_section('Timing'):
            return random.uniform(0.1, 0.8)

        if timing_type == 'random':
            min_time = float(config.get('Timing', 'min_random_time', fallback='0.1'))
            max_time = float(config.get('Timing', 'max_random_time', fallback='0.8'))
            return random.uniform(min_time, max_time)

        time_value = config.get('Timing', timing_type, fallback='0.1-0.8')

        if '-' not in time_value and ',' not in time_value:
            return float(time_value)

        min_time, max_time = map(float, time_value.split('-' if '-' in time_value else ','))
        return random.uniform(min_time, max_time)
    except:
        return random.uniform(0.1, 0.8)


def setup_driver(translator=None):
    """Setup browser driver"""
    try:
        config = get_config(translator)

        chrome_path = config.get('Chrome', 'chromepath', fallback=get_default_chrome_path())

        if not chrome_path or not os.path.exists(chrome_path):
            if translator:
                print(Fore.YELLOW + '\u26a0\ufe0f ' + translator.get('register.chrome_path_invalid') + Style.RESET_ALL)
            chrome_path = get_default_chrome_path()

        co = ChromiumOptions()
        co.set_browser_path(chrome_path)
        co.set_argument('--incognito')

        if sys.platform == 'linux':
            co.set_argument('--no-sandbox')

        co.auto_port()
        co.headless(False)

        try:
            extension_path = os.path.join(os.getcwd(), 'turnstilePatch')
            if os.path.exists(extension_path):
                co.set_argument('--allow-extensions-in-incognito')
                co.add_extension(extension_path)
        except Exception as e:
            if translator:
                print(Fore.RED + '\u274c ' + translator.get('register.extension_load_error', error=str(e)) + Style.RESET_ALL)
            else:
                print(f'Error loading extension: {e}')

        if translator:
            print(Fore.CYAN + '\U0001f680 ' + translator.get('register.starting_browser') + Style.RESET_ALL)
        else:
            print('Starting browser...')

        before_pids = []
        try:
            import psutil
            before_pids = [p.pid for p in psutil.process_iter() if 'chrome' in p.name().lower()]
        except:
            pass

        page = ChromiumPage(co)
        time.sleep(1)

        try:
            import psutil
            after_pids = [p.pid for p in psutil.process_iter() if 'chrome' in p.name().lower()]
            new_pids = [pid for pid in after_pids if pid not in before_pids]
            _chrome_process_ids.extend(new_pids)

            if _chrome_process_ids:
                print(f'Tracking {len(_chrome_process_ids)} Chrome processes')
            else:
                print(Fore.YELLOW + 'Warning: No new Chrome processes detected to track' + Style.RESET_ALL)
        except Exception as e:
            print('Warning: Could not track Chrome processes: ' + str(e))

        return config, page

    except Exception as e:
        if translator:
            print(Fore.RED + '\u274c ' + translator.get('register.browser_setup_error', error=str(e)) + Style.RESET_ALL)
        else:
            print(f'Error setting up browser: {e}')
        raise


def handle_turnstile(page, config=None, translator=None):
    """Handle Turnstile verification"""
    try:
        if translator:
            print(Fore.CYAN + '\U0001f504 ' + translator.get('register.handling_turnstile') + Style.RESET_ALL)
        else:
            print('\nHandling Turnstile verification...')

        turnstile_time = float(config.get('Turnstile', 'handle_turnstile_time', fallback='2'))
        random_time_str = config.get('Turnstile', 'handle_turnstile_random_time', fallback='1-3')

        try:
            min_time, max_time = map(float, random_time_str.split('-'))
        except:
            min_time, max_time = 1, 3

        max_retries = 2
        retry_count = 0

        while retry_count < max_retries:
            retry_count += 1

            if translator:
                print(Fore.CYAN + '\U0001f504 ' + translator.get('register.retry_verification', attempt=retry_count) + Style.RESET_ALL)
            else:
                print(f'Attempt {retry_count} of verification...')

            try:
                page.run_js('try { turnstile.reset() } catch(e) { }')
                time.sleep(turnstile_time)

                challenge_check = page.ele('@id=cf-turnstile', timeout=2).child().shadow_root.ele('tag:iframe').ele('tag:body').sr('tag:input')

                if challenge_check:
                    if translator:
                        print(Fore.CYAN + '\U0001f504 ' + translator.get('register.detect_turnstile') + Style.RESET_ALL)
                    else:
                        print('Detected verification box...')

                    time.sleep(random.uniform(min_time, max_time))
                    challenge_check.click()
                    time.sleep(turnstile_time)

                    if check_verification_success(page, translator):
                        if translator:
                            print(Fore.GREEN + '\u2705 ' + translator.get('register.verification_success') + Style.RESET_ALL)
                        else:
                            print('Verification successful!')
                        return True

                if check_verification_success(page, translator):
                    if translator:
                        print(Fore.GREEN + '\u2705 ' + translator.get('register.verification_success') + Style.RESET_ALL)
                    else:
                        print('Verification successful!')
                    return True

            except Exception as e:
                if translator:
                    print(Fore.RED + '\u274c ' + translator.get('register.verification_failed') + Style.RESET_ALL)
                else:
                    print('Verification attempt failed: ' + str(e))

            if check_verification_success(page, translator):
                if translator:
                    print(Fore.GREEN + '\u2705 ' + translator.get('register.verification_success') + Style.RESET_ALL)
                else:
                    print('Verification successful!')
                return True

            time.sleep(random.uniform(min_time, max_time))

        if translator:
            print(Fore.RED + '\u274c ' + translator.get('register.verification_failed') + Style.RESET_ALL)
        else:
            print('Exceeded maximum retry attempts')

        return False

    except Exception as e:
        if translator:
            print(Fore.RED + '\u274c ' + translator.get('register.verification_error', error=str(e)) + Style.RESET_ALL)
        else:
            print('Error in verification process: ' + str(e))
        return False


def check_verification_success(page, translator=None):
    """Check if verification is successful"""
    try:
        if page.ele('@name=password', timeout=0.5):
            return True

        if page.ele('@name=email', timeout=0.5):
            return True

        if page.ele('@data-index=0', timeout=0.5):
            return True

        if page.ele('Account Settings', timeout=0.5):
            return True

        error_messages = [
            'xpath://div[contains(text(), "Can\'t verify the user is human")]',
            'xpath://div[contains(text(), "Error: 600010")]',
            'xpath://div[contains(text(), "Please try again")]',
        ]

        for error_xpath in error_messages:
            if page.ele(error_xpath):
                return False

        return False

    except:
        return False


def generate_password(length=12):
    """Generate random password"""
    chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*'
    return ''.join(random.choices(chars, k=length))


def fill_password(page, password: str, config=None, translator=None):
    """
    Fill password form
    """
    try:
        print(Fore.CYAN + '\U0001f511 ' + (translator.get('register.setting_password') if translator else 'Setting password') + Style.RESET_ALL)

        password_input = page.ele('@name=password')

        print(Fore.CYAN + '\U0001f511 ' + translator.get('register.setting_on_password') + ': ' + password + Style.RESET_ALL)

        if password_input:
            password_input.input(password)

        submit_button = page.ele('@type=submit')
        if submit_button:
            submit_button.click()
            time.sleep(get_random_wait_time(config, 'submit_wait'))

        print(Fore.GREEN + '\u2705 ' + (translator.get('register.password_submitted') if translator else 'Password submitted') + Style.RESET_ALL)

        return True

    except Exception as e:
        if translator:
            print(Fore.RED + '\u274c ' + translator.get('register.password_error', error=str(e)) + Style.RESET_ALL)
        else:
            print(Fore.RED + '\u274c ' + 'Error setting password: ' + str(e) + Style.RESET_ALL)
        return False


def handle_verification_code(browser_tab, email_tab, controller, config=None, translator=None):
    """Handle verification code"""
    try:
        if translator:
            print('\n' + Fore.CYAN + '\U0001f504 ' + translator.get('register.waiting_for_verification_code') + Style.RESET_ALL)

        if hasattr(controller, 'get_verification_code') and email_tab is None:
            verification_code = controller.get_verification_code()

            if verification_code:
                for i, digit in enumerate(verification_code):
                    browser_tab.ele(f'@data-index={i}').input(digit)
                    time.sleep(get_random_wait_time(config, 'verification_code_input'))

                print(translator.get('register.verification_success'))
                time.sleep(get_random_wait_time(config, 'verification_success_wait'))

                if handle_turnstile(browser_tab, config, translator):
                    if translator:
                        print(Fore.GREEN + '\u2705 ' + translator.get('register.verification_success') + Style.RESET_ALL)
                    time.sleep(get_random_wait_time(config, 'verification_retry_wait'))

                    if translator:
                        print(Fore.CYAN + '\U0001f511 ' + translator.get('register.visiting_url') + ': https://www.cursor.com/settings' + Style.RESET_ALL)

                    browser_tab.get('https://www.cursor.com/settings')
                    time.sleep(get_random_wait_time(config, 'settings_page_load_wait'))
                    return (True, browser_tab)
                else:
                    return (False, None)
            else:
                return None

        if email_tab:
            print(Fore.CYAN + '\U0001f504 ' + translator.get('register.waiting_for_verification_code') + Style.RESET_ALL)

            time.sleep(get_random_wait_time(config, 'email_check_initial_wait'))
            email_tab.refresh_inbox()
            time.sleep(get_random_wait_time(config, 'email_refresh_wait'))

            if email_tab.check_for_cursor_email():
                verification_code = email_tab.get_verification_code()

                if verification_code:
                    for i, digit in enumerate(verification_code):
                        browser_tab.ele(f'@data-index={i}').input(digit)
                        time.sleep(get_random_wait_time(config, 'verification_code_input'))

                    if translator:
                        print(Fore.GREEN + '\u2705 ' + translator.get('register.verification_success') + Style.RESET_ALL)

                    time.sleep(get_random_wait_time(config, 'verification_success_wait'))

                    if handle_turnstile(browser_tab, config, translator):
                        if translator:
                            print(Fore.GREEN + '\u2705 ' + translator.get('register.verification_success') + Style.RESET_ALL)

                        time.sleep(get_random_wait_time(config, 'verification_retry_wait'))

                        if translator:
                            print(Fore.CYAN + '\U0001f511 ' + translator.get('register.visiting_url') + ': https://www.cursor.com/settings' + Style.RESET_ALL)

                        browser_tab.get('https://www.cursor.com/settings')
                        time.sleep(get_random_wait_time(config, 'settings_page_load_wait'))
                        return (True, browser_tab)
                    else:
                        if translator:
                            print(Fore.RED + '\u274c ' + translator.get('register.verification_failed') + Style.RESET_ALL)
                        else:
                            print('\u6700\u540e\u4e00\u6b21\u9a8c\u8bc1\u5931\u8d25')
                        return (False, None)

            verification_code = None
            max_attempts = 20
            retry_interval = get_random_wait_time(config, 'retry_interval')
            start_time = time.time()
            timeout = float(config.get('Timing', 'max_timeout', fallback='160'))

            if translator:
                print(Fore.CYAN + translator.get('register.start_getting_verification_code') + Style.RESET_ALL)

            for attempt in range(max_attempts):
                if time.time() - start_time > timeout:
                    if translator:
                        print(Fore.RED + '\u274c ' + translator.get('register.verification_timeout') + Style.RESET_ALL)
                    break

                verification_code = controller.get_verification_code()

                if verification_code:
                    if translator:
                        print(Fore.GREEN + '\u2705 ' + translator.get('register.verification_success') + Style.RESET_ALL)
                    break

                remaining_time = int(timeout - (time.time() - start_time))

                if translator:
                    print(Fore.CYAN + translator.get('register.try_get_code', attempt=attempt + 1, time=remaining_time) + Style.RESET_ALL)

                email_tab.refresh_inbox()
                time.sleep(retry_interval)

            if verification_code:
                for i, digit in enumerate(verification_code):
                    browser_tab.ele(f'@data-index={i}').input(digit)
                    time.sleep(get_random_wait_time(config, 'verification_code_input'))

                if translator:
                    print(Fore.GREEN + '\u2705 ' + translator.get('register.verification_success') + Style.RESET_ALL)

                time.sleep(get_random_wait_time(config, 'verification_success_wait'))

                if handle_turnstile(browser_tab, config, translator):
                    if translator:
                        print(Fore.GREEN + '\u2705 ' + translator.get('register.verification_success') + Style.RESET_ALL)

                    time.sleep(get_random_wait_time(config, 'verification_retry_wait'))

                    if translator:
                        print(Fore.CYAN + translator.get('register.visiting_url') + ': https://www.cursor.com/settings' + Style.RESET_ALL)

                    browser_tab.get('https://www.cursor.com/settings')
                    time.sleep(get_random_wait_time(config, 'settings_page_load_wait'))
                    return (True, browser_tab)
                else:
                    if translator:
                        print(Fore.RED + '\u274c ' + translator.get('register.verification_failed') + Style.RESET_ALL)
                    return (False, None)
            else:
                return (False, None)

        return None

    except Exception as e:
        if translator:
            print(Fore.RED + '\u274c ' + translator.get('register.verification_error', error=str(e)) + Style.RESET_ALL)
        return (False, None)


def handle_sign_in(browser_tab, email, password, translator=None):
    """Handle login process"""
    try:
        sign_in_header = browser_tab.ele('xpath://h1[contains(text(), "Sign in")]')

        if sign_in_header:
            pass
        else:
            return True

        print(Fore.CYAN + '\u68c0\u6d4b\u5230\u767b\u5f55\u9875\u9762\uff0c\u5f00\u59cb\u767b\u5f55...' + Style.RESET_ALL)

        email_input = browser_tab.ele('@name=email')

        if email_input:
            email_input.input(email)
            time.sleep(1)

            continue_button = browser_tab.ele('xpath://button[contains(@class, "BrandedButton") and text()="Continue"]')

            if continue_button:
                continue_button.click()
                time.sleep(2)

                if handle_turnstile(browser_tab, translator):
                    password_input = browser_tab.ele('@name=password')

                    if password_input:
                        password_input.input(password)
                        time.sleep(1)

                        sign_in_button = browser_tab.ele('xpath://button[@name="intent" and @value="password"]')

                        if sign_in_button:
                            sign_in_button.click()
                            time.sleep(2)

                            if handle_turnstile(browser_tab, translator):
                                print(Fore.GREEN + 'Login successful!' + Style.RESET_ALL)
                                time.sleep(3)
                                return True

        print(Fore.RED + 'Login failed' + Style.RESET_ALL)
        return False

    except Exception as e:
        print(Fore.RED + 'Login process error: ' + str(e) + Style.RESET_ALL)
        return False


def main(email=None, password=None, first_name=None, last_name=None, email_tab=None, controller=None, translator=None):
    """Main function, can receive account information, email tab, and translator"""
    global _translator, _chrome_process_ids
    _translator = translator
    _chrome_process_ids = []

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    page = None
    success = False

    try:
        config, page = setup_driver(translator)

        if translator:
            print(Fore.CYAN + '\U0001f680 ' + translator.get('register.browser_started') + Style.RESET_ALL)

        url = 'https://authenticator.cursor.sh/sign-up'

        simulate_human_input(page, url, config, translator)

        if translator:
            print(Fore.CYAN + '\U0001f504 ' + translator.get('register.waiting_for_page_load') + Style.RESET_ALL)

        time.sleep(get_random_wait_time(config, 'page_load_wait'))

        if not all([email, password, first_name, last_name]):
            first_name = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=6)).capitalize()
            last_name = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=6)).capitalize()
            email = f'{first_name.lower()}{random.randint(100, 999)}@example.com'
            password = generate_password()

            with open('test_accounts.txt', 'a', encoding='utf-8') as f:
                f.write('\n==================================================\n')
                f.write(f'Email: {email}\n')
                f.write(f'Password: {password}\n')
                f.write('==================================================\n')

        if fill_signup_form(page, first_name, last_name, email, config, translator):
            if translator:
                print('\n' + Fore.GREEN + '\u2705 ' + translator.get('register.form_submitted') + Style.RESET_ALL)

            if handle_turnstile(page, config, translator):
                if translator:
                    print('\n' + Fore.GREEN + '\u2705 ' + translator.get('register.first_verification_passed') + Style.RESET_ALL)

                if fill_password(page, password, config, translator):
                    if translator:
                        print('\n' + Fore.CYAN + '\U0001f504 ' + translator.get('register.waiting_for_second_verification') + Style.RESET_ALL)

                    if handle_turnstile(page, config, translator):
                        if translator:
                            print('\n' + Fore.CYAN + '\U0001f504 ' + translator.get('register.waiting_for_verification_code') + Style.RESET_ALL)

                        if handle_verification_code(page, email_tab, controller, config, translator):
                            success = True
                        else:
                            print('\n' + Fore.RED + '\u274c ' + (translator.get('register.verification_code_processing_failed') if translator else 'Verification code processing failed') + Style.RESET_ALL)
                    else:
                        print('\n' + Fore.RED + '\u274c ' + (translator.get('register.second_verification_failed') if translator else 'Second verification failed') + Style.RESET_ALL)
                else:
                    print('\n' + Fore.RED + '\u274c ' + (translator.get('register.second_verification_failed') if translator else 'Second verification failed') + Style.RESET_ALL)
            else:
                print('\n' + Fore.RED + '\u274c ' + (translator.get('register.first_verification_failed') if translator else 'First verification failed') + Style.RESET_ALL)

    except Exception as e:
        print(f'\u53d1\u751f\u9519\u8bef: {e}')

    if page and not success:
        page.quit()
        cleanup_chrome_processes(translator)

    if success:
        return (True, page)
    return (False, None)


if __name__ == '__main__':
    main()
