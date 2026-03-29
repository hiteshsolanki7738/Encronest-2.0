# config.py
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ---------------------------
# Helper function
# ---------------------------
def get_env_variable(name):
    value = os.getenv(name)
    if value is None or value.strip() == "":
        print(f"⚠️ Warning: {name} not set in .env file")
        return None
    return value.strip()

# ---------------------------
# Supabase
# ---------------------------
SUPABASE_URL = get_env_variable("SUPABASE_URL")
SUPABASE_KEY = get_env_variable("SUPABASE_KEY")

# ---------------------------
# Email (Gmail)
# ---------------------------
EMAIL_ADDRESS = get_env_variable("EMAIL_ADDRESS")
EMAIL_PASSWORD = get_env_variable("EMAIL_PASSWORD")

# ---------------------------
# Twilio
# ---------------------------
TWILIO_SID = get_env_variable("TWILIO_SID")
TWILIO_AUTH = get_env_variable("TWILIO_AUTH")
TWILIO_PHONE = get_env_variable("TWILIO_PHONE")

# ---------------------------
# Optional: OpenAI
# ---------------------------
OPENAI_API_KEY = get_env_variable("OPENAI_API_KEY")