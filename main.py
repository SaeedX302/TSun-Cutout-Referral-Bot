import socketio
import json
import requests
from bs4 import BeautifulSoup
import time
import random
import string
import re
import sys
import os

# --- CONFIGURATION ---
DOMAIN = "dayrep.com"
SOCKET_URL = "https://ws.fakemailgenerator.com" 
BASE_URL = "https://www.fakemailgenerator.com"
CHECK_EMAIL_API = "https://restapi.cutout.pro/user/checkEmail?email={prefix}%40{domain}"
REG_API_TEMPLATE = "https://restapi.cutout.pro/user/registerByEmail2?email={prefix}%40{domain}&password={prefix}%40{domain}&vsource={vsource}"
ACCOUNTS_FILE = "accounts.json"
LINKS_FILE = "activation_links.json"

# Colors for pretty logging
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def log(msg, color=Colors.ENDC):
    print(f"{color}{msg}{Colors.ENDC}")

# --- LOGIC ---

def generate_random_suffix(length=4):
    """Generates a random numeric suffix."""
    return ''.join(random.choice(string.digits) for _ in range(length))

def save_to_json(file_path, new_data):
    """Generic function to save data to a JSON file (list of dicts)."""
    data = []
    if os.path.exists(file_path):
        try:
            with open(file_path, "r") as f:
                data = json.load(f)
                if not isinstance(data, list):
                    data = []
        except (json.JSONDecodeError, IOError):
            data = []
            
    data.append(new_data)
    
    try:
        with open(file_path, "w") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        log(f"[!] Error saving to {file_path}: {e}", Colors.FAIL)

def check_email_exists(prefix):
    """API_0: Checks if the email is already registered on Cutout.pro."""
    url = CHECK_EMAIL_API.format(prefix=prefix, domain=DOMAIN)
    try:
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            data = res.json()
            # Code 2002 means email is already used
            if data.get("code") == 2002:
                return True
    except Exception:
        pass
    return False

def extract_activation_link(email_id, domain, recipient):
    """Fetches the email content and extracts the cutout.pro activation link."""
    content_url = f"{BASE_URL}/email/{domain}/{recipient}/message-{email_id}/"
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(content_url, headers=headers, timeout=15)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            links = soup.find_all('a', href=True)
            for link in links:
                if 'cutout.pro/resBackMsg' in link['href']:
                    return link['href']
            match = re.search(r'https://www\.cutout\.pro/resBackMsg\?type=2&token=[a-zA-Z0-9]+', response.text)
            if match: return match.group(0)
    except Exception as e:
        log(f"[!] Error fetching content: {e}", Colors.FAIL)
    return None

class CutoutAutomator:
    def __init__(self, prefix, referral_code):
        self.prefix = prefix
        self.referral_code = referral_code
        self.email = f"{prefix}@{DOMAIN}"
        self.password = f"{prefix}@{DOMAIN}"
        self.sio = socketio.Client(reconnection=True, reconnection_attempts=3, reconnection_delay=1)
        self.found_link = False
        self.activation_link = None
        self.error_occurred = False

        # Setup Socket Events
        self.sio.on('connect', self.on_connect)
        self.sio.on('incoming_email', self.on_email)
        self.sio.on('disconnect', self.on_disconnect)
        self.sio.on('connect_error', self.on_connect_error)

    def on_connect(self):
        log(f"[*] Connected to WebSocket. Watching: {self.email}", Colors.CYAN)
        self.sio.emit('watch_address', self.email.lower())
        time.sleep(1)
        self.trigger_registration()

    def on_connect_error(self, data):
        self.error_occurred = True
        log(f"[!] WebSocket Connection Error: {data}", Colors.FAIL)

    def trigger_registration(self):
        reg_url = REG_API_TEMPLATE.format(prefix=self.prefix, domain=DOMAIN, vsource=self.referral_code)
        log(f"[*] Sending Registration Request (api_1)...", Colors.BLUE)
        try:
            with requests.Session() as session:
                res = session.get(reg_url, timeout=15)
                log(f"[*] api_1 Response: {res.text}", Colors.BLUE)
                log("[*] Waiting for activation email...", Colors.WARNING)
        except Exception as e:
            log(f"[!] api_1 Failed: {e}", Colors.FAIL)
            self.error_occurred = True

    def on_email(self, data):
        try:
            email = data
            if isinstance(data, str): email = json.loads(data)
            sender = email.get('sender', '')
            if 'cutout.pro' in sender.lower():
                log("\n" + "!"*20 + " EMAIL DETECTED " + "!"*20, Colors.GREEN)
                log(f"From: {sender}", Colors.BOLD)
                time.sleep(3)
                link = extract_activation_link(email.get('emailid'), DOMAIN, self.prefix)
                if link:
                    log(f"\n{Colors.BOLD}{Colors.GREEN}SUCCESS! ACTIVATION LINK FOUND:{Colors.ENDC}")
                    log(f"{Colors.BOLD}{link}{Colors.ENDC}\n")
                    self.found_link = True
                    self.activation_link = link
                    save_to_json(ACCOUNTS_FILE, {"email": self.email, "password": self.password, "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")})
                    save_to_json(LINKS_FILE, {"gmail": self.email, "link": link, "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")})
                    log(f"[*] Data saved to {ACCOUNTS_FILE} and {LINKS_FILE}", Colors.GREEN)
                    self.sio.disconnect()
        except Exception as e:
            log(f"[!] Error in on_email: {e}", Colors.FAIL)

    def on_disconnect(self):
        pass

    def start(self):
        try:
            self.sio.connect(SOCKET_URL, transports=['websocket', 'polling'], socketio_path='socket.io')
            start_time = time.time()
            while not self.found_link and not self.error_occurred and (time.time() - start_time < 120):
                time.sleep(1)
            if not self.found_link and not self.error_occurred:
                log("[!] Timeout: No email received for this account.", Colors.FAIL)
        except Exception as e:
            log(f"[!] Connection Error: {e}", Colors.FAIL)
            self.error_occurred = True
        finally:
            if self.sio.connected:
                self.sio.disconnect()
        return self.found_link

