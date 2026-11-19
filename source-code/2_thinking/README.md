# Gemini Thinking Levels Example

This directory contains a simple example of Gemini's thinking feature, where the model reasons internally before it writes its final answer.

## Prerequisites

- Python 3.12 or newer
- A `GOOGLE_API_KEY` environment variable set with your Gemini API key

Install dependencies with `uv`:

```bash
uv sync
```

## Script

### `demo_1.py`

Sends a consulting prompt to Gemini twice, once with `thinking_level="low"` and once with `thinking_level="high"`. For each run it prints the time taken, the number of thinking tokens, the number of answer tokens, and the answer.

```bash
uv run python demo_1.py
```

## Key Concepts

- **ThinkingConfig**: `types.ThinkingConfig(thinking_level="high")` sets how much the model reasons. The levels are `minimal`, `low`, `medium`, `high`, and `xhigh`, and each model supports a subset. Gemini 4 Hydrogen supports `low` through `xhigh` and defaults to `high`.
- **Thinking costs tokens**: `response.usage_metadata.thoughts_token_count` reports the thinking tokens you pay for but never see.
- **Model ID Constant**: `MODEL_ID` is defined once per file. Change that one line when Google ships a newer model.
- **Legacy control**: `thinking_budget`, a token count, was the Gemini 2.5 control. Google lists replacing it with `thinking_level` as a required change when you move off 2.5 models.
