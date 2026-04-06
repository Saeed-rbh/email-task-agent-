import json
from llm_processor import extract_tasks_from_email

subject = "Expense Report Status Change"
sender = "Concur System <noreply@concur.com>"
body = """
Expense Report Status Change
Your expense report listed below has changed status.
Changed By
Concur System
Report Name
SPIE Conferance
Report Date
24/03/2026
Submit Date
24/03/2026
Amount Approved
2,357.89 CAD
Approval Status Set To
Approved
Payment Status Set To
Extracted for Payment
"""

print("Running extraction test...")
result = extract_tasks_from_email(subject, sender, body, "Work, Personal, Inbox")
print("Response JSON:")
print(json.dumps(result, indent=2))
