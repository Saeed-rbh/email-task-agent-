import json
from llm_processor import extract_tasks_from_email

subject = "Videos for DiscoveryX"
sender = "Christina Corre <ccorre@yorku.ca>"
body = """
Hi all,

Thank you for signing up to display your research at DiscoveryX.

We are working closely with the Communications Team to ensure that our branding and presentation look professional. To that end, could you please send any videos you plan to display at the show to Kerry (copied here) so that her team can add York branding to them?

Are you available later this week for a meeting? Friday morning?

Please send the videos by April 7.

Thanks,

Christina
"""

print("Running extraction test...")
result = extract_tasks_from_email(subject, sender, body, "Work, Personal, Inbox")
print("Response JSON:")
print(json.dumps(result, indent=2))
