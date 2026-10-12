# --- Example 2: Text Generation ---
# Purpose: Use the Gemini client to generate text
#          based on a given prompt.

from google import genai
import os

client = genai.Client(api_key=os.getenv('GOOGLE_API_KEY'))

# Google ships new Flash models several times a year. See the model naming
# note in python_auth_setup.md when this model ID stops working.
MODEL_ID = "gemini-3.8-flash"

# Define the prompt (your instruction to the model)
prompt = "Brainstorm 5 blog post ideas about remote work productivity for solo knowledge workers."

# Generate content by calling the model. This makes the actual API request.
response = client.models.generate_content(
    model=MODEL_ID,
    contents=prompt,
)

# Responses can be empty when safety filters block them, so check for text.
print("\n--- Blog Post Ideas ---")
if response.text:
    print(response.text)
else:
    print("Response was empty or potentially blocked.")
