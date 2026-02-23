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
    password_reset_otp_expiration_minutes: int
    email_verification_otp_expiration_minutes: int
    user_invitation_token_expiration_minutes: int
    otp_expiration_minutes: int
    sign_up_complete_expiration_days: int
    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()