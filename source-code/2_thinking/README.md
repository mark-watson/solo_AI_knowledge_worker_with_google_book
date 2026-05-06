# Gemini Thinking Mode Example

This directory contains a simple example demonstrating Gemini's "thinking" (reasoning) mode, where the model allocates a dedicated token budget for internal chain-of-thought reasoning before producing its final answer.

## Prerequisites

- Python 3.10+
- A `GOOGLE_API_KEY` environment variable set with your Google AI API key

Install dependencies:

```bash
pip install -r requirements.txt
```

## Script

### `demo_1.py`

Sends a consulting-oriented prompt to Gemini with a `thinking_budget` of 500 tokens. This causes the model to perform internal reasoning before responding, often producing more structured and higher-quality output.

```bash
python demo_1.py
```

## Key Concepts

- **ThinkingConfig**: The `types.ThinkingConfig(thinking_budget=500)` parameter tells Gemini how many tokens to dedicate to internal reasoning before generating the visible response.
- **Use Case**: Thinking mode is especially useful for complex tasks like brainstorming, planning, and analysis where deeper reasoning improves output quality.
