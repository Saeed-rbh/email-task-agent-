import json
from llm_processor import extract_tasks_from_email

subject = "Fwd: OPTIR @ Yorku - Focus problem"
sender = "Sergey Zayats <sergey@photothermal.com>"
body = """
Hi Sergey,

Perfect, let me know if you needed anything. Also, I wanted to ask for training certificate as we discussed before. I would like to have that as part of my resume if possible.

My phone number: 4168365851.

See you in 2 weeks,
Saeed
"""

print("Running outgoing email test...")
result = extract_tasks_from_email(subject, sender, body, "Work, Personal, Inbox")
print("Response JSON:")
print(json.dumps(result, indent=2))
