import os


class Config:
    def __init__(self):
        self.anthropic_api_key = os.environ["ANTHROPIC_API_KEY"]
        self.slack_token = os.environ["SLACK_BOT_TOKEN"]
        self.slack_channel = os.environ["SLACK_CHANNEL_ID"]
        self.notion_token = os.environ["NOTION_TOKEN"]
        self.notion_database_id = os.environ["NOTION_DATABASE_ID"]
        self.google_credentials_file = os.environ.get("GOOGLE_CREDENTIALS_FILE", "credentials.json")
        self.google_token_file = os.environ.get("GOOGLE_TOKEN_FILE", "token.json")
        self.meeting_name_filter = os.environ.get("MEETING_NAME_FILTER", "Domain Refinement")
        self.state_file = os.environ.get("STATE_FILE", "state.json")
        self.claude_model = os.environ.get("CLAUDE_MODEL", "claude-sonnet-4-6")
