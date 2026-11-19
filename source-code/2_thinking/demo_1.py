import time

from google import genai
from google.genai import types

client = genai.Client()

# Google ships new models several times a year. See the model naming note in
# python_auth_setup.md when this model ID stops working.
MODEL_ID = "gemini-4-hydrogen"

prompt = """
   I am starting an AI/LLM consulting company. Suggest
   three different options for advertising services.
"""


def ask(thinking_level):
    start = time.perf_counter()
    response = client.models.generate_content(
        model=MODEL_ID,
        contents=prompt,
        config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_level=thinking_level)
        ),
    )
    seconds = time.perf_counter() - start

    usage = response.usage_metadata
    print(f"\n===== thinking_level={thinking_level} =====")
    print(f"time: {seconds:.1f}s  "
          f"thinking tokens: {usage.thoughts_token_count or 0}  "
          f"answer tokens: {usage.candidates_token_count}")
    print(response.text)


for level in ["low", "high"]:
    ask(level)
