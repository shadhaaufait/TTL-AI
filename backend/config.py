import os
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()

# Correct way to read your OpenAI key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("❌ OPENAI_API_KEY not found. Please set it in your .env file.")

