from google import genai
import os

client = genai.Client(api_key=os.getenv('GOOGLE_API_KEY'))

# Google ships new Flash models several times a year. See the model naming
# note in python_auth_setup.md when this model ID stops working.
MODEL_ID = "gemini-3.8-flash"

# Define the prompt
prompt = "Brainstorm 5 blog post ideas about remote work productivity for solo knowledge workers."

# Generate content
response = client.models.generate_content(
    model=MODEL_ID,
    contents=prompt
)

# Print the generated text
print("\n--- Blog Post Ideas ---")
# Basic error check for blocked content
if response.text:
    print(response.text)
else:
    print("Response was empty or blocked.")
