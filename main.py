import socketio
import json
import requests
from bs4 import BeautifulSoup
import time
import random
import string
import re
import sys

# --- CONFIGURATION ---
REFERRAL_CODE = "cutout_share-2091786"  # Your referral code
DOMAIN = "dayrep.com"
SOCKET_URL = "https://ws.fakemailgenerator.com/"
BASE_URL = "https://www.fakemailgenerator.com"
REG_API_TEMPLATE = "https://restapi.cutout.pro/user/registerByEmail2?email={prefix}%40{domain}&password={prefix}%40{domain}&vsource={vsource}"

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

def generate_prefix(length=8):
    """Generates a random alphanumeric prefix."""
    chars = string.ascii_lowercase + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

def extract_activation_link(email_id, domain, recipient):
    """Fetches the email content and extracts the cutout.pro activation link."""
    content_url = f"{BASE_URL}/email/{domain}/{recipient}/message-{email_id}/"
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(content_url, headers=headers, timeout=10)
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
    def __init__(self, prefix):
        self.prefix = prefix
        self.email = f"{prefix}@{DOMAIN}"
        self.sio = socketio.Client()
        self.found_link = False

        # Setup Socket Events
        self.sio.on('connect', self.on_connect)
        self.sio.on('incoming_email', self.on_email)
        self.sio.on('disconnect', self.on_disconnect)

    def on_connect(self):
        log(f"[*] Connected to WebSocket. Watching: {self.email}", Colors.CYAN)
        self.sio.emit('watch_address', self.email.lower())
        
        # Once connected, trigger the registration API
        self.trigger_registration()

    def trigger_registration(self):
        reg_url = REG_API_TEMPLATE.format(prefix=self.prefix, domain=DOMAIN, vsource=REFERRAL_CODE)
        log(f"[*] Sending Registration Request (api_1)...", Colors.BLUE)
        try:
            res = requests.get(reg_url, timeout=10)
            log(f"[*] api_1 Response: {res.text}", Colors.BLUE)
            log("[*] Waiting for activation email...", Colors.WARNING)
        except Exception as e:
            log(f"[!] api_1 Failed: {e}", Colors.FAIL)
            self.sio.disconnect()

    def on_email(self, data):
        try:
            email = data
            if isinstance(data, str): email = json.loads(data)
            
            sender = email.get('sender', '')
            if 'cutout.pro' in sender.lower():
                log("\n" + "!"*20 + " EMAIL DETECTED " + "!"*20, Colors.GREEN)
                log(f"From: {sender}", Colors.BOLD)
                
                # Give the server a moment to save the body
                time.sleep(2)
                link = extract_activation_link(email.get('emailid'), DOMAIN, self.prefix)
                
                if link:
                    log(f"\n{Colors.BOLD}{Colors.GREEN}SUCCESS! ACTIVATION LINK FOUND:{Colors.ENDC}")
                    log(f"{Colors.BOLD}{link}{Colors.ENDC}\n")
                    self.found_link = True
                    # Disconnect after finding the link
                    self.sio.disconnect()
                else:
                    log("[!] Email received but link extraction failed.", Colors.FAIL)
        except Exception as e:
            log(f"[!] Error in on_email: {e}", Colors.FAIL)

    def on_disconnect(self):
        log("[*] Session Finished.", Colors.CYAN)

    def start(self):
        try:
            self.sio.connect(SOCKET_URL, transports=['websocket'])
            # Wait until link is found or manual exit
            while not self.found_link:
                time.sleep(1)
        except KeyboardInterrupt:
            log("\n[!] Interrupted by user.", Colors.FAIL)
        finally:
            if self.sio.connected:
                self.sio.disconnect()

if __name__ == "__main__":
    # You can provide a prefix as an argument, or let it generate one
    if len(sys.argv) > 1:
        target_prefix = sys.argv[1]
    else:
        target_prefix = generate_prefix()

    log(f"\n{Colors.HEADER}=== CUTOUT.PRO AUTO-REGISTRATION TOOL ==={Colors.ENDC}")
    log(f"Target Prefix: {Colors.BOLD}{target_prefix}{Colors.ENDC}")
    log(f"Referral:      {REFERRAL_CODE}")
    log("-" * 40)

    automator = CutoutAutomator(target_prefix)
    automator.start()
