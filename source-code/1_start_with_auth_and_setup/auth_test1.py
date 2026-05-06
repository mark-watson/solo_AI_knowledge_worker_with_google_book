# --- Example 1: Basic Authentication & Setup ---
# Purpose: Configure the Gemini API client using an API key
#          stored securely in an environment variable.

from google import genai
import os
import sys

# Best practice: Store your API key in an environment variable
# (e.g., GOOGLE_API_KEY) rather than hardcoding it.
# You can set this in your system or using a .env file with python-dotenv.
try:
    client = genai.Client(api_key=os.getenv('GOOGLE_API_KEY'))

    # Verify configuration by listing available models (optional)
    print("\nAvailable models:")
    for m in client.models.list():
        print(m.name)

except KeyError:
    print("Error: GOOGLE_API_KEY environment variable not found.")
    print("Please set the GOOGLE_API_KEY environment variable with your API key.")
except Exception as e:
    print(f"An error occurred during configuration: {e}")
