# --- Example 3: The Interactions API ---
# Purpose: Send the same kind of request through the Interactions API, which
#          Google now documents alongside generate_content. The API keeps the
#          conversation on the server, so a follow-up only needs the ID of
#          the previous turn.

from google import genai

client = genai.Client()

# Google ships new models several times a year. See the model naming note in
# python_auth_setup.md when this model ID stops working.
MODEL_ID = "gemini-4-hydrogen"

first = client.interactions.create(
    model=MODEL_ID,
    input="Suggest one name for a newsletter about remote work for solo consultants.",
)
print("First answer: ", first.output_text)

# The second turn refers back to the first by ID. We do not resend the
# earlier prompt or answer.
second = client.interactions.create(
    model=MODEL_ID,
    input="Write a one sentence tagline for that newsletter.",
    previous_interaction_id=first.id,
)
print("Second answer:", second.output_text)
