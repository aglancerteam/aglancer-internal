import os
import httpx

SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")


async def send_slack_message(channel: str, text: str):
    if not SLACK_BOT_TOKEN:
        raise ValueError("SLACK_BOT_TOKEN is missing")

    url = "https://slack.com/api/chat.postMessage"
    headers = {
        "Authorization": f"Bearer {SLACK_BOT_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "channel": channel,
        "text": text,
    }

    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.post(url, headers=headers, json=payload)
        data = response.json()

    if not data.get("ok"):
        raise RuntimeError(f"Slack API error: {data}")

    return data
