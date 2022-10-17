# Cutout.pro Multi-Account Registration Bot

A powerful Python automation tool designed to create multiple Cutout.pro accounts using temporary email addresses. It leverages WebSockets for real-time email monitoring and automatically extracts activation links for every account created.

## 🚀 Key Features
- **Interactive Setup:** Prompts for your prefix, referral code, and number of invites upon startup.
- **Auto-Suffixing:** Automatically adds a random 4-digit numeric string to your prefix for every new account.
- **Multi-Account Loop:** Seamlessly creates multiple accounts in a single run.
- **Real-time Monitoring:** Uses Socket.io to listen for incoming emails instantly.
- **Dual Data Saving:**
  - `accounts.json`: Stores **Email**, **Password**, and **Timestamp**.
  - `activation_links.json`: Stores **Gmail** (recipient), **Link** (activation URL), and **Timestamp**.
- **Robust Connection:** Automatic reconnection and fallback transport methods (WebSockets/Polling).
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
1. **Enter Prefix Name:** (e.g., `tsuncca`) - The bot will add 4 random numbers to this for every account.
2. **Enter Referral Code:** (e.g., `cutout_share-2091786`) - Your unique Cutout.pro referral ID.
3. **How many invites do you want?** (e.g., `5`) - Enter the total number of accounts you want to create.

## 📊 Example Output
```text
=== CUTOUT.PRO MULTI-ACCOUNT BOT ===
Enter Prefix Name: tsuncca
Enter Referral Code: cutout_share-2091786
How many invites do you want? 3
--------------------------------------------------
[*] Starting 3 registrations...

[1/3] Processing: tsuncca4921
[*] Connected to WebSocket. Watching: tsuncca4921@dayrep.com
[*] Sending Registration Request (api_1)...
[*] api_1 Response: {"code":1,"msg":"success"}
[*] Waiting for activation email...

!!!!!!!!!!!!!!!!!!!! EMAIL DETECTED !!!!!!!!!!!!!!!!!!!!
From: service@cutout.pro

SUCCESS! ACTIVATION LINK FOUND:
https://www.cutout.pro/resBackMsg?type=2&token=...

[*] Data saved to accounts.json and activation_links.json
```

## 📁 Project Structure
- `main.py`: The main interactive automation script.
- `accounts.json`: Stores created account credentials.
- `activation_links.json`: Stores activation links for easy access.
- `README.md`: Project documentation.

## ⚠️ Important Notes
- **Input Validation:** The "invites" field only accepts numbers.
- **Safety:** The script includes a 2-minute timeout per account to prevent hanging.
- **Persistence:** All data is appended to the JSON files, so you never lose previous work.

---