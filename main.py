import schedule
import time
import threading
from email_client import connect_imap, get_unread_emails
from llm_processor import extract_tasks_from_email, generate_morning_brief
from telegram_client import send_telegram_task, start_telegram_bot, send_telegram_message
from todo_client import get_todo_projects, get_todays_tasks
from imap_tools import AND

def run_morning_briefing():
    print("Running daily morning briefing...")
    tasks = get_todays_tasks()
    brief = generate_morning_brief(tasks)
    send_telegram_message(f"🌅 *Daily Morning Briefing*\n\n{brief}")

def poll_emails():
    print("Checking for new emails...")
    mailbox = connect_imap()
    if not mailbox:
        return

    try:
        projects = get_todo_projects()
        project_list_str = ", ".join([p.name for p in projects])
        
        for msg in mailbox.fetch(AND(seen=False), mark_seen=True):
            subject = msg.subject
            sender = msg.from_
            body = msg.text or msg.html
            
            print(f"Analyzing: {subject} from {sender}...")
            result = extract_tasks_from_email(subject, sender, body, project_list_str)
            
            if result and result.get("has_task"):
                title = result.get("task_title", "Task from Email")
                actual_sender = result.get("original_sender", sender)
                details = result.get("task_details", "") + f"\n\nFrom: {actual_sender}\nSubject: {subject}"
                due_date = result.get("due_date", "")
                priority = result.get("priority", 1)
                project_name = result.get("project_name", "Inbox")
                
                send_telegram_task(title, details, due_date, priority, project_name)
                print(f"Detected task: {title} (Project: {project_name})")
    except Exception as e:
        print(f"Error while polling: {e}")
    finally:
        mailbox.logout()

def run_scheduler():
    schedule.every(1).minutes.do(poll_emails)
    schedule.every().day.at("08:00").do(run_morning_briefing)
    
    print("Scheduler running. Checking inbox every minute... Daily briefing set for 08:00.")
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    print("--- Gemini Telegram Email Agent ---")
    
    # Start scheduler in background thread
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
    
    # Start Telegram bot in main thread (blocking)
    print("Starting Telegram Bot...")
    start_telegram_bot()
