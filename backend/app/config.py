from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    mongo_url: str = "mongodb://localhost:27017"
    mongo_db: str = "rateright"
    openai_api_key: Optional[str] = None
    serpapi_key: Optional[str] = None
    linkup_api_key: Optional[str] = None
    linkup_only: bool = False

    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    imap_host: str = ""
    imap_port: int = 993
    from_email: str = ""

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
