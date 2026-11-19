import pathlib
import sys

from google import genai
from google.genai import types
from PIL import Image
from pydantic import BaseModel, Field

client = genai.Client()

# Google ships new models several times a year. See the model naming note in
# python_auth_setup.md when this model ID stops working.
MODEL_ID = "gemini-4-hydrogen"

IMAGE_PATH = pathlib.Path(__file__).parent.parent / "data" / "poker.jpeg"


class Person(BaseModel):
    box_2d: list[int] = Field(
        description="Bounding box as [ymin, xmin, ymax, xmax], scaled to 0-1000."
    )
    description: str = Field(description="What the person looks like.")
    holding: str = Field(description="What the person holds in their hands.")


def describe_people(image):
    response = client.models.generate_content(
        model=MODEL_ID,
        contents=[
            "Find up to 10 people in this picture. For each person, give a "
            "bounding box, a short description, and what they hold in their hands.",
            image,
        ],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=list[Person],
            thinking_config=types.ThinkingConfig(thinking_level="low"),
        ),
    )
    return response.parsed


def summarize_scene(image):
    response = client.models.generate_content(
        model=MODEL_ID,
        contents=["Describe what is happening in this picture in three sentences.", image],
        config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_level="low"),
        ),
    )
    return response.text


try:
    im = Image.open(IMAGE_PATH)
except FileNotFoundError:
    sys.exit(f"Image not found: {IMAGE_PATH}")

people = describe_people(im)
print(f"Found {len(people)} people:\n")
for i, person in enumerate(people, 1):
    print(f"{i}. box={person.box_2d}")
    print(f"   {person.description}")
    print(f"   holding: {person.holding}")

print("\nScene summary:")
print(summarize_scene(im))
