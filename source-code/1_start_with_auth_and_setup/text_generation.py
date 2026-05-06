from google import genai
import os
import sys

# Best practice: Store your API key in an environment variable
# (e.g., GOOGLE_API_KEY) rather than hardcoding it.
# You can set this in your system or using a .env file with python-dotenv.
try:
    client = genai.Client(api_key=os.getenv('GOOGLE_API_KEY'))

    # Define the prompt
    prompt = "Brainstorm 5 blog post ideas about remote work productivity for solo knowledge workers."

    # Generate content
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt
    )

    # Print the generated text
    print("\n--- Blog Post Ideas ---")
    # Basic error check for blocked content
    if response.text:
        print(response.text)
    else:
        print("Response was empty or blocked.")


except AttributeError:
    print("Error: Gemini API likely not configured. Run Example 1 first.")
except Exception as e:
    print(f"An error occurred during text generation: {e}")