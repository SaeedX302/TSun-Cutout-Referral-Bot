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
            # Fallback regex
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
        self.sio = socketio.Client(reconnection=True, reconnection_attempts=5, reconnection_delay=2)
        self.found_link = False
        self.activation_link = None

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
        log(f"[!] Connection Error: {data}", Colors.FAIL)

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
                    
                    # Save account details
                    save_to_json(ACCOUNTS_FILE, {
                        "email": self.email,
                        "password": self.password,
                        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                    })
                    
                    # Save activation link details
                    save_to_json(LINKS_FILE, {
                        "gmail": self.email,
                        "link": link,
                        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                    })
                    
                    log(f"[*] Data saved to {ACCOUNTS_FILE} and {LINKS_FILE}", Colors.GREEN)
                    self.sio.disconnect()
                else:
                    log("[!] Email received but link extraction failed. Retrying in 5s...", Colors.WARNING)
                    time.sleep(5)
                    link = extract_activation_link(email.get('emailid'), DOMAIN, self.prefix)
                    if link:
                        self.found_link = True
                        self.activation_link = link
                        save_to_json(ACCOUNTS_FILE, {"email": self.email, "password": self.password, "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")})
                        save_to_json(LINKS_FILE, {"gmail": self.email, "link": link, "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")})
                        self.sio.disconnect()
        except Exception as e:
            log(f"[!] Error in on_email: {e}", Colors.FAIL)

    def on_disconnect(self):
        if self.found_link:
            log("[*] Registration Successful.", Colors.CYAN)
        else:
            log("[!] Disconnected.", Colors.WARNING)

    def start(self):
        try:
            self.sio.connect(SOCKET_URL, transports=['websocket', 'polling'], socketio_path='socket.io')
            start_time = time.time()
            # Wait for link or 2-minute timeout per account
            while not self.found_link and (time.time() - start_time < 120):
                time.sleep(1)
            
            if not self.found_link:
                log("[!] Timeout: No email received for this account.", Colors.FAIL)
                
        except Exception as e:
            log(f"[!] Error: {e}", Colors.FAIL)
        finally:
            if self.sio.connected:
                self.sio.disconnect()
        return self.found_link

def main():
    try:
        log(f"\n{Colors.HEADER}=== CUTOUT.PRO MULTI-ACCOUNT BOT ==={Colors.ENDC}")
        
        # 1. Ask for prefix
        base_prefix = input(f"{Colors.BOLD}Enter Prefix Name: {Colors.ENDC}").strip()
        if not base_prefix:
            base_prefix = "user"
            
        # 2. Ask for Referral Code
        ref_code = input(f"{Colors.BOLD}Enter Referral Code: {Colors.ENDC}").strip()
        if not ref_code:
            ref_code = "cutout_share-2091786"
            
        # 3. Ask for number of invites
        while True:
            invites_str = input(f"{Colors.BOLD}How many invites do you want? {Colors.ENDC}").strip()
            if invites_str.isdigit():
                num_invites = int(invites_str)
                break
            else:
                log("[!] Please enter a valid number.", Colors.FAIL)

        log("-" * 50)
        log(f"[*] Starting {num_invites} registrations...", Colors.WARNING)
        
        success_count = 0
        for i in range(num_invites):
            current_prefix = f"{base_prefix}{generate_random_suffix()}"
            log(f"\n[{i+1}/{num_invites}] Processing: {current_prefix}", Colors.HEADER)
            
            automator = CutoutAutomator(current_prefix, ref_code)
            if automator.start():
                success_count += 1
            
            # Small delay between accounts
            if i < num_invites - 1:
                log("[*] Waiting 5 seconds before next account...", Colors.CYAN)
                time.sleep(5)

        log("\n" + "=" * 50)
        log(f"COMPLETED! Successfully created {success_count}/{num_invites} accounts.", Colors.GREEN)
        
    except KeyboardInterrupt:
        log("\n[!] Bot stopped by user.", Colors.FAIL)
    except Exception as e:
        log(f"\n[!] Fatal Error: {e}", Colors.FAIL)
    finally:
        print("\n" + "-" * 50)
        input(f"{Colors.BOLD}Press ENTER to close the terminal...{Colors.ENDC}")

if __name__ == "__main__":
    main()
