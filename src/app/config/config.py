import os
from dotenv import load_dotenv

load_dotenv()

# DATABASE_URL="mysql://root:mysqlsane!4422@localhost/ticketSystem"
DATABASE_URL = "postgresql://postgres:postsane!4422@localhost:5432/chat_app"
SECRET_KEY="asdfghhtgbhhhyuiokmnbvcx"

class Settings:
    # DATABASE_URL: str = os.getenv("DATABASE_URL")
    DATABASE_URL: str = DATABASE_URL
    # SECRET_KEY: str = os.getenv("SECRET_KEY")
    SECRET_KEY: str = SECRET_KEY
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

settings = Settings()