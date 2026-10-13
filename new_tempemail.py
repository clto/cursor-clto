from DrissionPage import ChromiumPage, ChromiumOptions
import time
import os
import sys
from colorama import Fore, Style, init
import requests
import random
import string
from utils import get_random_wait_time

init()


class NewTempEmail:
    def __init__(self, translator=None):
        self.translator = translator
        self.page = None
        self.setup_browser()

    def get_blocked_domains(self):
        """Get blocked domains list"""
        try:
            block_url = 'https://raw.githubusercontent.com/hovanhoa/cursor-free-vip/main/block_domain.txt'
            response = requests.get(block_url, timeout=5)
            if response.status_code == 200:
                domains = [line.strip() for line in response.text.split('\n') if line.strip()]
                if self.translator:
                    print(f"{Fore.CYAN}\u2139\ufe0f  {self.translator.get('email.blocked_domains_loaded', count=len(domains))}{Style.RESET_ALL}")
                else:
                    print(f"{Fore.CYAN}\u2139\ufe0f \u5df2\u52a0\u8f7d {len(domains)} \u4e2a\u88ab\u5c4f\u853d\u7684\u57df\u540d{Style.RESET_ALL}")
                return domains
            else:
                return self._load_local_blocked_domains()
        except Exception as e:
            if self.translator:
                print(f"{Fore.YELLOW}\u26a0\ufe0f {self.translator.get('email.blocked_domains_error', error=str(e))}{Style.RESET_ALL}")
            else:
                print(f"{Fore.YELLOW}\u26a0\ufe0f \u83b7\u53d6\u88ab\u5c4f\u853d\u57df\u540d\u5217\u8868\u5931\u8d25: {str(e)}{Style.RESET_ALL}")
            return self._load_local_blocked_domains()

    def _load_local_blocked_domains(self):
        """Load blocked domains from local file as fallback"""
        try:
            local_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'block_domain.txt')
            if os.path.exists(local_path):
                with open(local_path, 'r', encoding='utf-8') as f:
                    domains = [line.strip() for line in f.readlines() if line.strip()]
                if self.translator:
                    print(f"{Fore.CYAN}\u2139\ufe0f  {self.translator.get('email.local_blocked_domains_loaded', count=len(domains))}{Style.RESET_ALL}")
                else:
                    print(f"{Fore.CYAN}\u2139\ufe0f \u5df2\u4ece\u672c\u5730\u52a0\u8f7d {len(domains)} \u4e2a\u88ab\u5c4f\u853d\u7684\u57df\u540d{Style.RESET_ALL}")
                return domains
            else:
                if self.translator:
                    print(f"{Fore.YELLOW}\u26a0\ufe0f {self.translator.get('email.local_blocked_domains_not_found')}{Style.RESET_ALL}")
                else:
                    print(f"{Fore.YELLOW}\u26a0\ufe0f \u672c\u5730\u88ab\u5c4f\u853d\u57df\u540d\u6587\u4ef6\u4e0d\u5b58\u5728{Style.RESET_ALL}")
                return []
        except Exception as e:
            if self.translator:
                print(f"{Fore.YELLOW}\u26a0\ufe0f {self.translator.get('email.local_blocked_domains_error', error=str(e))}{Style.RESET_ALL}")
            else:
                print(f"{Fore.YELLOW}\u26a0\ufe0f \u8bfb\u53d6\u672c\u5730\u88ab\u5c4f\u853d\u57df\u540d\u6587\u4ef6\u5931\u8d25: {str(e)}{Style.RESET_ALL}")
            return []

    def exclude_blocked_domains(self, domains):
        """Exclude blocked domains"""
        if not self.blocked_domains:
            return domains
        filtered_domains = []
        for domain in domains:
            if domain['domain'] not in self.blocked_domains:
                filtered_domains.append(domain)
        excluded_count = len(domains) - len(filtered_domains)
        if excluded_count > 0:
            if self.translator:
                print(f"{Fore.YELLOW}\u26a0\ufe0f {self.translator.get('email.domains_excluded', domains=excluded_count)}{Style.RESET_ALL}")
            else:
                print(f"{Fore.YELLOW}\u26a0\ufe0f \u5df2\u6392\u9664 {excluded_count} \u4e2a\u88ab\u5c4f\u853d\u7684\u57df\u540d{Style.RESET_ALL}")
        return filtered_domains

    def get_extension_block(self):
        """\u83b7\u53d6\u63d2\u4ef6\u8def\u5f84"""
        root_dir = os.getcwd()
        extension_path = os.path.join(root_dir, 'PBlock')
        if hasattr(sys, '_MEIPASS'):
            extension_path = os.path.join(sys._MEIPASS, 'PBlock')
        if not os.path.exists(extension_path):
            raise FileNotFoundError(f'\u63d2\u4ef6\u4e0d\u5b58\u5728: {extension_path}')
        return extension_path

    def setup_browser(self):
        """\u8bbe\u7f6e\u6d4f\u89c8\u5668"""
        try:
            if self.translator:
                print(f"{Fore.CYAN}\u2139\ufe0f {self.translator.get('email.starting_browser')}{Style.RESET_ALL}")
            else:
                print(f"{Fore.CYAN}\u2139\ufe0f \u6b63\u5728\u542f\u52a8\u6d4f\u89c8\u5668...{Style.RESET_ALL}")

            co = ChromiumOptions()

            if not hasattr(self, 'auth_type') or self.auth_type != 'oauth':
                co.set_argument('--headless=new')

            if sys.platform == 'linux':
                if '--headless=new' not in co.arguments and not os.environ.get('DISPLAY'):
                    print(f"{Fore.RED}\u274c {self.translator.get('email.no_display_found') if self.translator else 'No display found. Make sure X server is running.'}{Style.RESET_ALL}")
                    print(f"{Fore.YELLOW}\u2139\ufe0f {self.translator.get('email.try_export_display') if self.translator else 'Try: export DISPLAY=:0'}{Style.RESET_ALL}")
                    return False
                co.set_argument('--no-sandbox')
                co.set_argument('--disable-dev-shm-usage')
                co.set_argument('--disable-gpu')
                if os.geteuid() == 0:
                    sudo_user = os.environ.get('SUDO_USER')
                    if sudo_user:
                        actual_home = f'/home/{sudo_user}'
                        user_data_dir = os.path.join(actual_home, '.config', 'google-chrome')
                        if os.path.exists(user_data_dir):
                            if self.translator:
                                print(f"{Fore.CYAN}\u2139\ufe0f {self.translator.get('email.using_chrome_profile', user_data_dir=user_data_dir)}{Style.RESET_ALL}")
                            else:
                                print(f"{Fore.CYAN}\u2139\ufe0f Using Chrome profile from: {user_data_dir}{Style.RESET_ALL}")
                            co.set_argument(f'--user-data-dir={user_data_dir}')

            co.auto_port()

            try:
                extension_path = self.get_extension_block()
                co.set_argument('--allow-extensions-in-incognito')
                co.add_extension(extension_path)
            except Exception as e:
                if self.translator:
                    print(f"{Fore.YELLOW}\u26a0\ufe0f {self.translator.get('email.extension_load_error')}: {str(e)}{Style.RESET_ALL}")
                else:
                    print(f"{Fore.YELLOW}\u26a0\ufe0f \u52a0\u8f7d\u63d2\u4ef6\u5931\u8d25: {str(e)}{Style.RESET_ALL}")

            self.page = ChromiumPage(co)
            return True
        except Exception as e:
            if self.translator:
                print(f"{Fore.RED}\u274c {self.translator.get('email.browser_start_error')}: {str(e)}{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}\u274c \u542f\u52a8\u6d4f\u89c8\u5668\u5931\u8d25: {str(e)}{Style.RESET_ALL}")
            if sys.platform == 'linux':
                print(f"{Fore.YELLOW}\u2139\ufe0f {self.translator.get('email.make_sure_chrome_chromium_is_properly_installed') if self.translator else 'Make sure Chrome/Chromium is properly installed'}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}\u2139\ufe0f {self.translator.get('email.try_install_chromium') if self.translator else 'Try: sudo apt install chromium-browser'}{Style.RESET_ALL}")
            return False

    def create_email(self):
        """create temporary email"""
        try:
            if self.translator:
                print(f"{Fore.CYAN}\u2139\ufe0f {self.translator.get('email.visiting_site')}{Style.RESET_ALL}")
            else:
                print(f"{Fore.CYAN}\u2139\ufe0f \u6b63\u5728\u8bbf\u95ee smailpro.com...{Style.RESET_ALL}")

            self.blocked_domains = self.get_blocked_domains()

            self.page.get('https://smailpro.com/')
            time.sleep(2)

            create_button = self.page.ele('xpath://button[@title="Create temporary email"]')
            if create_button:
                create_button.click()
                time.sleep(1)

                modal_create_button = self.page.ele('xpath://button[contains(text(), "Create")]')
                if modal_create_button:
                    modal_create_button.click()
                    time.sleep(2)

                    email_div = self.page.ele('xpath://div[@class="text-base sm:text-lg md:text-xl text-gray-700"]')
                    if email_div:
                        email = email_div.text.strip()
                        if '@' in email:
                            domain = email.split('@')[1]
                            if self.blocked_domains and domain in self.blocked_domains:
                                if self.translator:
                                    print(f"{Fore.YELLOW}\u26a0\ufe0f {self.translator.get('email.domain_blocked')}: {domain}{Style.RESET_ALL}")
                                else:
                                    print(f"{Fore.YELLOW}\u26a0\ufe0f \u57df\u540d\u5df2\u88ab\u5c4f\u853d: {domain}\uff0c\u5c1d\u8bd5\u91cd\u65b0\u521b\u5efa\u90ae\u7bb1{Style.RESET_ALL}")
                                return self.create_email()
                            if self.translator:
                                print(f"{Fore.GREEN}\u2705 {self.translator.get('email.create_success')}: {email}{Style.RESET_ALL}")
                            else:
                                print(f"{Fore.GREEN}\u2705 \u521b\u5efa\u90ae\u7bb1\u6210\u529f: {email}{Style.RESET_ALL}")
                            return email

            if self.translator:
                print(f"{Fore.RED}\u274c {self.translator.get('email.create_failed')}{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}\u274c \u521b\u5efa\u90ae\u7bb1\u5931\u8d25{Style.RESET_ALL}")
            return None
        except Exception as e:
            if self.translator:
                print(f"{Fore.RED}\u274c {self.translator.get('email.create_error')}: {str(e)}{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}\u274c \u521b\u5efa\u90ae\u7bb1\u51fa\u9519: {str(e)}{Style.RESET_ALL}")
            return None

    def close(self):
        """close browser"""
        if self.page:
            self.page.quit()

    def refresh_inbox(self):
        """refresh inbox"""
        try:
            if self.translator:
                print(f"{Fore.CYAN}\U0001f504 {self.translator.get('email.refreshing')}{Style.RESET_ALL}")
            else:
                print(f"{Fore.CYAN}\U0001f504 \u6b63\u5728\u5237\u65b0\u90ae\u7bb1...{Style.RESET_ALL}")

            refresh_button = self.page.ele('xpath://button[@id="refresh"]')
            if refresh_button:
                refresh_button.click()
                time.sleep(2)
                if self.translator:
                    print(f"{Fore.GREEN}\u2705 {self.translator.get('email.refresh_success')}{Style.RESET_ALL}")
                else:
                    print(f"{Fore.GREEN}\u2705 \u90ae\u7bb1\u5237\u65b0\u6210\u529f{Style.RESET_ALL}")
                return True
            else:
                if self.translator:
                    print(f"{Fore.RED}\u274c {self.translator.get('email.refresh_button_not_found')}{Style.RESET_ALL}")
                else:
                    print(f"{Fore.RED}\u274c \u672a\u627e\u5230\u5237\u65b0\u6309\u94ae{Style.RESET_ALL}")
                return False
        except Exception as e:
            if self.translator:
                print(f"{Fore.RED}\u274c {self.translator.get('email.refresh_error')}: {str(e)}{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}\u274c \u5237\u65b0\u90ae\u7bb1\u51fa\u9519: {str(e)}{Style.RESET_ALL}")
            return False

    def check_for_cursor_email(self):
        """\u68c0\u67e5\u662f\u5426\u6709 Cursor \u7684\u9a8c\u8bc1\u90ae\u4ef6"""
        try:
            email_div = self.page.ele('xpath://div[contains(@class, "p-2") and contains(@class, "cursor-pointer") and contains(@class, "bg-white") and contains(@class, "shadow") and .//b[text()="no-reply@cursor.sh"] and .//span[text()="Verify your email address"]]')
            if email_div:
                if self.translator:
                    print(f"{Fore.GREEN}\u2705 {self.translator.get('email.verification_found')}{Style.RESET_ALL}")
                else:
                    print(f"{Fore.GREEN}\u2705 \u627e\u5230\u9a8c\u8bc1\u90ae\u4ef6{Style.RESET_ALL}")
                self.page.run_js('arguments[0].click()', email_div)
                time.sleep(2)
                return True
            else:
                if self.translator:
                    print(f"{Fore.YELLOW}\u26a0\ufe0f {self.translator.get('email.verification_not_found')}{Style.RESET_ALL}")
                else:
                    print(f"{Fore.YELLOW}\u26a0\ufe0f \u672a\u627e\u5230\u9a8c\u8bc1\u90ae\u4ef6{Style.RESET_ALL}")
                return False
        except Exception as e:
            if self.translator:
                print(f"{Fore.RED}\u274c {self.translator.get('email.verification_error')}: {str(e)}{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}\u274c \u68c0\u67e5\u9a8c\u8bc1\u90ae\u4ef6\u51fa\u9519: {str(e)}{Style.RESET_ALL}")
            return False

    def get_verification_code(self):
        """\u83b7\u53d6\u9a8c\u8bc1\u7801"""
        try:
            code_element = self.page.ele('xpath://td//div[contains(@style, "font-size:28px") and contains(@style, "letter-spacing:2px")]')
            if code_element:
                code = code_element.text.strip()
                if code.isdigit() and len(code) == 6:
                    if self.translator:
                        print(f"{Fore.GREEN}\u2705 {self.translator.get('email.verification_code_found')}: {code}{Style.RESET_ALL}")
                    else:
                        print(f"{Fore.GREEN}\u2705 \u83b7\u53d6\u9a8c\u8bc1\u7801\u6210\u529f: {code}{Style.RESET_ALL}")
                    return code
            if self.translator:
                print(f"{Fore.YELLOW}\u26a0\ufe0f {self.translator.get('email.verification_code_not_found')}{Style.RESET_ALL}")
            else:
                print(f"{Fore.YELLOW}\u26a0\ufe0f \u672a\u627e\u5230\u6709\u6548\u7684\u9a8c\u8bc1\u7801{Style.RESET_ALL}")
            return None
        except Exception as e:
            if self.translator:
                print(f"{Fore.RED}\u274c {self.translator.get('email.verification_code_error')}: {str(e)}{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}\u274c \u83b7\u53d6\u9a8c\u8bc1\u7801\u51fa\u9519: {str(e)}{Style.RESET_ALL}")
            return None


def main(translator=None):
    temp_email = NewTempEmail(translator)
    try:
        email = temp_email.create_email()
        if email:
            if translator:
                print(f"\n{Fore.CYAN}\U0001f4e7 {translator.get('email.address')}: {email}{Style.RESET_ALL}")
            else:
                print(f"\n{Fore.CYAN}\U0001f4e7 \u4e34\u65f6\u90ae\u7bb1\u5730\u5740: {email}{Style.RESET_ALL}")

            while True:
                if translator:
                    choice = input(f"\n{translator.get('email.refresh_prompt')}: ").lower()
                else:
                    choice = input('\n\u6309 R \u5237\u65b0\u90ae\u7bb1\uff0c\u6309 Q \u9000\u51fa: ').lower()

                if choice == 'r':
                    temp_email.refresh_inbox()
                elif choice == 'q':
                    break
    finally:
        temp_email.close()


if __name__ == '__main__':
    main()
