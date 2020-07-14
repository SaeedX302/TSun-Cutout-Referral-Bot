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
SOCKET_URL = "https://ws.fakemailgenerator.com" 
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
    def __init__(self, prefix):
        self.prefix = prefix
        self.email = f"{prefix}@{DOMAIN}"
        self.sio = socketio.Client(reconnection=True, reconnection_attempts=5, reconnection_delay=2)
        self.found_link = False

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
        reg_url = REG_API_TEMPLATE.format(prefix=self.prefix, domain=DOMAIN, vsource=REFERRAL_CODE)
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
                    self.sio.disconnect()
                else:
                    log("[!] Email received but link extraction failed. Retrying in 5s...", Colors.WARNING)
                    time.sleep(5)
                    link = extract_activation_link(email.get('emailid'), DOMAIN, self.prefix)
                    if link:
                        log(f"\n{Colors.BOLD}{Colors.GREEN}SUCCESS (on retry)!:{Colors.ENDC}")
                        log(f"{Colors.BOLD}{link}{Colors.ENDC}\n")
                        self.found_link = True
                        self.sio.disconnect()
                    else:
                        log("[!] Link extraction failed again.", Colors.FAIL)
        except Exception as e:
            log(f"[!] Error in on_email: {e}", Colors.FAIL)

    def on_disconnect(self):
        if not self.found_link:
            log("[!] Disconnected before finding link.", Colors.WARNING)
        else:
            log("[*] Session Finished Successfully.", Colors.CYAN)

    def start(self):
        log(f"[*] Connecting to {SOCKET_URL}...", Colors.CYAN)
        try:
            self.sio.connect(SOCKET_URL, transports=['websocket', 'polling'], socketio_path='socket.io')
            start_time = time.time()
            while not self.found_link and (time.time() - start_time < 300):
                time.sleep(1)
            
            if not self.found_link:
                log("[!] Timeout: No email received within 5 minutes.", Colors.FAIL)
                
        except socketio.exceptions.ConnectionError as e:
            log(f"[!] Could not connect to the server: {e}", Colors.FAIL)
        except Exception as e:
            log(f"[!] An unexpected error occurred: {e}", Colors.FAIL)
        finally:
            if self.sio.connected:
                self.sio.disconnect()

if __name__ == "__main__":
    try:
        if len(sys.argv) > 1:
            target_prefix = sys.argv[1]
        else:
            target_prefix = generate_prefix()

        log(f"\n{Colors.HEADER}=== CUTOUT.PRO AUTO-REGISTRATION TOOL ==={Colors.ENDC}")
        log(f"Target Prefix: {Colors.BOLD}{target_prefix}{Colors.ENDC}")
        log(f"Referral:      {REFERRAL_CODE}")
        log("-" * 50)

        automator = CutoutAutomator(target_prefix)
        automator.start()
        
    except KeyboardInterrupt:
        log("\n[!] Interrupted by user.", Colors.FAIL)
    except Exception as e:
        log(f"\n[!] Fatal Error: {e}", Colors.FAIL)
    finally:
        # Keep the terminal open
        print("\n" + "-" * 50)
        input(f"{Colors.BOLD}Press ENTER to close the terminal...{Colors.ENDC}")
