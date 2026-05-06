from google import genai
from google.genai import types
import os

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

MODEL_ID="gemini-2.5-flash-preview-04-17"

prompt = """
   I am starting a AI/LLM consulting company. Suggest
   three different options for advertising services.
"""

response = client.models.generate_content(
    model=MODEL_ID,
    contents=prompt,
    config=types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(
            thinking_budget=500
        )
    )
)

print(response.text)