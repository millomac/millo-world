import logging
from datetime import datetime

from notion_client import Client

logger = logging.getLogger(__name__)


class NotionNotifier:
    def __init__(self, config):
        self.client = Client(auth=config.notion_token)
        self.database_id = config.notion_database_id

    def create_page(self, notes: dict, filename: str):
        date_str = datetime.now().strftime("%Y-%m-%d")
        properties = {
            "Name": {"title": [{"text": {"content": filename}}]},
            "Date": {"date": {"start": date_str}},
        }
        children = self._build_blocks(notes)
        try:
            self.client.pages.create(
                parent={"database_id": self.database_id},
                properties=properties,
                children=children,
            )
            logger.info("Página creada en Notion")
        except Exception as e:
            logger.error(f"Error creando página en Notion: {e}")
            raise

    def _build_blocks(self, notes: dict) -> list:
        blocks = []

        blocks.append(self._heading("Resumen"))
        blocks.append(self._paragraph(notes["summary"]))

        if notes.get("participants"):
            blocks.append(self._heading("Participantes"))
            for p in notes["participants"]:
                blocks.append(self._bullet(p))

        if notes.get("decisions"):
            blocks.append(self._heading("Decisiones"))
            for d in notes["decisions"]:
                blocks.append(self._bullet(d))

        if notes.get("action_items"):
            blocks.append(self._heading("Action Items"))
            for ai in notes["action_items"]:
                blocks.append(self._bullet(f"{ai['task']} — {ai['owner']} ({ai['due_date']})"))

        if notes.get("parking_lot"):
            blocks.append(self._heading("Parking Lot"))
            for p in notes["parking_lot"]:
                blocks.append(self._bullet(p))

        if notes.get("next_steps"):
            blocks.append(self._heading("Próximos Pasos"))
            for n in notes["next_steps"]:
                blocks.append(self._bullet(n))

        return blocks

    def _heading(self, text: str) -> dict:
        return {
            "object": "block",
            "type": "heading_2",
            "heading_2": {"rich_text": [{"text": {"content": text}}]},
        }

    def _paragraph(self, text: str) -> dict:
        return {
            "object": "block",
            "type": "paragraph",
            "paragraph": {"rich_text": [{"text": {"content": text}}]},
        }

    def _bullet(self, text: str) -> dict:
        return {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {"rich_text": [{"text": {"content": text}}]},
        }
