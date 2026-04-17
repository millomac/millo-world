import logging

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

logger = logging.getLogger(__name__)


class SlackNotifier:
    def __init__(self, config):
        self.client = WebClient(token=config.slack_token)
        self.channel = config.slack_channel

    def send(self, notes: dict, filename: str):
        blocks = self._build_blocks(notes, filename)
        try:
            self.client.chat_postMessage(
                channel=self.channel,
                blocks=blocks,
                text=f"Meeting Notes: {filename}",
            )
            logger.info(f"Notas enviadas a Slack (canal {self.channel})")
        except SlackApiError as e:
            logger.error(f"Error enviando a Slack: {e.response['error']}")
            raise

    def _build_blocks(self, notes: dict, filename: str) -> list:
        blocks = [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": f"Meeting Notes: {filename}"},
            },
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"*Resumen*\n{notes['summary']}"},
            },
        ]

        if notes.get("participants"):
            blocks.append(
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*Participantes*\n" + ", ".join(notes["participants"]),
                    },
                }
            )

        if notes.get("decisions"):
            text = "\n".join(f"• {d}" for d in notes["decisions"])
            blocks.append(
                {"type": "section", "text": {"type": "mrkdwn", "text": f"*Decisiones*\n{text}"}}
            )

        if notes.get("action_items"):
            text = "\n".join(
                f"• *{ai['task']}* — {ai['owner']} ({ai['due_date']})"
                for ai in notes["action_items"]
            )
            blocks.append(
                {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": f"*Action Items*\n{text}"},
                }
            )

        if notes.get("parking_lot"):
            text = "\n".join(f"• {p}" for p in notes["parking_lot"])
            blocks.append(
                {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": f"*Parking Lot*\n{text}"},
                }
            )

        if notes.get("next_steps"):
            text = "\n".join(f"• {n}" for n in notes["next_steps"])
            blocks.append(
                {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": f"*Próximos Pasos*\n{text}"},
                }
            )

        blocks.append({"type": "divider"})
        return blocks
