# config.py
import os
from dotenv import load_dotenv

load_dotenv()  

TOKEN = os.getenv("DORF_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

if not TOKEN:
    raise RuntimeError("DORF_TOKEN is not set in environment variables")
