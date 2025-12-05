import asyncio

from fastapi_mail import MessageSchema, MessageType, MultipartSubtypeEnum, NameEmail
from core.celery_app import celery_app
from core.logger import get_logger
from core.emails.config import fm

logger = get_logger()

@celery_app.task(
    name="send_email_task",
    bind=True,
    max_retries=3,
    soft_time_limit=30,
    auto_retry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=60,
)
def send_email_task(
    self,
    *,
    recipients: list[str],
    subject: str,
    htpm_content: str, 
    plain_content: str = "",
) -> bool:
    """Send an email asynchronously using FastAPI-Mail and Celery.

    Args:
        recipients (list[str]): List of recipient email addresses.
        subject (str): Subject of the email.
        htpm_content (str): HTML content of the email.
        plain_content (str, optional): Plain text content of the email. Defaults to "".

    Returns:
        bool: True if the email was sent successfully, False otherwise.
    """
    try:
        message = MessageSchema(
            subject=subject,
            recipients=[NameEmail(name="", email=email) for email in recipients],
            body=htpm_content,
            subtype=MessageType.html,
            alternative_body=plain_content,
            multipart_subtype=MultipartSubtypeEnum.alternative,
        )

        loop = asyncio.get_event_loop()
        loop.run_until_complete(fm.send_message(message))
        logger.info(f"Email sent to {recipients} with subject '{subject}'")
        return True
    except Exception as e:
        logger.error(f"Failed to send email to {recipients} with subject '{subject}': {e}")
        return False