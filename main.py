import socketio
import json
import requests
from bs4 import BeautifulSoup
import sys
import time
import re

# Configuration
INBOX_ADDRESS = "tsuncca22@dayrep.com"
SOCKET_URL = "https://ws.fakemailgenerator.com/"
BASE_URL = "https://www.fakemailgenerator.com"

# Initialize Socket.io client
sio = socketio.Client()

def extract_activation_link(email_id, domain, recipient):
    """Fetches the email content and extracts the cutout.pro activation link."""
    # The actual content is inside an iframe with a specific URL structure
    content_url = f"{BASE_URL}/email/{domain}/{recipient}/message-{email_id}/"
    
    try:
        # Add a timeout and a user-agent to look like a real browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(content_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for links containing 'cutout.pro/resBackMsg'
            # The user specified /html/body/div[1]/div/a
            links = soup.find_all('a', href=True)
            for link in links:
                href = link['href']
                if 'cutout.pro/resBackMsg' in href:
                    return href
            
            # Fallback: search for the link pattern in the raw text if soup fails
            match = re.search(r'https://www\.cutout\.pro/resBackMsg\?type=2&token=[a-zA-Z0-9]+', response.text)
            if match:
                return match.group(0)
                
    except Exception as e:
        print(f"[!] Error fetching email content: {e}")
    
    return None

@sio.event
def connect():
    print(f"[*] Connected to {SOCKET_URL}")
    print(f"[*] Monitoring: {INBOX_ADDRESS}")
    # Join the channel for the specific email address
    sio.emit('watch_address', INBOX_ADDRESS.lower())

@sio.event
def disconnect():
    print("[!] Disconnected from server")

@sio.on("incoming_email")
def on_incoming_email(data):
    try:
        email = data
        if isinstance(data, str):
            try:
                email = json.loads(data)
            except:
                pass
            
        sender = email.get('sender', 'Unknown Sender')
        subject = email.get('subject', 'No Subject')
        email_id = email.get('emailid', 'N/A')
        domain = email.get('domain', 'N/A')
        recipient = email.get('recipient', 'N/A')
        
        print("\n" + "="*60)
        print(">>> NEW EMAIL RECEIVED <<<")
        print(f"From:    {sender}")
        print(f"Subject: {subject}")
        
        # Check if the email is from cutout.pro
        if 'cutout.pro' in sender.lower() or 'cutout.pro' in subject.lower():
            print("[*] Detecting cutout.pro email. Extracting activation link...")
            # Wait a second for the server to process the email content
            time.sleep(2)
            activation_link = extract_activation_link(email_id, domain, recipient)
            
            if activation_link:
                print(f"\033[92mACTIVATION LINK: {activation_link}\033[0m")
            else:
                print("[!] Could not find activation link in the email body.")
        
        if email_id != 'N/A':
            read_url = f"{BASE_URL}/inbox/{domain}/{recipient}/message-{email_id}/"
            print(f"Full Message: {read_url}")
            
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"[!] Error processing data: {e}")

def main():
    print("[*] Starting FakeMail Monitor with Link Extraction...")
    try:
        sio.connect(SOCKET_URL, transports=['websocket'])
        sio.wait()
    except KeyboardInterrupt:
        print("\n[*] Stopping monitor...")
        sio.disconnect()
    except Exception as e:
        print(f"[!] Connection error: {e}")

if __name__ == "__main__":
    main()
