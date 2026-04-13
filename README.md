# Gemini Email-to-Telegram Agent 

Welcome to your automated Email-to-Task Agent!

This application runs on your local machine. It reads your unread Gmail emails every minute. Using Google's Gemini AI, it identifies if an email contains a task assigned to you. If it does, it will instantly send a message to your **Telegram** app with actionable "Approve" and "Decline" buttons.

Clicking "Approve" will instantly add the parsed task directly to your Todoist!

## 🚀 Setup Instructions

### 1. Configuration (.env)
Ensure you have populated the following in your `.env` file:
- `GEMINI_API_KEY`: Your Google Gemini API Key.
- `GMAIL_ADDRESS`: Your Gmail address.
- `GMAIL_APP_PASSWORD`: Your Gmail App Password.
- `TODOIST_API_TOKEN`: Your Todoist API Token.
- `TELEGRAM_BOT_TOKEN`: Your Telegram Bot Token (from BotFather).
- `TELEGRAM_CHAT_ID`: Your Telegram Chat ID (from userinfobot).

### 2. Running the Agent (Development)
If you have Python installed, you can run it directly:
```powershell
cd "c:\Users\Saeed\Desktop\Task manager\email_agent"
.\venv\Scripts\Activate.ps1
python main.py
```

### 3. Running the Executable (.exe)
You can also run the pre-packaged executable:
1. Navigate to the `dist` folder.
2. Run `EmailAgent.exe`.
3. Keep the `.env` file in the same directory as the `.exe`.

## 🛠️ Building the EXE
To rebuild the executable:
```powershell
python build_exe.py
```
