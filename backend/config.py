import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://root:root123@localhost:3306/embodied_ai")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")