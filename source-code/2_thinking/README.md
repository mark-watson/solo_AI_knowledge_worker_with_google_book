# Gemini Thinking Levels Example

This directory contains a simple example of Gemini's thinking feature, where the model reasons internally before it produces its final answer.

## Prerequisites

- Python 3.12 or newer
- A `GOOGLE_API_KEY` environment variable set with your Google AI API key

Install dependencies with `uv`:

```bash
uv sync
```

## Script

### `demo_1.py`

Sends a consulting-oriented prompt to Gemini with `thinking_level="high"`. The model reasons at length before answering, which often produces a more structured response.

```bash
uv run python demo_1.py
```

## Key Concepts

- **ThinkingConfig**: `types.ThinkingConfig(thinking_level="high")` sets how much internal reasoning the model does. Accepted levels are `minimal`, `low`, `medium`, and `high`, and each model supports a subset of them. Gemini 3.8 Flash supports `low`, `medium`, and `high`.
- **Model ID Constant**: `MODEL_ID` is defined once per file. Change that one line when Google ships a newer Flash model.
- **Legacy Alternative**: `thinking_budget`, a token count, is the older Gemini 2.5 control. It still works on Gemini 3 models, but new code should use `thinking_level`.
