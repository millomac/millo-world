import logging
import sys

from dotenv import load_dotenv

from meeting_notes.config import Config
from meeting_notes.drive import DriveClient
from meeting_notes.notion_notifier import NotionNotifier
from meeting_notes.processor import TranscriptProcessor
from meeting_notes.slack_notifier import SlackNotifier
from meeting_notes.state_manager import StateManager

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def main():
    config = Config()
    state = StateManager(config.state_file)
    drive = DriveClient(config)
    processor = TranscriptProcessor(config)
    slack = SlackNotifier(config)
    notion = NotionNotifier(config)

    logger.info(f"Buscando transcripts de '{config.meeting_name_filter}' en Google Drive...")
    transcripts = drive.find_new_transcripts(config.meeting_name_filter, state.processed_ids)

    if not transcripts:
        logger.info("No hay transcripts nuevos por procesar.")
        return

    errors = []
    for transcript in transcripts:
        logger.info(f"Procesando: {transcript['name']}")
        try:
            content = drive.download_transcript(transcript)
            notes = processor.generate_notes(transcript["name"], content)
            slack.send(notes, transcript["name"])
            notion.create_page(notes, transcript["name"])
            state.mark_processed(transcript["id"])
            logger.info(f"OK: {transcript['name']}")
        except Exception as e:
            logger.error(f"Error procesando '{transcript['name']}': {e}")
            errors.append(transcript["name"])

    if errors:
        logger.warning(f"Fallaron {len(errors)} transcripts: {errors}")
        sys.exit(1)


if __name__ == "__main__":
    main()
