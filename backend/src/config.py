import os

from dotenv import load_dotenv

load_dotenv()


def get_env_variable(name: str) -> str:
    value = os.getenv(name)
    if value is None:
        raise ValueError(f"Missing required environment variable: {name}")
    return value


# DATABASE_URL = get_env_variable("DATABASE_URL")
TWITTER_CLIENT_ID = get_env_variable("TWITTER_CLIENT_ID")
TWITTER_CLIENT_SECRET = get_env_variable("TWITTER_CLIENT_SECRET")
SECRET_KEY = get_env_variable("SECRET_KEY")


DB_USER = get_env_variable("DB_USER")
DB_PASSWORD = get_env_variable("DB_PASSWORD")
DB_HOST = get_env_variable("DB_HOST")
DB_PORT = get_env_variable("DB_PORT")
DB_NAME = get_env_variable("DB_NAME")

DATABASE_URL = (
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)
