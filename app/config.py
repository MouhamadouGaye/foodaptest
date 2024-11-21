from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SECRET_KEY: str  # This will hold your secret key
    ALGORITHM: str ="HS256" # This sets the default algorithm
    DATABASE_URL:str
    MY_GMAIL_SECRET_KEY_CONTACT: str  # Add this field if you need it

    class Config:
        env_file = ".env"  # This allows you to load settings from a .env file

# Create an instance of the Settings class
settings = Settings()