def main():
    try:
        log(f"\n{Colors.HEADER}{Colors.BOLD}=== CUTOUT.PRO ADVANCED AUTO-BOT ==={Colors.ENDC}")
        
        base_prefix = input(f"{Colors.BOLD}Enter Prefix Name: {Colors.ENDC}").strip()
        if not base_prefix: base_prefix = "user"
            
        ref_code = input(f"{Colors.BOLD}Enter Referral Code: {Colors.ENDC}").strip()
        if not ref_code: ref_code = "cutout_share-2091786"
            
        while True:
            invites_str = input(f"{Colors.BOLD}How many successful invites do you want? {Colors.ENDC}").strip()
            if invites_str.isdigit():
                target_invites = int(invites_str)
                break
            else:
                log("[!] Please enter a valid number.", Colors.FAIL)

        log("-" * 50)
        log(f"[*] Target: {target_invites} Successful Registrations", Colors.WARNING)
        
        success_count = 0
        attempt_count = 0
        
        while success_count < target_invites:
            attempt_count += 1
            current_prefix = f"{base_prefix}{generate_random_suffix()}"
            
            log(f"\n{Colors.UNDERLINE}[Attempt {attempt_count}] Processing: {current_prefix}{Colors.ENDC}", Colors.HEADER)
            
            # API_0: Check if email exists
            log(f"[*] Checking if email exists (api_0)...", Colors.CYAN)
            if check_email_exists(current_prefix):
                log(f"[!] Email {current_prefix} already exists. Skipping...", Colors.WARNING)
                continue
            
            automator = CutoutAutomator(current_prefix, ref_code)
            if automator.start():
                success_count += 1
                log(f"{Colors.GREEN}[+] Progress: {success_count}/{target_invites} Success{Colors.ENDC}")
            else:
                log(f"{Colors.FAIL}[-] Failed. Retrying with new prefix...{Colors.ENDC}")
            
            if success_count < target_invites:
                log("[*] Waiting 5 seconds for safety...", Colors.CYAN)
                time.sleep(5)

        log("\n" + "=" * 50)
        log(f"{Colors.BOLD}{Colors.GREEN}COMPLETED! Target of {target_invites} accounts reached.{Colors.ENDC}", Colors.GREEN)
        log(f"Total attempts made: {attempt_count}")
        
    except KeyboardInterrupt:
        log("\n[!] Bot stopped by user.", Colors.FAIL)
    except Exception as e:
        log(f"\n[!] Fatal Error: {e}", Colors.FAIL)
    finally:
        print("\n" + "-" * 50)
        input(f"{Colors.BOLD}Press ENTER to close the terminal...{Colors.ENDC}")

if __name__ == "__main__":
    main()
