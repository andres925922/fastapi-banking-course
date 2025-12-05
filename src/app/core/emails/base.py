from typing import List
from jinja2 import Environment, FileSystemLoader, select_autoescape
from core.logger import get_logger
from core.emails.config import TEMPLATE_FOLDER_PATH
from core.emails.tasks import send_email_task

logger = get_logger()

email_env = Environment(
    loader=FileSystemLoader(TEMPLATE_FOLDER_PATH),
    autoescape=True,
)

class EmailTemplate:
    template_name: str
    template_name_plain: str
    subject: str

    @classmethod
    def send_email(
        cls, 
        email_to: str | List[str], 
        context: dict, 
        subject_override: str | None = None) -> None:
        """Render the email template and send the email asynchronously.

        Args:
            email_to (str | list[str]): Recipient email address or list of email addresses.
            context (dict): Context data for rendering the template.
            subject_override (str | None): Optional subject override for the email.
        Returns:
            bool: True if the email was sent successfully, False otherwise.
        """
        try:
            recipients = [email_to] if isinstance(email_to, str) else email_to
            if not cls.template_name or not cls.template_name_plain:
                raise ValueError("Template names must be defined.")
            
            html_template = email_env.get_template(cls.template_name)
            plain_template = email_env.get_template(cls.template_name_plain)

            html_content = html_template.render(**context)
            plain_content = plain_template.render(**context)

            task = send_email_task.delay(
                recipients=recipients,
                subject=subject_override or cls.subject,
                htpm_content=html_content,
                plain_content=plain_content,
            )
            logger.info(f"Email task {task.id} queued for recipients: {recipients}")

        except Exception as e:
            logger.error(f"Failed to send email: {e} | Template: {cls.template_name} | Recipients: {email_to}")
            raise