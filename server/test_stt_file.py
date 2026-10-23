import os
from dotenv import load_dotenv
from gnani.stt import GnaniSTTClient

load_dotenv()

api_key = os.getenv("GNANI_API_KEY")
if not api_key:
    raise RuntimeError("GNANI_API_KEY is missing from .env")

client = GnaniSTTClient(api_key=api_key)

result = client.transcribe(
    "kirana-test.wav",
    language_code="hi-IN",
    format="verbatim",
)

print("API response:")
print(result)
