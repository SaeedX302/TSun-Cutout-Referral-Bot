## How to Use the Script
### Install Dependencies:
You need the You'll need python-socketio, requests, and beautifulsoup4 library

### Run this command in your terminal

    pip install "python-socketio[client]" requests beautifulsoup4

### Run the Script
### To use a random prefix:
    python main.py
### To use a specific prefix
    python main.py your_prefix_here

## Example Output

### When an email arrives from cutout.pro, you will see
```============================================================
>NEW EMAIL RECEIVED <<

> From:    service@cutout.pro

> Subject: Activate your cutout.pro account [*] Detecting cutout.pro email. Extracting activation link...

> ACTIVATION LINK: https://www.cutout.pro/resBackMsg...

> Full Msg: https://www.fakemailgenerator.com/inbox/dayre...
============================================================
```
## New Features Included
**One at a time:** It handles one registration per run to ensure reliability.

**Beautiful Logs:** It uses colors to distinguish between connection status, registration responses, and the final link.

***Referral Integration:*** Your referral code cutout_share-2091786 is already hardcoded into the script.