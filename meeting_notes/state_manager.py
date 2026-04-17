import json
from pathlib import Path


class StateManager:
    def __init__(self, state_file: str):
        self.state_file = Path(state_file)
        self._state = self._load()

    def _load(self) -> dict:
        if self.state_file.exists():
            return json.loads(self.state_file.read_text())
        return {"processed_ids": []}

    @property
    def processed_ids(self) -> set:
        return set(self._state["processed_ids"])

    def mark_processed(self, file_id: str):
        self._state["processed_ids"].append(file_id)
        self.state_file.write_text(json.dumps(self._state, indent=2))
