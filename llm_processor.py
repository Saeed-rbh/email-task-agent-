import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

model = None
try:
    model = genai.GenerativeModel('gemini-3.1-flash-lite-preview')
except Exception as e:
    print(f"Warning: Gemini Model initialization failed. Ensure API key is set. {e}")

def extract_tasks_from_email(subject, sender, body, project_list=""):
    if not model:
        print("Gemini model not initialized.")
        return {"has_task": False}

    projects_hint = ""
    if project_list:
        projects_hint = f"\nAVAILABLE TODOIST PROJECTS TO CATEGORIZE INTO: {project_list}\n"

    prompt = f"""
You are an intelligent assistant analyzing an email to extract meaningful tasks for a professional's To-Do list.

Email Subject: {subject}
Sender: {sender}
Email Body:
{body}
{projects_hint}
Analyze the email carefully. Specifically hunt for genuine tasks, action items, personal meetings, or calendar appointments that require the user's attention or attendance.

CRITICAL RULES FOR IGNORING EMAILS:
1. Do NOT create tasks for automated system notifications, security alerts, login warnings, welcome emails, or account provisioning.
2. Do NOT create tasks for simple onboarding steps like checking or verifying an email address.
3. ABSOLUTELY IGNORE ALL emails sent from "no-reply" addresses. There are zero exceptions to this rule, even if it claims to be a critical failure.
4. General status updates, receipts, or marketing newsletters are NOT tasks.

If there is a genuine, human-assigned action item, a personal meeting, or a calendar appointment, return VALID JSON ONLY with this format. Do not use formatting like ```json.
{{
  "has_task": true,
  "task_title": "A short, descriptive title of the task",
  "task_details": "Relevant details from the email",
  "due_date": "exact date and time", // e.g. "2026-04-10 at 15:00" or "Friday at 3 PM". MUST include "at <time>" if a time is mentioned. Leave as null if absent.
  "priority": 1, // integer from 1 to 4. 1=Normal, 2=Medium, 3=High, 4=Urgent/Critical.
  "original_sender": "Name <email@domain.com>", // Identify the ORIGINAL sender if the email was forwarded. Otherwise, output the provided Sender.
  "project_name": "Project Name" // Select the single most relevant project EXACTLY matching the AVAILABLE TODOIST PROJECTS list above. If none match perfectly or the list is missing, default exactly to "Inbox".
}}

If NO genuine task is present, or it violates the rules above, return:
{{
  "has_task": false
}}

Respond ONLY with valid JSON.
"""
    try:
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        if response_text.startswith("```json"):
            response_text = response_text[7:-3].strip()
        elif response_text.startswith("```"):
            response_text = response_text[3:-3].strip()
            
        result = json.loads(response_text)
        return result
    except Exception as e:
        print(f"Failed to parse Gemini response: {e}")
        return {"has_task": False}

def generate_morning_brief(tasks_list):
    if not model:
        return "Good morning! (AI failed to initialize)"
    
    tasks_text = ""
    for idx, t in enumerate(tasks_list):
        tasks_text += f"{idx+1}. {t.content} (Priority: {t.priority})\n"
        
    prompt = f"""
Write a short, professional, and highly motivating Telegram morning brief summarizing these tasks that are due today. Keep it extremely concise and direct. Use emojis naturally.

TASKS DUE TODAY:
{tasks_text if tasks_text else "No tasks scheduled for today!"}

Respond strictly with the text of the Telegram message. Do not include introductory text like 'Here is your brief'.
"""
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Good morning! You have {len(tasks_list)} tasks due today."
