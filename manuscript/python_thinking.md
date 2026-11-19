# Gemini Thinking Levels and Extended Reasoning

**Introduction**

In the previous chapter, we authenticated with the Gemini API and generated text with the Python SDK. Those examples asked for a direct answer to a prompt. Some tasks go better when the model plans before it writes the answer. Gemini lets you control that planning, and this chapter shows how.

Three terms appear in Google's documentation and in this book:

- **Thinking** is the model's internal reasoning before it produces the answer you see.
- **Thinking level** is the setting that decides how much reasoning happens. It is a coarse setting: `minimal`, `low`, `medium`, `high`, or `xhigh`.
- **Thinking budget** is the older Gemini 2.5 setting, which asked for a number of tokens instead of a level. New code should use thinking level.

## When to Raise the Thinking Level

Raised thinking levels help when:

1.  **The problem is complex.** The prompt requires breaking a problem into steps, weighing several approaches, or pulling together information from many angles. For example: "Develop a phased marketing strategy for launching a new SaaS product that targets small businesses."
2.  **You need detailed analysis.** You want a close reading of a complex document and a careful summary or critique.
3.  **Creative work needs planning.** Long stories, complex code, and detailed project plans all improve when the model structures them first.
4.  **The prompt has several steps.** The prompt contains dependent instructions that the model must handle in order.

For simple prompts such as "What is the capital of France?", a higher thinking level only adds delay.

A word of caution about cost. You pay for thinking tokens even though you never see them. Raising the level on a prompt that does not need it is the easiest way to spend money for nothing. Start at the default, raise the level when the output is visibly shallow, and lower it for bulk work.

## Setting the Thinking Level with the Python SDK

Two classes from `google.genai.types` are involved:

1.  **`types.GenerateContentConfig`** holds the generation settings, including the thinking configuration.
2.  **`types.ThinkingConfig`** holds the thinking setting. Set `thinking_level` on it.

Not every model accepts every level, and each model has its own default. Here are the current models as of November 2026:

| Model | Levels accepted | Default |
| --- | --- | --- |
| `gemini-4-hydrogen`, `gemini-4-neon` | `low`, `medium`, `high`, `xhigh` | `high` |
| `gemini-4-carbon`, `gemini-4-argon` | `low`, `medium`, `high` | `medium` |
| `gemini-3.8-flash` | `low`, `medium`, `high` | `medium` |
| `gemini-3.6-flash`, Flash-Lite models | `minimal`, `low`, `medium`, `high` | varies |

