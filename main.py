import os
import requests
from imap_tools import MailBox, AND
from datetime import datetime

GMAIL_EMAIL = os.environ.get('GMAIL_EMAIL')
GMAIL_APP_PASSWORD = os.environ.get('GMAIL_APP_PASSWORD')
NOTION_TOKEN = os.environ.get('NOTION_TOKEN')
DATABASE_ID = os.environ.get('DATABASE_ID')

def add_to_notion(subject, date, link, full_text):
    url = "https://api.notion.com/v1/pages"
    headers = {"Authorization": f"Bearer {NOTION_TOKEN}", "Content-Type": "application/json", "Notion-Version": "2022-06-28"}
    
    chunks = [full_text[i:i+1800] for i in range(0, len(full_text), 1800)]
    child_blocks = [{"object": "block", "type": "heading_2", "heading_2": {"rich_text": [{"text": {"content": "Email Content"}}]}}]
    for chunk in chunks[:3]:
        child_blocks.append({"object": "block", "type": "paragraph", "paragraph": {"rich_text": [{"text": {"content": chunk}}]}})

    payload = {
        "parent": {"database_id": DATABASE_ID},
        "properties": {
            "Assignment": {"title": [{"text": {"content": subject}}]},
            "Due Date": {"date": {"start": date}},
            "Email Link": {"url": link},
            "Status": {"select": {"name": "To Do"}},
            "Course": {"rich_text": [{"text": {"content": "EE 3310"}}]}
        },
        "children": child_blocks
    }
    res = requests.post(url, headers=headers, json=payload)
    return res.status_code == 200

with MailBox('imap.gmail.com').login(GMAIL_EMAIL, GMAIL_APP_PASSWORD) as mailbox:
    for msg in mailbox.fetch(AND(subject='Fw:'), reverse=True, limit=5):
        if "jlosh@uta.edu" in msg.text.lower():
            clean_date = msg.date.strftime('%Y-%m-%dT%H:%M:%S')
            link = "https://outlook.office.com/mail/search/from%3Ajlosh%40uta.edu"
            if add_to_notion(msg.subject, clean_date, link, msg.text):
                print(f"Synced: {msg.subject}")
