# Cutout.pro Auto-Registration Bot

A powerful Python automation tool designed to streamline the registration process for Cutout.pro using temporary email addresses. It leverages WebSockets for real-time email monitoring and automatically extracts activation links.

## 🚀 Key Features
- **Real-time Monitoring:** Uses Socket.io to listen for incoming emails instantly without refreshing.
- **Automated Registration:** Calls the Cutout.pro API automatically with a random or specific prefix.
- **Link Extraction:** Automatically fetches email content and extracts the activation URL using BeautifulSoup.
- **Data Persistence:** Saves all successfully created accounts (email, password, and activation link) into a structured `accounts.json` file.
- **User-Friendly Logs:** Color-coded terminal output for easy status tracking.
- **Robust Connection:** Includes automatic reconnection attempts and fallback transport methods (WebSockets/Polling).
- **Persistent Terminal:** Keeps the terminal window open after completion so you can review the results.

## 🛠️ Installation

### 1. Install Dependencies
You will need `python-socketio`, `requests`, and `beautifulsoup4`. Install them using pip:

```bash
pip install "python-socketio[client]" requests beautifulsoup4
```

## 📖 How to Use

### Run the Script
To start the automation, run the main script from your terminal:

#### To use a random prefix:
```bash
python main.py
```

#### To use a specific prefix:
```bash
python main.py your_prefix_here
```

## 📊 Example Output
When an email arrives from cutout.pro, the terminal will display:

```text
============================================================
>>> NEW EMAIL RECEIVED <<<
From:    service@cutout.pro
Subject: Activate your cutout.pro account
[*] Detecting cutout.pro email. Extracting activation link...

SUCCESS! ACTIVATION LINK FOUND:
https://www.cutout.pro/resBackMsg?type=2&token=a9d1f70676724b009eb70a49d6483b0c

[*] Account saved to accounts.json
============================================================
```

## 📁 Project Structure
- `cutout_auto_register.py`: The main automation script.
- `accounts.json`: (Auto-generated) Stores created account credentials and links.
- `README.md`: Project documentation.

## ⚙️ Configuration
You can modify the following variables at the top of `cutout_auto_register.py`:
- `REFERRAL_CODE`: Your unique Cutout.pro referral ID.
- `DOMAIN`: The temporary email domain (default: `dayrep.com`).
- `ACCOUNTS_FILE`: The name of the file where account data is saved.

## ⚠️ Important Notes
- **One at a time:** The script is optimized to handle one registration per run for maximum reliability.
- **Referral Integration:** Your referral code `cutout_share-2091786` is pre-configured.
- **Waiting For Confirmation:** The terminal stays open until you press any key, ensuring you never miss a result.

---