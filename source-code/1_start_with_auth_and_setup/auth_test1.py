# --- Example 1: Basic Authentication & Setup ---
# Purpose: Confirm that your API key works by creating a Gemini client and
#          listing the models you can call.

import os
import sys

from google import genai

# Best practice: store your API key in an environment variable rather than
# in your source code. The client reads GOOGLE_API_KEY or GEMINI_API_KEY.
# If both are set, GOOGLE_API_KEY wins.
if not (os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")):
    print("Error: set the GOOGLE_API_KEY environment variable to your API key.")
    print("Create a key at https://aistudio.google.com/app/api-keys")
    sys.exit(1)

try:
    client = genai.Client()
    print(f"google-genai SDK version: {genai.__version__}")

    # The full list includes speech, embedding, and live audio models. Show
    # only the models that answer text prompts with generate_content.
    print("\nModels that support generate_content:")
    for m in client.models.list():
        if "generateContent" in (m.supported_actions or []):
            print(f"  {m.name.removeprefix('models/'):40} {m.display_name}")

except Exception as e:
    # An invalid key produces a 400 INVALID_ARGUMENT error with API_KEY_INVALID.
    print(f"An error occurred: {e}")
    sys.exit(1)
