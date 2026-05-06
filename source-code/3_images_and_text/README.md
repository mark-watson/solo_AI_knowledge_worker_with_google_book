# Using Gemini with Images — Multimodal Photo Understanding

![System Design](FIG_3_images_and_text.jpg)

This directory demonstrates Gemini's multimodal capabilities by sending an image along with a text prompt to the API. The script analyzes a photograph and returns structured JSON with bounding boxes and descriptions of people in the image.

## Prerequisites

- Python 3.10+
- A `GOOGLE_API_KEY` environment variable set with your Google AI API key

Install dependencies:

```bash
pip install -r requirements.txt
```

## Script

### `photo_understanding.py`

Loads an image (`../data/poker.jpeg`) using PIL, sends it to Gemini with two successive prompts:
1. **General identification** — detects people and returns bounding boxes with descriptions
2. **Detailed analysis** — focuses on what each person is holding in their hands

```bash
python photo_understanding.py
```

### Example Output

```json
[
  {"box_2d": [204, 156, 467, 348], "label": "a man with a grey sweater and black shirt is sitting at a table"},
  {"box_2d": [255, 0, 998, 331], "label": "a man with a black baseball cap is sitting at a table"},
  {"box_2d": [178, 596, 998, 998], "label": "a man with a green shirt is sitting at a table"},
  {"box_2d": [257, 734, 525, 875], "label": "a woman with a white shirt and a purple scarf is sitting at a table"},
  {"box_2d": [198, 435, 393, 629], "label": "a woman with a red scarf is sitting at a table"}
]
```

## Key Concepts

- **Multimodal Input**: Gemini accepts a list of `[prompt, image]` as the `contents` parameter, enabling combined text+image reasoning.
- **Bounding Box Detection**: The prompt instructs Gemini to return structured JSON with `box_2d` coordinates and `label` descriptions.
- **ThinkingConfig with budget=0**: Disables internal reasoning for faster, more direct responses when deep analysis isn't needed.