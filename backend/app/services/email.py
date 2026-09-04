from abc import ABC, abstractmethod
from typing import Optional
from app.core.config import settings
from app.core.logging import logger

class BaseEmailService(ABC):
    @abstractmethod
    async def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        html_body: Optional[str] = None
    ) -> bool:
        pass

class ConsoleEmailService(BaseEmailService):
    """Development Email Service logging email payloads to system logger/stdout."""
    async def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        html_body: Optional[str] = None
    ) -> bool:
        logger.info(
            f"--- [DEV EMAIL SENT] ---\n"
            f"To: {to_email}\n"
            f"Subject: {subject}\n"
            f"Body:\n{body}\n"
            f"------------------------"
        )
        return True

def get_email_service() -> BaseEmailService:
    return ConsoleEmailService()
