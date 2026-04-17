import logging

import anthropic

logger = logging.getLogger(__name__)

_MEETING_NOTES_TOOL = {
    "name": "meeting_notes",
    "description": "Estructura las notas de la reunión en secciones clave",
    "input_schema": {
        "type": "object",
        "properties": {
            "summary": {
                "type": "string",
                "description": "Resumen ejecutivo de la reunión en 3-5 oraciones",
            },
            "participants": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Lista de participantes que aparecen en el transcript",
            },
            "decisions": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Decisiones concretas tomadas durante la reunión",
            },
            "action_items": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "task": {"type": "string"},
                        "owner": {"type": "string"},
                        "due_date": {"type": "string"},
                    },
                    "required": ["task", "owner", "due_date"],
                },
                "description": "Tareas asignadas con responsable y fecha límite",
            },
            "parking_lot": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Temas que surgieron pero quedaron pendientes para otra reunión",
            },
            "next_steps": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Próximos pasos generales acordados por el equipo",
            },
        },
        "required": [
            "summary",
            "participants",
            "decisions",
            "action_items",
            "parking_lot",
            "next_steps",
        ],
    },
}

_SYSTEM = (
    "Eres un experto en product management que transforma transcripts de reuniones "
    "en meeting notes claras y accionables. Responde siempre en español. "
    "Extrae únicamente información que aparezca explícitamente en el transcript. "
    "Para fechas límite no mencionadas en la reunión, usa 'Por definir'."
)


class TranscriptProcessor:
    def __init__(self, config):
        self.client = anthropic.Anthropic(api_key=config.anthropic_api_key)
        self.model = config.claude_model

    def generate_notes(self, filename: str, transcript: str) -> dict:
        prompt = (
            f"Aquí está el transcript de la reunión '{filename}':\n\n"
            f"<transcript>\n{transcript[:100_000]}\n</transcript>\n\n"
            "Extrae y estructura las meeting notes usando la herramienta meeting_notes."
        )

        response = self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            system=_SYSTEM,
            tools=[_MEETING_NOTES_TOOL],
            tool_choice={"type": "tool", "name": "meeting_notes"},
            messages=[{"role": "user", "content": prompt}],
        )

        for block in response.content:
            if block.type == "tool_use" and block.name == "meeting_notes":
                logger.info("Meeting notes generadas exitosamente por Claude")
                return block.input

        raise RuntimeError("Claude no retornó meeting notes estructuradas")
