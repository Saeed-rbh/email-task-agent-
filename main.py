import schedule
import time
import threading
import os
import sys

# Ensure UTF-8 encoding for Windows console
if sys.stdout is not None:
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        # Fallback for older python versions
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from email_client import get_unread_emails_last_24h
from llm_processor import extract_tasks_from_email, generate_morning_brief
from telegram_client import send_telegram_task, start_telegram_bot, send_telegram_message
from todo_client import get_todo_projects, get_todays_tasks
from update_manager import check_for_updates
from imap_tools import AND

def run_morning_briefing():
    print("Running daily morning briefing...")
    today_tasks, unassigned_tasks = get_todays_tasks()
    brief = generate_morning_brief(today_tasks, unassigned_tasks)
    send_telegram_message(f"🌅 *Daily Morning Briefing*\n\n{brief}")

def poll_emails():
    print("Checking for new emails...")
    messages = get_unread_emails_last_24h()
    if not messages:
        return

    try:
        projects = get_todo_projects()
        project_list_str = ", ".join([p.name for p in projects])
        
        for msg in messages:
            subject = msg.subject
            sender = msg.from_
            body = msg.text or msg.html
            
            print(f"Analyzing: {subject} from {sender}...")
            result = extract_tasks_from_email(subject, sender, body, project_list_str)
            
            if result and result.get("has_info"):
                info_msg = result.get("info_message", "")
                if info_msg:
                    actual_sender = result.get("original_sender", sender)
                    text = f"ℹ️ *Information Update*\n\n{info_msg}\n\n*From:* {actual_sender}\n*Subject:* {subject}"
                    send_telegram_message(text)
                    print(f"Detected info update: {subject}")
            
            if result and result.get("has_task"):
                actual_sender = result.get("original_sender", sender)
                tasks = result.get("tasks", [])
                
                if not tasks and "task_title" in result:
                    tasks = [result]
                    
                for t in tasks:
                    title = t.get("task_title", "Task from Email")
                    details = t.get("task_details", "") + f"\n\nFrom: {actual_sender}\nSubject: {subject}"
                    due_date = t.get("due_date", "")
                    priority = t.get("priority", 1)
                    project_name = t.get("project_name", "Inbox")
                    
                    send_telegram_task(title, details, due_date, priority, project_name)
                    print(f"Detected task: {title} (Project: {project_name})")
    except Exception as e:
        print(f"Error while polling: {e}")

def run_scheduler():
    schedule.every(1).minutes.do(poll_emails)
    schedule.every().day.at("08:00").do(run_morning_briefing)
    schedule.every(1).hours.do(check_for_updates)
    
    print("Scheduler running. Checking inbox every minute... Daily briefing set for 08:00. Checking for updates every hour.")
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    print("--- Gemini Telegram Email Agent ---")
    
    # Check for updates
    check_for_updates()
    
    # Start scheduler in background thread
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
    
    # Start Telegram bot in main thread (blocking)
    print("Starting Telegram Bot...")
    start_telegram_bot()
