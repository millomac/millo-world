import io
import logging
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

logger = logging.getLogger(__name__)

SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]


class DriveClient:
    def __init__(self, config):
        self.config = config
        self._service = self._build_service()

    def _build_service(self):
        creds = None
        token_path = Path(self.config.google_token_file)
        creds_path = Path(self.config.google_credentials_file)

        if token_path.exists():
            creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(str(creds_path), SCOPES)
                creds = flow.run_local_server(port=0)
            token_path.write_text(creds.to_json())

        return build("drive", "v3", credentials=creds)

    def find_new_transcripts(self, name_filter: str, processed_ids: set) -> list[dict]:
        query = (
            f"name contains '{name_filter}' "
            "and mimeType != 'application/vnd.google-apps.folder' "
            "and trashed = false"
        )
        result = (
            self._service.files()
            .list(
                q=query,
                fields="files(id, name, mimeType, modifiedTime)",
                orderBy="modifiedTime desc",
            )
            .execute()
        )

        files = result.get("files", [])
        new_files = [f for f in files if f["id"] not in processed_ids]
        logger.info(f"Encontrados {len(files)} transcripts, {len(new_files)} sin procesar")
        return new_files

    def download_transcript(self, file_meta: dict) -> str:
        file_id = file_meta["id"]
        mime = file_meta.get("mimeType", "")

        if mime == "application/vnd.google-apps.document":
            response = (
                self._service.files()
                .export(fileId=file_id, mimeType="text/plain")
                .execute()
            )
            return response.decode("utf-8")

        # For .docx, .txt, .vtt, or other binary formats
        request = self._service.files().get_media(fileId=file_id)
        buffer = io.BytesIO()
        downloader = MediaIoBaseDownload(buffer, request)
        done = False
        while not done:
            _, done = downloader.next_chunk()
        return buffer.getvalue().decode("utf-8", errors="replace")
