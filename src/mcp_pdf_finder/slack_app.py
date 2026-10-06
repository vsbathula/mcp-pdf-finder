import logging
import asyncio
from typing import Any, Dict

from mcp_pdf_finder.client import ask_pdf_assistant

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from mcp_pdf_finder.config import settings
from mcp_pdf_finder.logging_config import setup_logging


setup_logging()
logger = logging.getLogger(__name__)


SLACK_BOT_TOKEN = settings.slack_bot_token.get_secret_value()
SLACK_APP_TOKEN = settings.slack_app_token.get_secret_value()
SLACK_CHANNEL_ID = settings.slack_channel_id


if not SLACK_BOT_TOKEN:
    raise ValueError("SLACK_BOT_TOKEN is not configured")

if not SLACK_APP_TOKEN:
    raise ValueError("SLACK_APP_TOKEN is not configured")


app = App(
    token=SLACK_BOT_TOKEN,
)

def resolve_slack_user(
    client: Any,
    user_id: str,
) -> Dict[str, str]:
    """Resolve Slack user ID to email, username, and display name."""

    user_info = client.users_info(
        user=user_id
    )

    profile = user_info["user"]["profile"]

    email = profile.get("email", "")

    username = (
        email.split("@")[0]
        if email
        else user_info["user"].get("name", user_id)
    )

    return {
        "slack_user_id": user_id,
        "username": username,
        "email": email,
        "real_name": profile.get(
            "real_name",
            username,
        ),
    }


@app.event("app_mention")
def handle_app_mention(event, say, client):

    slack_user_id = event["user"]
    text = event.get("text", "")

    # Existing thread_ts means this mention is already inside a thread.
    existing_thread_ts = event.get("thread_ts")

    # Use the original message timestamp to start a new thread.
    thread_ts = existing_thread_ts or event["ts"]

    logger.info(
        "Received Slack app mention | user=%s thread_ts=%s",
        slack_user_id,
        thread_ts,
    )

    # First mention / top-level message
    if existing_thread_ts is None:
        say(
            text="Hello from MCP PDF Finder!",
            thread_ts=thread_ts,
        )

    user = resolve_slack_user(
        client=client,
        user_id=slack_user_id,
    )

    username = user["username"]

    answer = asyncio.run(
        ask_pdf_assistant(
            question=text,
            user_id=username,
        )
    )

    say(
        text=answer,
        thread_ts=thread_ts,
    )

    


def main():
    logger.info("Starting Slack PDF Agent")

    handler = SocketModeHandler(
        app,
        SLACK_APP_TOKEN,
    )

    handler.start()


if __name__ == "__main__":
    main()