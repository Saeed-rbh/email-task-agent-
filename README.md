# Gemini Email-to-Telegram Agent 

Welcome to your automated Email-to-Task Agent!

This Python application runs in the background. It reads your unread Gmail emails every minute. Using Google's Gemini AI, it identifies if an email contains a task assigned to you. If it does, it will instantly send a message to your **Telegram** app with actionable "Approve" and "Decline" buttons.

Clicking "Approve" will instantly add the parsed task directly to your Todoist!

## 🚀 Setup Instructions

### 1. Todoist & Gmail
Ensure you have populated `GMAIL_ADDRESS`, `GMAIL_APP_PASSWORD`, and `TODOIST_API_TOKEN` in your `.env` file.

### 2. Telegram Bot Setup
We need to create a bot on Telegram to send you messages and receive your button clicks.
1. Open the Telegram app and search for **BotFather** (it has a verified checkmark).
2. Send the message `/newbot` and follow the prompts to name your bot.
3. BotFather will give you a long **HTTP API Token**. 
   * Paste this into `.env` under `TELEGRAM_BOT_TOKEN`.
4. Go to your new Bot's chat and press **Start**.
5. Now, search for **@userinfobot** on Telegram and press Start. It will reply with your personal `Id` number.
   * Paste this number into `.env` under `TELEGRAM_CHAT_ID`.

### 3. Run the Agent!
Open PowerShell or your command prompt and run the following commands:
```powershell
cd "c:\Users\Saeed\Desktop\Task manager\email_agent"
.\venv\Scripts\Activate.ps1
python main.py
```
