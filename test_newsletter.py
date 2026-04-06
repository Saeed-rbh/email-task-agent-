import json
from llm_processor import extract_tasks_from_email

subject = "CONGRATS TO ARIANA NATURALS, CHOCOVATE LABS, GREENVEIL, JOEYDOLLS, LEAOPORD AI & TEWARI DE-OX"
sender = "YSpace York University <newsletter@yspace.ca>"
body = """
CONGRATS TO ARIANA NATURALS, CHOCOVATE LABS, GREENVEIL, JOEYDOLLS, LEAOPORD AI & TEWARI DE-OX

Congratulations to Chocovate, Tewari, and GreenVeil for securing the Ontario Food Technology Pilot grant from CFIN!
Congrats to Ariana Naturals for their feature by Invest Ottawa!
Shoutout to Joeydolls for being nominated for Entrepreneur of Impact! VOTE HERE

COMING UP AT YSPACE
Join us for a high-energy co-working day taking place on April 9th at YSpace Markham.

Venture Catalyst Showcase
YSpace Venture Catalyst Showcase Winter 2026 takes place on Thursday, April 16 from 6:00 PM to 9:00 PM. Register here

Founder Fundamentals: Leadership & Culture by Design
Tuesday, April 7th, 6:00 pm - 8:00 pm REGISTER HERE

FUNDING
NERVE Program 2026: Applications open, offering up to $100,000. Deadline: April 24th.
BMO Celebrating Women Grant: Applications deadline April 23.
Student Work Placement: Apply by April 10.

You are receiving this email because you opted in at our website.
Copyright 2026 YSpace York University
"""

print("Running newsletter test...")
result = extract_tasks_from_email(subject, sender, body, "Work, Personal, Inbox")
print("Response JSON:")
print(json.dumps(result, indent=2))
