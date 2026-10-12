# Gemini Thinking Levels and Extended Reasoning

**Introduction**

In the previous chapter, we covered authenticating with the Gemini API and performing basic text generation using the Python SDK. Those examples asked for a direct answer to a prompt. Some tasks do better when the model takes time to plan before it writes the answer. Gemini exposes that planning as a feature you control, and this chapter shows how.

Three terms appear in Google's documentation and in this book:

- **Thinking** is the model's internal reasoning before it produces the answer you see.
- **Thinking level** is the setting that decides how much of that reasoning happens. It is a coarse setting: minimal, low, medium, or high.
- **Thinking budget** is the older setting, which asked for a number of tokens instead of a level. `thinking_budget` still works on Gemini 3 models as a compatibility path, but thinking level is what new code should use.

## When to Raise the Thinking Level

Standard generation is fast and good enough for most prompts. Raised thinking levels help when:

1.  **Complex problem solving.** The prompt requires breaking a problem into steps, weighing several approaches, or synthesizing information from many angles. For example: "Develop a phased marketing strategy for launching a new SaaS product that targets small businesses."
2.  **Detailed analysis or summarization.** You need a close reading of a complex document and a nuanced summary or critique.
3.  **Creative work that needs planning.** Long stories, complex code, and detailed project plans all improve when the model structures them first.
4.  **Multi-step instructions.** The prompt contains several dependent instructions that the model must handle in order.

For simple prompts such as "What is the capital of France?", a higher thinking level only adds latency.

A word of caution about cost. You pay for thinking tokens even though you never see them. Raising the level on a prompt that does not need it is the easiest way to spend money for nothing. Start at the default, raise the level when the output is visibly shallow, and lower it for bulk work.

## Setting the Thinking Level with the Python SDK

Two objects from `google.genai.types` are involved:

1.  **`types.GenerateContentConfig`** holds the generation settings, including the thinking configuration.
2.  **`types.ThinkingConfig`** holds the thinking setting. Set `thinking_level` on it.

The accepted values are `"minimal"`, `"low"`, `"medium"`, and `"high"`. Not every model accepts every value. Gemini 3.8 Flash supports `low`, `medium`, and `high`, and asks for `minimal` is an error. Gemini 3.6 Flash and the Flash-Lite models accept all four. When you switch models, check the model page for the levels it supports.

**Client initialization:** As in the previous chapter, we use `genai.Client(api_key=...)` to create a client that authenticates with your API key.

## Example: `demo_1.py` - Advertising Strategy Brainstorm

This script asks for advertising ideas for a new consulting company. The task rewards structure, so it asks for a high thinking level.

```python
from google import genai
from google.genai import types
import os

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

# Google ships new Flash models several times a year. See the model naming
# note in python_auth_setup.md when this model ID stops working.
MODEL_ID = "gemini-3.8-flash"

prompt = """
   I am starting a AI/LLM consulting company. Suggest
   three different options for advertising services.
"""

response = client.models.generate_content(
    model=MODEL_ID,
    contents=prompt,
    config=types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(
            thinking_level="high"
        )
    )
)

print(response.text)
```

**Explanation:**

1.  **Imports:** `google.genai`, `google.genai.types` for `GenerateContentConfig` and `ThinkingConfig`, and `os`.
2.  **Client Initialization:** `genai.Client()` authenticates using the `GOOGLE_API_KEY` environment variable.
3.  **Model ID:** One `MODEL_ID` constant, so a model change is a one line edit.
4.  **Prompt:** A moderately complex prompt that asks for structured suggestions, which suits a raised thinking level.
5.  **`generate_content` call:**
    * `model` and `contents` work as before.
    * `config=types.GenerateContentConfig(...)` passes the advanced settings.
    * `thinking_config=types.ThinkingConfig(thinking_level="high")` asks the model to reason at length before answering.
6.  **Output:** `response.text` holds the advertising options.

This example generates a report that runs several pages. Here is the beginning of the output:

```text
Okay, starting an AI/LLM consulting company is exciting! Since it's a B2B service focused on technology and strategy, your advertising needs to reach business decision-makers and demonstrate expertise. Here are three distinct options for advertising your services:

**Targeted Content Marketing & LinkedIn Advertising:**

**Strategy:** Position yourself as a thought leader and educator in the AI/LLM space. Create valuable content that addresses the pain points and opportunities businesses face with AI (e.g., improving customer service with chatbots, automating tasks, leveraging data with LLMs, ethical considerations, choosing the right models).

**Tactics:**
-   **Blog Posts/Articles:** Write detailed articles on your website covering specific use cases, implementation strategies, benefits, and challenges.
-   **Whitepapers/Ebooks:** Offer downloadable, in-depth guides on topics like "The Executive's Guide to Implementing AI in [Industry]" or "Evaluating LLM Solutions for Your Business."
-   **Webinars/Online Workshops:** Host free sessions demonstrating how AI/LLMs can solve specific business problems. This allows direct interaction and showcases expertise.
-   **Case Studies:** Showcase successful projects (anonymized if necessary) highlighting the business results you achieved for clients.
...
```

Run the example to see the full report.

## Seeing the Difference

This example does not run a side by side comparison, but if you run the same complex prompt at two thinking levels you will notice:

* **At a higher level:** The output tends to be more structured, covers more of the prompt, and shows its reasoning in the organization of the answer.
* **At a lower level:** The output can still be good, but it is more likely to miss nuance on a complex request.
* **Latency:** A higher level takes longer, because the model reasons before it answers.
* **Cost:** You pay for the thinking tokens, so the higher level costs more for the same visible answer.

The cheapest way to decide is to run the prompt at the default level, read the answer, and raise the level only if the answer is shallow.

## Compatibility with Gemini 2.5 Models

Gemini 2.5 models predate thinking levels. They were controlled with `thinking_budget`, a token count:

```python
config=types.GenerateContentConfig(
    thinking_config=types.ThinkingConfig(
        thinking_budget=500
    )
)
```

The Gemini 3 models still accept `thinking_budget` for compatibility, so this code runs, but it is the legacy path. Two limits are worth knowing. First, `thinking_budget=0` used to turn thinking off on 2.5 models, and on Gemini 3 models thinking cannot be fully disabled. Second, a budget is harder to reason about than a level, because the same budget means different amounts of work on different models. Use `thinking_level` in new code. Reach for `thinking_budget` only when you must keep an older script running unchanged.

## Wrap Up

Thinking level is the current way to control how much Gemini reasons before it answers. Set `thinking_level` on a `types.ThinkingConfig` inside a `types.GenerateContentConfig`, and choose a level that matches the difficulty of the task. Remember four points:

- Raise the level for multi-step analysis and planning, and leave it alone for simple prompts.
- You pay for thinking tokens, so a high level on a trivial prompt is wasted money.
- Gemini 3.8 Flash supports `low`, `medium`, and `high`, but not `minimal`, and you cannot turn thinking off completely on Gemini 3 models.
- `thinking_budget` is the legacy control for Gemini 2.5 models. It still works, but new code should use `thinking_level`.

In the next chapter we add images to the prompt and use a low thinking level to keep the answers fast.
