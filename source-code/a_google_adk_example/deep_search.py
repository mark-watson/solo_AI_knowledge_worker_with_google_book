# Derived from: https://github.com/google/adk-samples/tree/main/python/agents/deep-search

import asyncio
import datetime
import re
import warnings
from typing import AsyncGenerator, Literal

from google.adk.agents import BaseAgent, LlmAgent, LoopAgent, SequentialAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.agents.context_cache_config import ContextCacheConfig
from google.adk.agents.invocation_context import InvocationContext
from google.adk.apps.app import App
from google.adk.events import Event, EventActions
from google.adk.planners import BuiltInPlanner
from google.adk.runners import InMemoryRunner
from google.adk.tools import google_search
from google.adk.tools.agent_tool import AgentTool
from google.genai import types as genai_types
from pydantic import BaseModel, Field

# ADK 2 deprecates SequentialAgent and LoopAgent in favor of Workflow, but a
# Workflow cannot yet be the sub-agent of an LlmAgent, which this design needs.
warnings.filterwarnings("ignore", message=".*is deprecated in favor of Workflow.*")

# Google ships new models several times a year. See the model naming note in
# python_auth_setup.md when this model ID stops working.
MODEL_NAME = "gemini-4-hydrogen"


# --- Structured Outputs ---
class SearchQuery(BaseModel):
    search_query: str = Field(description="A specific, targeted query for web search.")


class Feedback(BaseModel):
    grade: Literal["pass", "fail"]
    comment: str
    follow_up_queries: list[SearchQuery] | None = Field(default=None)


# --- Callbacks ---
def collect_sources(callback_context: CallbackContext) -> None:
    """Give each web source found by Google Search a short ID such as src-1."""
    state = callback_context.state
    url_map = state.get("url_to_short_id", {})
    sources = state.get("sources", {})

    for event in callback_context.session.events:
        if not (md := event.grounding_metadata):
            continue
        for chunk in md.grounding_chunks or []:
            if not chunk.web or chunk.web.uri in url_map:
                continue
            short_id = f"src-{len(url_map) + 1}"
            url_map[chunk.web.uri] = short_id
            sources[short_id] = {
                "title": chunk.web.title or chunk.web.domain,
                "url": chunk.web.uri,
            }

    state["url_to_short_id"] = url_map
    state["sources"] = sources


def replace_citations(callback_context: CallbackContext) -> genai_types.Content:
    """Turn <cite source="src-1" /> tags into Markdown links."""
    text = callback_context.state.get("final_cited_report", "")
    sources = callback_context.state.get("sources", {})

    def replacer(match):
        info = sources.get(match.group(1))
        return f" [{info['title']}]({info['url']})" if info else ""

    text = re.sub(r'\s*<cite\s+source\s*=\s*["\']?(src-\d+)["\']?\s*/>', replacer, text)
    text = re.sub(r"\s+([.,;:])", r"\1", text)
    return genai_types.Content(parts=[genai_types.Part(text=text)])


# --- Agents ---

# 1. Plan Generator: Creates the initial strategy
plan_generator = LlmAgent(
    model=MODEL_NAME,
    name="plan_generator",
    tools=[google_search],
    instruction=f"""
    Create a 5-step research plan.
    Prefix every step with either:
    - **`[RESEARCH]`**: For information gathering.
    - **`[DELIVERABLE]`**: For synthesis/output creation.

    Start with 5 `[RESEARCH]` goals. If these imply a specific output (like a table), add a `[DELIVERABLE][IMPLIED]` step immediately after.
    If refining a plan based on feedback, mark changes with `[MODIFIED]` or `[NEW]`.
    Only use search if strictly necessary to clarify ambiguous topics.
    Date: {datetime.date.today().isoformat()}
    """,
)

# 2. Section Planner: Outlines the report structure
section_planner = LlmAgent(
    model=MODEL_NAME,
    name="section_planner",
    output_key="report_sections",
    instruction="""
    Using the 'research_plan', design a Markdown outline (4-6 sections) for the final report.
    Do not include a References section.
    Format: # Section Name \n Brief overview...
    """,
)

# 3. Researcher: The heavy lifter (Search -> Synthesize)
section_researcher = LlmAgent(
    model=MODEL_NAME,
    name="section_researcher",
    tools=[google_search],
    output_key="section_research_findings",
    after_agent_callback=collect_sources,
    planner=BuiltInPlanner(thinking_config=genai_types.ThinkingConfig(include_thoughts=True)),
    instruction="""
    Execute the `research_plan` in two strict phases:

    **Phase 1: Research**
    Process all `[RESEARCH]` goals first. For each, generate 4-5 search queries, execute them, and summarize findings. Store these summaries internally.

    **Phase 2: Synthesis**
    Once Phase 1 is complete, process `[DELIVERABLE]` goals.
    Use the stored summaries to build the requested artifacts (tables, reports, etc).
    Do NOT search during this phase.

    Final output must include all research summaries and deliverable artifacts.
    """,
)