A level the model does not accept produces an error. For example, asking `gemini-3.8-flash` for `xhigh` returns `400 INVALID_ARGUMENT` with the message "Thinking level XHIGH is not supported for this model." When you switch models, check the [thinking page](https://aistudio.google.com/docs/thinking) in Google's documentation for the levels it supports.

## Example: `demo_1.py` - Advertising Strategy Brainstorm

This script asks for advertising ideas for a new consulting company. It runs the prompt twice, at `low` and at `high`, and prints how long each run took and how many tokens it used.

```python
import time

from google import genai
from google.genai import types

client = genai.Client()

# Google ships new models several times a year. See the model naming note in
# python_auth_setup.md when this model ID stops working.
MODEL_ID = "gemini-4-hydrogen"

prompt = """
   I am starting an AI/LLM consulting company. Suggest
   three different options for advertising services.
"""


def ask(thinking_level):
    start = time.perf_counter()
    response = client.models.generate_content(
        model=MODEL_ID,
        contents=prompt,
        config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_level=thinking_level)
        ),
    )
    seconds = time.perf_counter() - start

    usage = response.usage_metadata
    print(f"\n===== thinking_level={thinking_level} =====")
    print(f"time: {seconds:.1f}s  "
          f"thinking tokens: {usage.thoughts_token_count or 0}  "
          f"answer tokens: {usage.candidates_token_count}")
    print(response.text)


for level in ["low", "high"]:
    ask(level)
```

**Explanation:**

1.  **Imports:** `google.genai`, `google.genai.types` for `GenerateContentConfig` and `ThinkingConfig`, and `time` to measure each call.
2.  **Client:** `genai.Client()` reads your key from the environment.
3.  **Model ID:** One `MODEL_ID` constant, so a model change is a one line edit.
4.  **Prompt:** A moderately complex prompt that asks for structured suggestions.
5.  **The `ask` function** makes one `generate_content` call:
    * `config=types.GenerateContentConfig(...)` passes the settings.
    * `thinking_config=types.ThinkingConfig(thinking_level=thinking_level)` sets how much the model reasons.
6.  **Usage metadata:** `response.usage_metadata` reports the tokens the call used. `thoughts_token_count` counts the thinking tokens and `candidates_token_count` counts the tokens in the answer. You pay for both.
7.  **The loop** runs the same prompt at `low` and then at `high`, so you can compare them.

Here are the two summary lines from one run, followed by the start of the `low` answer:

```text
===== thinking_level=low =====
time: 8.2s  thinking tokens: 460  answer tokens: 665
Here are three distinct advertising options tailored for an AI/LLM consulting company, each targeting potential B2B clients at different stages of the buying journey:

### 1. LinkedIn Ads (Targeted B2B Outreach)
LinkedIn is the premier platform for B2B consulting because it allows you to target decision-makers directly by job title, industry, and company size.
* **Why it works for AI consulting:** You can put your services directly in front of CTOs, VPs of Engineering, and Founders who are actively thinking about AI strategy.
...

===== thinking_level=high =====
time: 10.6s  thinking tokens: 567  answer tokens: 810
...
```

Run the example to see both full answers.

## Reading the Numbers

On this prompt the two levels came out close. The `high` run used about 25% more thinking tokens, took about 30% longer, and wrote a somewhat longer answer. Both answers suggested LinkedIn ads and Google search ads, and both were usable. The thinking level is an upper limit on effort, not a fixed amount: the model decides how much of that room a prompt needs, and a three item brainstorm does not need much.

The gap grows with the difficulty of the task. I changed the prompt to ask for a twelve month launch plan with a budget table that must sum to a fixed total, the dependencies between activities, and the three riskiest assumptions. At `low` the model used 1,179 thinking tokens. At `high` it used 4,585, almost four times as many, and wrote an answer more than twice as long.

When you compare levels on your own prompts, look at four things:

* **Quality:** At a higher level the output tends to be more structured and covers more of the prompt. At a lower level the output can still be good, but it is more likely to miss detail on a complex request.
* **Time:** A higher level takes longer, because the model reasons before it answers.
* **Tokens:** You pay for the thinking tokens, so a higher level costs more for the same visible answer.
* **Default:** Gemini 4 Hydrogen already defaults to `high`. If you leave out `thinking_config`, you get the most expensive setting short of `xhigh`. Set `low` explicitly for bulk work such as tagging or short summaries.

The cheapest way to decide is to run the prompt at a low level, read the answer, and raise the level only if the answer is shallow.

## Migrating from `thinking_budget`

Gemini 2.5 models predated thinking levels. They used `thinking_budget`, a token count:

```python
config=types.GenerateContentConfig(
    thinking_config=types.ThinkingConfig(
        thinking_budget=500
    )
)
```

You will still see this in older code and older tutorials. Google deprecated `gemini-2.5-pro` and `gemini-2.5-flash` on November 2, 2026, and from December 1, 2026 it routes their requests to newer models. Google's migration notes list replacing `thinking_budget` with `thinking_level` as one of the changes to make. Two other differences matter when you move old code. First, `thinking_budget=0` turned thinking off on 2.5 models, but you cannot turn thinking off on Gemini 3 and Gemini 4 models: the lowest level is `low` or `minimal`. Second, a budget is harder to reason about than a level, because the same budget means different amounts of work on different models.

## Wrap Up

Thinking level controls how much Gemini reasons before it answers. Set `thinking_level` on a `types.ThinkingConfig` inside a `types.GenerateContentConfig`, and pick a level that fits the task. Remember these points:

- Raise the level for multi-step analysis and planning, and lower it for simple or bulk prompts.
- You pay for thinking tokens. Read `usage_metadata.thoughts_token_count` to see how many you used.
- Each model accepts its own set of levels. Gemini 4 Hydrogen accepts `low` through `xhigh` and defaults to `high`.
- `thinking_budget` is the old Gemini 2.5 control. Replace it with `thinking_level` when you update old code.

In the next chapter we add images to the prompt and use a low thinking level to keep the answers fast.
