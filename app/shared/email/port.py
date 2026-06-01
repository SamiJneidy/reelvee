from abc import ABC, abstractmethod


class EmailService(ABC):
    """Abstract interface for all transactional email sending."""

    @abstractmethod
    async def send_welcome_email(self, email: str) -> None: ...

    @abstractmethod
    async def send_onboarding_email(
        self, email: str, *, first_name: str | None, store_url: str
    ) -> None: ...

    @abstractmethod
    async def send_email_verification_otp(self, email: str, code: str) -> None: ...

    @abstractmethod
    async def send_password_reset_link(self, email: str, link: str) -> None: ...

    @abstractmethod
    async def send_email_change_link(self, email: str, link: str) -> None: ...
