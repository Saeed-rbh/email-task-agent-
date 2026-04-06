import os
import datetime
from todoist_api_python.api import TodoistAPI
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.environ.get("TODOIST_API_TOKEN")
api = TodoistAPI(TOKEN) if TOKEN else None

def get_todo_projects():
    if not api:
        return []
    try:
        return api.get_projects()
    except Exception as e:
        print(f"Failed to fetch Todoist projects: {e}")
        return []

def get_todays_tasks():
    if not api:
        return [], []
    try:
        all_tasks = []
        for page in api.get_tasks():
            all_tasks.extend(page)
            
        today_tasks = []
        unassigned_tasks = []
        today_str = datetime.datetime.now().strftime("%Y-%m-%d")
        
        # Weekday check (0-4 are Mon-Fri, 5-6 are weekend)
        is_weekday = datetime.datetime.now().weekday() < 5
        
        for t in all_tasks:
            if getattr(t, 'due', None) and getattr(t.due, 'date', None):
                due_date_str = str(t.due.date)[:10]
                if due_date_str <= today_str:
                    today_tasks.append(t)
            else:
                if is_weekday:
                    unassigned_tasks.append(t)
            
        return today_tasks, unassigned_tasks
    except Exception as e:
        print(f"Failed to fetch today's tasks: {e}")
        return [], []

def create_todo_task(title, details, due_date=None, priority=1, project_name=None):
    if not api:
        print("Todoist API Token missing.")
        return False
        
    try:
        try:
            priority = int(priority)
        except (ValueError, TypeError):
            priority = 1
            
        task_data = {
            "content": title,
            "description": details,
            "priority": priority
        }
        if due_date:
            task_data["due_string"] = due_date
            
        if project_name and project_name.lower() != "inbox":
            projects = get_todo_projects()
            for p in projects:
                if p.name.lower() == project_name.lower():
                    task_data["project_id"] = p.id
                    break
            
        task = api.add_task(**task_data)
        print(f"Todoist task created: {task.content}")
        return True
    except Exception as e:
        print(f"Error creating Todoist task: {e}")
        return False
