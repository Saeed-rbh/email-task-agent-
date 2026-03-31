import os
import smtplib
from email.message import EmailMessage
from imap_tools import MailBox, AND
import datetime
from dotenv import load_dotenv

load_dotenv()
GMAIL_ADDRESS = os.environ.get("GMAIL_ADDRESS")
GMAIL_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD")

def get_unread_emails_last_24h():
    if not GMAIL_ADDRESS or not GMAIL_PASSWORD:
        print("Gmail credentials missing in .env")
        return []
        
    try:
        messages_list = []
        with MailBox('imap.gmail.com').login(GMAIL_ADDRESS, GMAIL_PASSWORD) as mailbox:
            # fetch unread emails and instantly mark them as read so we don't process them again
            for msg in mailbox.fetch(AND(seen=False), mark_seen=True):
                messages_list.append(msg)
        return messages_list
    except Exception as e:
        print(f"IMAP Error: {e}")
        return []

def send_morning_brief(html_content, recipient_email):
    if not GMAIL_ADDRESS or not GMAIL_PASSWORD:
        print("Gmail credentials missing in .env")
        return False
        
    try:
        msg = EmailMessage()
        msg['Subject'] = 'Your Daily Email Task Brief'
        msg['From'] = GMAIL_ADDRESS
        msg['To'] = recipient_email
        msg.add_alternative(html_content, subtype='html')
        
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(GMAIL_ADDRESS, GMAIL_PASSWORD)
            smtp.send_message(msg)
            
        print("Morning brief sent successfully via Gmail.")
        return True
    except Exception as e:
        print(f"SMTP Error: {e}")
        return False
