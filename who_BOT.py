import praw
import prawcore
import re
import sys
import requests
from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

# ───────────── CONFIG ──────────────
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
HF_TOKEN = os.getenv("HF_API")
USER_AGENT    = "script:reddit_persona_builder:v1.0 (by u/notgonnagivemaname)"
ROUTER_URL    = "https://router.huggingface.co/novita/v3/openai/chat/completions"
MODEL_NAME    = "mistralai/mistral-7b-instruct"
DATA_DIR      = Path("data")
OUTPUT_DIR    = Path("personas")
TIMEOUT       = 90
# ───────────────────────────────────

reddit = praw.Reddit(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    user_agent=USER_AGENT
)

def extract_username(profile_url):
    match = re.search(r'reddit\.com/user/([\w-]+)/?', profile_url)
    return match.group(1) if match else None

def user_exists(username):
    try:
        _ = reddit.redditor(username).id
        return True
    except (prawcore.exceptions.NotFound, prawcore.exceptions.Forbidden, AttributeError):
        return False

def scrape_user_data(username, limit=40):
    user = reddit.redditor(username)
    comments, posts = [], []


    for c in user.comments.new(limit=limit):
        comments.append({
            "id": c.id,
            "subreddit": c.subreddit.display_name,
            "created_utc": c.created_utc,
            "score": c.score,
            "permalink": f"https://www.reddit.com{c.permalink}",
            "body": c.body
        })

    for p in user.submissions.new(limit=limit):
        posts.append({
            "id": p.id,
            "title": p.title,
            "subreddit": p.subreddit.display_name,

            "selftext": p.selftext
        })

    return {"username": username, "comments": comments, "posts": posts}

def build_prompt(data, sample_limit=30):
    intro = f"""You are an expert analyst tasked with building a user persona from Reddit activity. 
    Keep your inference playful and light hearted, but hard hitting nonetheless, along with a short explanation, which may include multiple examples for each trait. Focus PRIMARILY ON COMMNETS OF THE USER
    NECESSARY INSTRUCTION: DONT BOLD THE ANY TEXT IN YOUR ANSWERS, KEEP REST OF THE FORMATTING. DON'T MENTION LINKS, or cite lack of data
Return the output in this structure:

Username: <username>

>>> Personality Traits:
- <trait> : <example>

>>> Interests:
- ...

>>> Activity Pattern:
- ...

Include a subreddit corresponding to each trait for every insight.

Now here are up to {sample_limit} raw posts and comments from u/{data['username']}:
------------------------------------------------
"""
    snippets = []

    for c in data["comments"][: sample_limit // 2]:
        snippets.append(
            f"Comment on r/{c['subreddit']} (score {c['score']}):\n\"{c['body']}\"\n[Link: {c['permalink']}]\n"
        )
    for p in data["posts"][: sample_limit // 2]:
        body = p['selftext'] or "(no self-text)"
        snippets.append(
            f"Post on r/{p['subreddit']} \n\"{p['title']}\"\n{body}\n"
        )

    return intro + "\n---\n".join(snippets)

def call_hf_router(prompt):
    if not HF_TOKEN:
        sys.exit("HF_TOKEN environment variable not set.")

    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant that creates user personas from Reddit data."},
            {"role": "user", "content": prompt}
        ]
    }

    response = requests.post(ROUTER_URL, headers=headers, json=payload, timeout=TIMEOUT)

    if response.status_code == 200:
        result = response.json()
        return result["choices"][0]["message"]["content"]
    else:
        print(f"Router error {response.status_code}: {response.text}")
        sys.exit(1)




# ───────────── MAIN ──────────────

r"""

          _              ____   ___ _____ 
__      _| |__   ___    | __ ) / _ \_   _|
\ \ /\ / / '_ \ / _ \   |  _ \| | | || |  
 \ V  V /| | | | (_) |  | |_) | |_| || |  
  \_/\_/ |_| |_|\___/___|____/ \___/ |_|  
                   |_____|                

"""
