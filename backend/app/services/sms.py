from abc import ABC, abstractmethod
from app.core.logging import logger

class BaseSMSService(ABC):
    @abstractmethod
    async def send_sms(self, phone_number: str, message: str) -> bool:
        pass

class ConsoleSMSService(BaseSMSService):
    """Development SMS service logging OTP messages to output."""
    async def send_sms(self, phone_number: str, message: str) -> bool:
        logger.info(
            f"--- [DEV SMS SENT] ---\n"
            f"To: {phone_number}\n"
            f"Message: {message}\n"
            f"----------------------"
        )
        return True

def get_sms_service() -> BaseSMSService:
    return ConsoleSMSService()
