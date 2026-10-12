from google import genai
from google.genai import types
from PIL import Image

import os

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

# Google ships new Flash models several times a year. See the model naming
# note in python_auth_setup.md when this model ID stops working.
MODEL_ID = "gemini-3.8-flash"

prompt = """
    Return bounding boxes around people as a JSON array with labels. Never return masks or code fencing. Limit to 10 people.
    Describe each person identified in a picture.
      """

image_path = os.path.join(os.getcwd(), "..", "data", "poker.jpeg")

im = Image.open(image_path)

# Gemini 3.8 Flash cannot turn thinking off completely. Use the lowest
# thinking level when you want the fastest answer.
response = client.models.generate_content(
    model=MODEL_ID,
    contents=[prompt, im],
    config=types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(
            thinking_level="low"
        )
    )
)

print(response.text)

prompt2 = """
    Return bounding boxes around people as a JSON array with labels. Never return masks or code fencing. Limit to 10 people.
    Describe each person identified in a picture, specifically what they are holding in their hands.
      """

response = client.models.generate_content(
    model=MODEL_ID,
    contents=[prompt2, im],
    config=types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(
            thinking_level="low"
        )
    )
)

print(response.text)