# 4. Evaluator: Checks quality
research_evaluator = LlmAgent(
    model=MODEL_NAME,
    name="research_evaluator",
    output_key="research_evaluation",
    output_schema=Feedback,
    instruction="""
    Evaluate 'section_research_findings'.
    Pass if coverage is comprehensive. Fail if there are gaps.
    If Fail, provide 'follow_up_queries' to fix the gaps.
    """,
)

# 5. Search Executor: Fixes gaps found by Evaluator
enhanced_search_executor = LlmAgent(
    model=MODEL_NAME,
    name="enhanced_search_executor",
    tools=[google_search],
    output_key="section_research_findings",
    after_agent_callback=collect_sources,
    instruction="""
    You are fixing a failed research attempt.
    1. Execute all 'follow_up_queries' from the evaluation.
    2. Synthesize new findings and merge them into 'section_research_findings'.
    """,
)


# 6. Escalation Checker: Breaks the loop if Passed
class EscalationChecker(BaseAgent):
    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        result = ctx.session.state.get("research_evaluation", {})
        if result.get("grade") == "pass":
            yield Event(author=self.name, actions=EventActions(escalate=True))
        else:
            yield Event(author=self.name)


# 7. Composer: Writes final report with citations
report_composer = LlmAgent(
    model=MODEL_NAME,
    name="report_composer",
    output_key="final_cited_report",
    after_agent_callback=replace_citations,
    instruction="""
    Write a professional report that follows this outline:
    {report_sections}

    Base it on these research findings:
    {section_research_findings}

    **CITATIONS:** These are the available sources, keyed by ID:
    {sources?}
    After each claim that comes from a source, cite it with `<cite source="src-ID" />`,
    using only IDs from the list above.
    Do not create a bibliography; use inline citations only.
    """,
)

# --- Pipelines ---

research_pipeline = SequentialAgent(
    name="research_pipeline",
    description="Executes plan, refines via loop, writes report.",
    sub_agents=[
        section_planner,
        section_researcher,
        LoopAgent(
            name="refinement_loop",
            max_iterations=3,
            sub_agents=[
                research_evaluator,
                EscalationChecker(name="escalation_checker"),
                enhanced_search_executor,
            ],
        ),
        report_composer,
    ],
)

# The Root Agent: Interfaces with the user
interactive_planner = LlmAgent(
    name="interactive_planner",
    model=MODEL_NAME,
    output_key="research_plan",
    tools=[AgentTool(plan_generator)],
    sub_agents=[research_pipeline],
    instruction="""
    You are a research assistant.
    1. Receive user topic.
    2. Call `plan_generator` to create a plan.
    3. Show plan to user.
    4. If user requests changes, call `plan_generator` again.
    5. If user agrees, delegate to `research_pipeline`.
    """,
)

# --- Application ---
# Each agent transfer changes the system instruction, so give each agent its
# own context cache instead of resending the whole prompt after a transfer.
app = App(
    root_agent=interactive_planner,
    name="DeepSearchApp",
    context_cache_config=ContextCacheConfig(),
)


async def main():
    print("\n--- Deep Search Agent ---")
    topic = input("Enter the research topic: ")

    runner = InMemoryRunner(app=app)
    user_id, session_id = "cli_user", "cli_session"
    await runner.session_service.create_session(
        app_name=app.name, user_id=user_id, session_id=session_id
    )

    current_input = topic
    while True:
        message = genai_types.Content(role="user", parts=[genai_types.Part(text=current_input)])
        last_author = None
        report = None
        async for event in runner.run_async(
            user_id=user_id, session_id=session_id, new_message=message
        ):
            if not (event.content and event.content.parts):
                continue
            for part in event.content.parts:
                # Skip the model's internal reasoning and tool calls.
                if not part.text or part.thought:
                    continue
                # replace_citations sends a second copy of the report with
                # links in place of cite tags. Keep only the last copy.
                if event.author == report_composer.name:
                    report = part.text
                    continue
                if event.author != last_author:
                    print(f"\n\n[{event.author}]")
                    last_author = event.author
                print(part.text, end="", flush=True)

        if report:
            print(f"\n\n[{report_composer.name}]\n{report}")

        current_input = input(
            "\n\n(Enter to continue, or type feedback. Type 'quit' to exit)\n> "
        ).strip()
        if current_input.lower() in ("quit", "exit"):
            break
        current_input = current_input or "proceed"


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, EOFError):
        print("\nExiting...")
