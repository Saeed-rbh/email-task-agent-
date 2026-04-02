import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
USER_EMAIL = os.environ.get("GMAIL_ADDRESS", "")
USER_NAME = USER_EMAIL.split("@")[0] if USER_EMAIL else "Saeed"

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
You are an intelligent assistant analyzing an email received in the inbox of {USER_EMAIL} (the user, Saeed) to extract meaningful tasks for their To-Do list.

Email Subject: {subject}
Sender: {sender}
Email Body:
{body}
{projects_hint}
Analyze the email carefully from the perspective of {USER_EMAIL}. Specifically hunt for genuine tasks, action items, personal meetings, or calendar appointments that require the USER'S attention or attendance.

CRITICAL RULES FOR IGNORING EMAILS:
1. Do NOT create tasks for automated system notifications, security alerts, login warnings, welcome emails, or account provisioning.
2. Do NOT create tasks for simple onboarding steps like checking or verifying an email address.
3. ABSOLUTELY IGNORE ALL emails sent from "no-reply" addresses. There are zero exceptions to this rule, even if it claims to be a critical failure.
4. General status updates, receipts, or marketing newsletters are NOT tasks. Any email containing a newsletter footer (e.g. "You are receiving this email because you opted in", "Unsubscribe", "Copyright © [Org]") is a newsletter and MUST be completely ignored.
5. IGNORE mass institutional or university broadcast emails (e.g. wellness updates, support resources, community announcements, policy reminders, general advisories) even if they address the recipient by name ("Dear Saeed"). These are bulk emails and contain no personal actionable task.
6. Public event announcements (co-working days, showcases, workshops, webinars) in a newsletter are NOT tasks. Do NOT create tasks like "Attend X event" unless the user was personally and directly invited or required to attend.
7. Broadly available funding calls, grants, or application opportunities (e.g. "Applications are now open for...") mentioned in a newsletter are NOT personal tasks. Do NOT create tasks like "Apply for X grant" unless the email is directly and personally asking the user specifically to apply.
8. CRITICAL: If the email body was WRITTEN BY the user themselves (signed "Saeed", references their own email, or Sender matches the user's email), do NOT create tasks for requests or actions Saeed already performed (e.g. he already asked for something, already replied, already confirmed). HOWEVER, if that email contains a meeting, appointment, or calendar event that Saeed organized or agreed to attend, STILL extract that as a task so it appears in Todoist.
9. Do NOT create tasks for actions the user has already completed in this email chain (e.g. Saeed already sent a reply, made a request, confirmed attendance). Only create tasks for things that are STILL PENDING and assigned to the USER by a DIFFERENT person, OR meetings/appointments that Saeed needs to attend.
10. Do NOT create separate tasks out of conditional, advisory, or boilerplate suggestions in administrative notifications (e.g., "We encourage you to set up direct deposit", "You can view this on your portal").

CRITICAL RULES FOR EXTRACTION:
1. If the email contains multiple distinct requests or actions, extract EACH one as a separate task in the `tasks` array.
2. If there is a confirmed meeting or calendar appointment (meeting is set), extract it as a standard task to attend the meeting.
3. If the email includes an unresolved request to schedule a meeting (e.g. asking for your availability), extract it as a task to 'Reply regarding meeting availability'. Specifically for this task, YOU MUST begin the `task_details` field exactly with `🚨 *MEETING REQUEST NOTE:*` followed by a summary of their proposed times so it is highly visible.
4. If the email is an important administrative MUST-KNOW update (like an Expense Report status change, payment extracted, or approval), set `has_info: true` and provide a concise summary in `info_message`. If the email contains advisory/optional suggestions (like "set up direct deposit"), DO NOT make them tasks. Instead, briefly include these suggestions as extra notes strictly within the `info_message`.

If genuine tasks, meetings, or important info updates are present, return VALID JSON ONLY with this format. Do not use formatting like ```json.
{{
  "has_task": true or false, // True if there are tasks in the tasks array
  "has_info": true or false, // True if there is an important non-actionable update
  "info_message": "A concise summary of the important informational update (e.g. Expense report approved for 2,357 CAD). Empty string if none.",
  "original_sender": "Name <email@domain.com>", // Identify the ORIGINAL sender if the email was forwarded. Otherwise, output the provided Sender.
  "tasks": [
    {{
      "task_title": "A short, descriptive title of the task",
      "task_details": "Relevant details from the email",
      "due_date": "exact date and time", // e.g. "2026-04-10 at 15:00". MUST include "at <time>" if a time is mentioned. Leave as null if absent.
      "priority": 1, // integer from 1 to 4. 1=Normal, 2=Medium, 3=High, 4=Urgent/Critical.
      "project_name": "Project Name" // Select the most relevant project exactly matching the AVAILABLE TODOIST PROJECTS list. Default to "Inbox".
    }}
  ]
}}

If NO genuine task and NO important informational update is present, or it violates the rules above, return:
{{
  "has_task": false,
  "has_info": false
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

def generate_morning_brief(today_tasks, unassigned_tasks=None):
    if not model:
        return "Good morning! (AI failed to initialize)"
    
    tasks_text = ""
    if today_tasks:
        for idx, t in enumerate(today_tasks):
            tasks_text += f"{idx+1}. {t.content} (Priority: {t.priority})\n"
    else:
        tasks_text = "No tasks scheduled for today!\n"
        
    unassigned_text = ""
    if unassigned_tasks:
        for idx, t in enumerate(unassigned_tasks):
            unassigned_text += f"- {t.content}\n"
    
    prompt = f"""
Write a short, professional, and highly motivating Telegram morning brief addressed to "Saeed". Keep it extremely concise and direct. Use emojis naturally.

TASKS DUE TODAY:
{tasks_text}
"""
    if unassigned_tasks:
        prompt += f"""
UNASSIGNED TASKS (NO DUE DATE):
Provide a very brief summary or mention of these backlogged/unassigned tasks so Saeed keeps them in mind:
{unassigned_text}
"""
    
    prompt += "\nRespond strictly with the text of the Telegram message. Do not include introductory text like 'Here is your brief'."
    
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Good morning Saeed! You have {len(today_tasks)} tasks due today."
