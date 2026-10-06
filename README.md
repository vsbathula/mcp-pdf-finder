# MCP PDF Finder

A Slack-based PDF assistant built with the Model Context Protocol (MCP), Groq, Slack Bolt, and pypdf. It is designed to let an LLM or application safely query one user's PDF set without crossing into other users' folders.

## Architecture

Slack
  -> slack_app.py
  -> resolve authenticated Slack user
  -> client.py / Groq
  -> MCP client over stdio
  -> MCP server
  -> PDF tools
  -> PDFService
  -> documents/{username}/

Slack is the user interface. Groq chooses which PDF tool to use, while client.py executes the tool through MCP.

## Project structure

```text
mcp-pdf-finder/
├── .dev.env
├── .prod.env
├── pyproject.toml
├── README.md
├── documents/
│   ├── user1/
│   └── user2/
├── logs/
├── src/
│   └── mcp_pdf_finder/
│       ├── client.py
│       ├── config.py
│       ├── logging_config.py
│       ├── server.py
│       ├── slack_app.py
│       ├── services/
│       │   └── pdf_service.py
│       └── tools/
│           ├── list_pdfs.py
│           ├── pdf_info.py
│           ├── read_pdf.py
│           ├── search_all_pdfs.py
│           └── search_pdf.py
└── tests/
    ├── test_list_pdfs.py
    ├── test_read_pdf.py
    └── test_search_pdf.py
```

## Features

• Slack Socket Mode integration
• Thread-based Slack replies
• Slack user resolution using corporate email
• Per-user PDF directories
• MCP server over stdio
• Groq tool selection and final-answer generation
• PDF extraction with pypdf
• Case-insensitive lexical PDF search
• Page-level results and snippets
• File-based logging
• Path traversal protection
• Application-enforced authenticated user_id

## Requirements

- Python 3.11+
- A virtual environment recommended
- PDF files stored under `documents/<user_id>/`
- Valid API credentials for the configured LLM and Slack integration

## Setup

1. Create and activate a virtual environment:

```bash
cd mcp-pdf-finder
python -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -U pip
pip install -e '.[dev]'
```

3. Configure environment variables.

The project automatically loads the environment file based on `APP_ENV`:

- `APP_ENV=dev` -> `.dev.env`
- `APP_ENV=prod` -> `.prod.env`

Example:

```env
APP_ENV=dev
LOGGING_LEVEL=INFO
DOCUMENTS_DIR=documents
MAX_PDF_SIZE=50000000
MAX_SEARCH_RESULTS=50
OCR_ENABLED=false
LLM_API_KEY=your_api_key_here
LLM_API_MODEL=openai/gpt-oss-120b
SLACK_BOT_TOKEN=xoxb-your-bot-token
SLACK_APP_TOKEN=xapp-your-app-token
SLACK_CHANNEL_ID=your-channel-id
```

## Environment variables

| Variable             | Required                     | Description                                            |
| -------------------- | ---------------------------- | ------------------------------------------------------ |
| `APP_ENV`            | Yes                          | Selects the environment file to load (`dev` or `prod`) |
| `DOCUMENTS_DIR`      | Yes                          | Base directory for user-scoped PDF storage             |
| `MAX_PDF_SIZE`       | No                           | Maximum accepted PDF size in bytes                     |
| `MAX_SEARCH_RESULTS` | No                           | Maximum search results returned                        |
| `LOGGING_LEVEL`      | No                           | Logging verbosity (`INFO`, `DEBUG`, etc.)              |
| `LLM_API_KEY`        | Yes for AI-powered assistant | API key for the LLM provider                           |
| `LLM_API_MODEL`      | No                           | Model name used by the assistant                       |
| `SLACK_BOT_TOKEN`    | Yes for Slack integration    | Bot token for Slack Socket Mode                        |
| `SLACK_APP_TOKEN`    | Yes for Slack integration    | App-level token for Socket Mode                        |
| `SLACK_CHANNEL_ID`   | Yes for Slack integration    | Channel where the app listens or posts                 |

Never commit real API keys or Slack tokens.

## Slack Configuration

The Slack app uses Socket Mode.

Required app-level scope:

```
connections:write
```

Bot scopes:

```
app_mentions:read
chat:write
users:read
users:read.email
```

After changing scopes, reinstall the Slack app.

Invite the bot to a channel:

```
/invite @pdf-assistant
```

## Running the MCP server

Start the MCP PDF server:

```bash
python -m mcp_pdf_finder.server
```

The server exposes these tools:

- `list_pdfs(user_id: str)`
- `pdf_info(user_id: str, filename: str)`
- `read_pdf(user_id: str, filename: str, page: int)`
- `search_pdf(user_id: str, filename: str, query: str)`
- `search_all_pdfs(user_id: str, query: str)`

## Slack assistant

The project includes a Slack bot that forwards user questions to the PDF assistant and uses the authenticated Slack user identity to scope all operations to that person's document repository.

Start the Slack app:

```bash
python -m mcp_pdf_finder.slack_app
```

The bot listens for app mentions and responds in thread with answers that use the available PDF tools.

## Example document layout

```text
documents/
├── dasarpsony/
│   ├── quarterly-report.pdf
│   └── onboarding-guide.pdf
└── user2/
    └── contract.pdf
```

The server validates all requested file access to ensure each operation remains inside that user's document directory.

## Running tests

```bash
pytest
```

## Notes

- The PDF service blocks paths that escape the configured user directory.
- Only PDF files are accepted for file lookups and reads.
- Search and read operations are scoped to the authenticated user, not the free-form text of the query.

## License

This project is intended for internal or local use unless otherwise specified by your organization.
