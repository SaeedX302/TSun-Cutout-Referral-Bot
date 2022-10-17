# Cutout.pro Advanced Multi-Account Registration Bot

A high-performance Python automation tool designed to create a specific number of Cutout.pro accounts. It includes smart email checking, multi-invite loop persistence, and real-time WebSocket monitoring.

## 🚀 New & Advanced Features
- **Smart Email Check (api_0):** Before starting, the bot checks if the generated email already exists on Cutout.pro. If it does, it automatically skips it and tries a new one.
- **Guaranteed Invites:** If you ask for 3 invites, the bot will keep running until it successfully completes exactly 3 registrations, even if some attempts fail due to connection errors.
- **Improved Error Handling:** Clear, beautiful, and readable logs for connection errors or internet issues.
- **Auto-Suffixing:** Adds a random 4-digit numeric string to your prefix for every new account.
- **Dual Data Saving:**
  - `accounts.json`: Stores **Email**, **Password**, and **Timestamp**.
  - `activation_links.json`: Stores **Gmail** (recipient), **Link** (activation URL), and **Timestamp**.
- **Persistent Terminal:** Keeps the terminal window open after completion.

## 🛠️ Installation

### 1. Install Dependencies
You will need `python-socketio`, `requests`, and `beautifulsoup4`. Install them using pip:

```bash
pip install "python-socketio[client]" requests beautifulsoup4
```

## 📖 How to Use

### Run the Script
Start the bot by running:

```bash
python main.py
```

### Interactive Prompts
1. **Enter Prefix Name:** (e.g., `saeed`) - The bot will add 4 random numbers to this for every account.
2. **Enter Referral Code:** (e.g., `cutout_share-2091786`) - Your unique Cutout.pro referral ID.
3. **How many successful invites do you want?** (e.g., `3`) - The bot will work until it reaches this exact number of successes.

## 📊 Example Output
```text
=== CUTOUT.PRO ADVANCED AUTO-BOT ===
Enter Prefix Name: saeed
Enter Referral Code: cutout_share-2091786
How many successful invites do you want? 3
--------------------------------------------------
[*] Target: 3 Successful Registrations

[Attempt 1] Processing: saeed5749
[*] Checking if email exists (api_0)...
[!] Connection Error: Connection error
[-] Failed. Retrying with new prefix...
[*] Waiting 5 seconds for safety...

[Attempt 2] Processing: saeed6430
[*] Checking if email exists (api_0)...
[*] Connected to WebSocket. Watching: saeed6430@dayrep.com
[*] Sending Registration Request (api_1)...
[*] api_1 Response: {"code":0,"msg":"success"}
[*] Waiting for activation email...

!!!!!!!!!!!!!!!!!!!! EMAIL DETECTED !!!!!!!!!!!!!!!!!!!!
From: service@cutout.pro

SUCCESS! ACTIVATION LINK FOUND:
https://www.cutout.pro/resBackMsg?type=2&token=...

[*] Data saved to accounts.json and activation_links.json
[+] Progress: 1/3 Success
```

## 📁 Project Structure
- `main.py`: The main advanced automation script.
- `accounts.json`: Stores created account credentials.
- `activation_links.json`: Stores activation links for easy access.
- `README.md`: Project documentation.

---