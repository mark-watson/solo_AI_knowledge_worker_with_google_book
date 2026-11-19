# Source Code Map

This table maps each chapter file in `./manuscript` to its source code example directory in `./source-code`. Chapters follow the book order in `manuscript/Book.txt`. Chapters with no code show `(none)`.

| Chapter file | Source code directory |
| --- | --- |
| `manuscript/preface.md` | (none) |
| `manuscript/part_1_introduction.md` | (none) |
| `manuscript/who_is_book_for.md` | (none) |
| `manuscript/rise_of_solo_ai_kw.md` | (none) |
| `manuscript/key_concepts.md` | (none) |
| `manuscript/power_prompting.md` | (none) |
| `manuscript/google_ai_ecosystem.md` | (none) |
| `manuscript/gemini_gmail_docs_sheets_meet.md` | `source-code/9_optional_google_apps` |
| `manuscript/part_2_programming.md` | (none) |
| `manuscript/python_tutorial.md` | (none) |
| `manuscript/python_auth_setup.md` | `source-code/1_start_with_auth_and_setup` |
| `manuscript/python_thinking.md` | `source-code/2_thinking` |
| `manuscript/python_images_text.md` | `source-code/3_images_and_text` |
| `manuscript/python_gemini_and_google_colab.md` | (none) |
| `manuscript/part_3_agents.md` | (none) |
| `manuscript/agy-introduction.md` | (none) |
| `manuscript/agy-agent-workflows.md` | (none) |
| `manuscript/knowledgegraphs.md` | `source-code/5_knowledgegraphs` |
| `manuscript/google_agent_development_kit.md` | `source-code/a_google_adk_example` |
| `manuscript/wrapup.md` | (none) |

Every example uses the model `gemini-4-hydrogen` and pins its dependencies in
its own `pyproject.toml`. The ADK project uses `google-genai` 2.x because
`google-adk` requires it; every other project uses `google-genai` 3.x. Run
`make sync` and then `make verify` inside `source-code/` to check that every
example still compiles and still names the current Gemini model. Set `LIVE=1`
to also run the examples that need no OAuth sign-in or keyboard input.

| Directory | Files |
| --- | --- |
| `1_start_with_auth_and_setup` | `auth_test1.py`, `text_generation.py`, `interactions_demo.py` |
| `2_thinking` | `demo_1.py` |
| `3_images_and_text` | `photo_understanding.py` |
| `5_knowledgegraphs` | `demo_ladybug_basics.py`, `movies_demo_ladybug.py` |
| `9_optional_google_apps` | `create_gmail_token.py`, `summarize_gmail.py` |
| `a_google_adk_example` | `deep_search.py` |
