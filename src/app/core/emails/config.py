from pathlib import Path
from fastapi_mail import ConnectionConfig, FastMail
from pydantic import SecretStr
from core.settings import settings

TEMPLATE_FOLDER_PATH = Path(__file__).parent / "templates"

conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_FROM,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
    MAIL_PASSWORD=SecretStr(""),
    MAIL_PORT=settings.SMTP_PORT,
    MAIL_SERVER=settings.SMTP_HOST,
    MAIL_SSL_TLS=False,
    MAIL_STARTTLS=False,
    USE_CREDENTIALS=False,
    VALIDATE_CERTS=False,
    TEMPLATE_FOLDER=TEMPLATE_FOLDER_PATH,
)

fm = FastMail(conf)