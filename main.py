import socketio
import json
import sys
import time

# Configuration
INBOX_ADDRESS = "tsuncca22@dayrep.com"
SOCKET_URL = "https://ws.fakemailgenerator.com/"

# Initialize Socket.io client
sio = socketio.Client()

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
        # In python-socketio, data is usually already parsed if it's JSON
        # but let's be safe.
        email = data
        if isinstance(data, str):
            try:
                email = json.loads(data)
            except:
                pass
            
        print("\n" + "="*50)
        print(">>> NEW EMAIL RECEIVED <<<")
        
        # Display the email details
        sender = email.get('sender', 'Unknown Sender')
        subject = email.get('subject', 'No Subject')
        time_received = email.get('timeonly', 'N/A')
        email_id = email.get('emailid', 'N/A')
        domain = email.get('domain', 'N/A')
        recipient = email.get('recipient', 'N/A')
        
        print(f"From:    {sender}")
        print(f"Subject: {subject}")
        print(f"Time:    {time_received}")
        print(f"Full ID: {email_id}")
        
        # Construct the URL to read the full message
        if email_id != 'N/A' and domain != 'N/A' and recipient != 'N/A':
            read_url = f"https://www.fakemailgenerator.com/inbox/{domain}/{recipient}/message-{email_id}/"
            print(f"Link:    {read_url}")
            
        print("="*50 + "\n")
        
    except Exception as e:
        print(f"[!] Error processing data: {e}")
        print(f"Raw data: {data}")

def main():
    print("[*] Starting FakeMail Monitor...")
    try:
        # Use websocket transport for efficiency
        sio.connect(SOCKET_URL, transports=['websocket'])
        sio.wait()
    except KeyboardInterrupt:
        print("\n[*] Stopping monitor...")
        sio.disconnect()
    except Exception as e:
        print(f"[!] Connection error: {e}")

if __name__ == "__main__":
    main()
