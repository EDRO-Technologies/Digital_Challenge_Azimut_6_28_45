import os
from dotenv import load_dotenv
load_dotenv()

model_url = os.getenv("MODEL_URL", "")
model_name = os.getenv("MODEL_NAME", "")
gigachat_token = os.getenv("GIGACHAT_TOKEN", "")


CONFIG = {
    'host': os.getenv("DB_HOST", ""),
    'port': os.getenv("DB_PORT", ""),
    'user': os.getenv("DB_USER", ""),
    'password': os.getenv("DB_PASSWORD", ""),
    'database': 'XakatonBaza',
    'autocommit': True
}