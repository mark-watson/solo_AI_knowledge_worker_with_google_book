from google import genai
from google.genai import types
import os

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

# Google ships new Flash models several times a year. See the model naming
# note in python_auth_setup.md when this model ID stops working.
MODEL_ID = "gemini-3.8-flash"

prompt = """
   I am starting a AI/LLM consulting company. Suggest
   three different options for advertising services.
"""

response = client.models.generate_content(
    model=MODEL_ID,
    contents=prompt,
    config=types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(
            thinking_level="high"
        )
    )
)

print(response.text)
