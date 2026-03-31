import os
import uuid
import json
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from todo_client import create_todo_task, get_todo_projects
from llm_processor import extract_tasks_from_email
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

bot = telebot.TeleBot(TOKEN) if TOKEN else None

TASKS_FILE = "pending_tasks.json"

def load_tasks():
    if os.path.exists(TASKS_FILE):
        with open(TASKS_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except:
                return {}
    return {}

def save_tasks(tasks):
    with open(TASKS_FILE, "w", encoding="utf-8") as f:
        json.dump(tasks, f, indent=4)

def send_telegram_message(text):
    if bot and CHAT_ID:
        try:
            bot.send_message(CHAT_ID, text, parse_mode="Markdown")
        except Exception as e:
            print(f"Failed to send brief: {e}")

def send_telegram_task(title, details, due_date, priority=1, project_name="Inbox"):
    if not bot or not CHAT_ID:
        print("Telegram configuration missing. Check .env")
        return

    priority_map = {1: "⚪ Normal", 2: "🟡 Medium", 3: "🟠 High", 4: "🔴 Urgent"}
    p_text = priority_map.get(priority, "⚪ Normal")

    text = f"📝 *New Task Detected*\n\n*Title:* {title}\n*Priority:* {p_text}\n*Details:* {details}"
    if project_name and project_name != "Inbox":
        text += f"\n*Project:* 📁 {project_name}"
    if due_date:
        text += f"\n*Due Date:* {due_date}"

    task_id = str(uuid.uuid4())[:8]
    
    tasks = load_tasks()
    tasks[task_id] = {
        "title": title,
        "details": details,
        "due_date": due_date,
        "priority": priority,
        "project_name": project_name,
        "status": "pending"
    }
    save_tasks(tasks)

    markup = InlineKeyboardMarkup()
    btn_approve = InlineKeyboardButton("✅ Approve", callback_data=f"approve_{task_id}")
    btn_decline = InlineKeyboardButton("❌ Decline", callback_data=f"decline_{task_id}")
    markup.add(btn_approve, btn_decline)

    try:
        bot.send_message(CHAT_ID, text, reply_markup=markup, parse_mode="Markdown")
        print("Sent task to Telegram.")
    except Exception as e:
        print(f"Failed to send Telegram message: {e}")

@bot.callback_query_handler(func=lambda call: call.data.startswith('approve_') or call.data.startswith('decline_'))
def handle_approval(call):
    action, task_id = call.data.split('_', 1)
    
    tasks = load_tasks()
    task = tasks.get(task_id)

    if not task:
        bot.answer_callback_query(call.id, "Task not found in database.", show_alert=True)
        return
        
    if task.get("status") != "pending":
        bot.answer_callback_query(call.id, f"You already {task.get('status')} this task!", show_alert=True)
        return

    if action == 'approve':
        success = create_todo_task(task['title'], task['details'], task['due_date'], task.get('priority', 1), task.get('project_name', 'Inbox'))
        if success:
            bot.edit_message_text(
                chat_id=call.message.chat.id, 
                message_id=call.message.message_id, 
                text=call.message.text + "\n\n✅ Status: Added to Todoist!"
            )
            bot.answer_callback_query(call.id, "Added to Todoist!")
            task["status"] = "approved"
            save_tasks(tasks)
        else:
            bot.answer_callback_query(call.id, "Failed to connect to Todoist! Check console.")
            
    elif action == 'decline':
        bot.edit_message_text(
            chat_id=call.message.chat.id, 
            message_id=call.message.message_id, 
            text=call.message.text + "\n\n❌ Status: Declined"
        )
        bot.answer_callback_query(call.id, "Task Declined.")
        task["status"] = "declined"
        save_tasks(tasks)

@bot.message_handler(func=lambda message: True)
def handle_direct_message(message):
    if str(message.chat.id) != str(CHAT_ID):
        return
        
    msg = bot.reply_to(message, "🧠 _Analyzing your text..._", parse_mode="Markdown")
    
    projects = get_todo_projects()
    project_list_str = ", ".join([p.name for p in projects])
    
    result = extract_tasks_from_email("Direct Message", "You", message.text, project_list_str)
    
    if result and result.get("has_task"):
        bot.delete_message(chat_id=message.chat.id, message_id=msg.message_id)
        
        title = result.get("task_title", "Task from Telegram")
        details = result.get("task_details", "")
        due_date = result.get("due_date", "")
        priority = result.get("priority", 1)
        project_name = result.get("project_name", "Inbox")
        
        send_telegram_task(title, details, due_date, priority, project_name)
    else:
        bot.edit_message_text("No actionable task or meeting was found in that message.", chat_id=message.chat.id, message_id=msg.message_id)

def start_telegram_bot():
    if not bot:
        print("Telegram bot not configured.")
        return
    bot.infinity_polling()
