from dataclasses import dataclass
import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic import SecretStr


PROJECT_ROOT = Path(__file__).resolve().parents[2]

APP_ENV = os.getenv("APP_ENV", "dev")

ENV_FILES = {
    "dev": ".dev.env",
    "prod": ".prod.env",
}

env_file = ENV_FILES.get(APP_ENV)

if env_file is None:
    raise ValueError(
        f"Unsupported APP_ENV: {APP_ENV}"
    )
    
load_dotenv(PROJECT_ROOT / env_file)


def resolve_project_path(value: str) -> Path:
    path = Path(value)

    if not path.is_absolute():
        path = PROJECT_ROOT / path

    return path.resolve()


def get_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)

    if value is None:
        return default

    return value.lower() in {
        "true",
        "1",
        "yes",
        "on",
    }


@dataclass(frozen=True)
class Settings:
    app_env: str
    documents_dir: Path
    max_pdf_size: int
    max_search_results: int

    logging_directory: Path
    logging_level: str

    ocr_enabled: bool
    ocr_model: str
    ocr_device: str
    
    llm_api_key: SecretStr
    llm_api_model: str
    
    slack_app_token: SecretStr
    slack_bot_token: SecretStr
    slack_channel_id: str


def load_settings() -> Settings:
    return Settings(
        app_env=APP_ENV,

        documents_dir=resolve_project_path(
            os.getenv(
                "DOCUMENTS_DIR",
                "documents",
            )
        ),

        max_pdf_size=int(
            os.getenv(
                "MAX_PDF_SIZE",
                "50000000",
            )
        ),

        max_search_results=int(
            os.getenv(
                "MAX_SEARCH_RESULTS",
                "50",
            )
        ),

        logging_directory=PROJECT_ROOT / "logs",
        
        logging_level=os.getenv(
            "LOGGING_LEVEL",
            "INFO",
        ).upper(),

        ocr_enabled=get_bool(
            "OCR_ENABLED",
            False,
        ),

        ocr_model=os.getenv(
            "OCR_MODEL",
            "baidu/Unlimited-OCR",
        ),

        ocr_device=os.getenv(
            "OCR_DEVICE",
            "cuda",
        ),
        
        llm_api_key=SecretStr(
            os.getenv(
                "LLM_API_KEY",
                "",
            )
        ),
        
        llm_api_model=os.getenv(
            "LLM_API_MODEL",
            "openai/gpt-oss-120b",
        ),
        
        slack_app_token=SecretStr(
            os.getenv(
                "SLACK_APP_TOKEN",
                "",
            )
        ),
        
        slack_bot_token=SecretStr(
            os.getenv(
                "SLACK_BOT_TOKEN",
                "",
            )
        ),
        
        slack_channel_id=os.getenv(
            "SLACK_CHANNEL_ID",
            "",
        ),
    )


settings = load_settings()