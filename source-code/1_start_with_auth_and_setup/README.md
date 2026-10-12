# Authentication and Setup for Google Gemini API

![System Design](FIG_1_start_with_auth_and_setup.jpg)

This directory contains two starter scripts that show how to authenticate with the Google Gemini API and generate text.

## Prerequisites

- Python 3.12 or newer
- A `GOOGLE_API_KEY` environment variable set with your Google AI API key

Install dependencies with `uv`:

```bash
uv sync
```

## Scripts

### `auth_test1.py`

Verifies that your API key is configured correctly by initializing the `genai.Client` and listing all available Gemini models. Run this first to confirm your setup works.

```bash
uv run python auth_test1.py
```

### `text_generation.py`

Generates text with the `gemini-3.8-flash` model. It sends a brainstorming prompt and prints the AI-generated response.

```bash
uv run python text_generation.py
```

## Key Concepts

- **API Key Authentication**: The scripts use `os.getenv('GOOGLE_API_KEY')` to load the API key from the environment rather than hardcoding it.
- **Client Initialization**: `genai.Client(api_key=...)` creates a reusable client for all Gemini API interactions.
- **Content Generation**: `client.models.generate_content()` sends a prompt and returns the model response.
- **Model ID Constant**: `MODEL_ID` is defined once per file. Change that one line when Google ships a newer Flash model.
