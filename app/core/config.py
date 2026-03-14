from fastapi_mail import ConnectionConfig
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    mongodb_uri: str
    mongodb_name: str
    environment: str
    maximum_number_of_invalid_login_attempts: int
    secret_key: str
    algorithm: str
    access_token_expiration_minutes: int
    refresh_token_expiration_days: int
    password_reset_token_expiration_minutes: int
    email_verification_otp_expiration_minutes: int
    email_change_token_expiration_minutes: int
    user_invitation_token_expiration_minutes: int
    otp_expiration_minutes: int
    sign_up_complete_expiration_days: int
    frontend_url: str

    # AWS
    aws_access_key_id: str
    aws_secret_access_key: str
    aws_region: str
    aws_bucket: str
    aws_presigned_url_expiration_seconds: int

    # Mail
    mail_username: str
    mail_password: str
    mail_from: str
    mail_port: int
    mail_server: str
    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()

mail_config = ConnectionConfig(
    MAIL_USERNAME=settings.mail_username,
    MAIL_PASSWORD=settings.mail_password,
    MAIL_FROM=settings.mail_from,
    MAIL_PORT=settings.mail_port,
    MAIL_SERVER=settings.mail_server,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
)