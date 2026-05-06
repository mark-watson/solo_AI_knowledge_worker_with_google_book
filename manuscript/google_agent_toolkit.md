# Python Research Agent Using Google Agent Tool Kit

The Google Agent Development Kit (ADK) is an open-source Python framework for building multi-agent AI systems. In this chapter we build a deep research agent that plans investigations, executes web searches, evaluates its own findings, and produces a professionally cited report — all orchestrated by cooperating LLM-powered agents running on the Gemini model family.

## Overview of Google Agent Toolkit

The ADK provides composable agent primitives — `LlmAgent`, `SequentialAgent`, `LoopAgent`, and `BaseAgent` — that let you assemble complex workflows from simple, single-purpose agents. Each agent has its own instruction prompt, optional tools (such as Google Search), and structured output schemas enforced via Pydantic models. Agents communicate through shared session state, and the framework handles the event loop, tool dispatch, and callback lifecycle automatically. This design makes it straightforward to build systems where one agent plans, another researches, a third evaluates quality, and a fourth composes the final output.

## Research Agent

I rewrote Google's full research agent  web app example program, simplyfying it as a command line utility.
The following listing shows the complete deep search agent. It defines seven specialized agents wired together in a sequential pipeline with an inner refinement loop. The `interactive_planner` root agent receives a research topic from the user, delegates plan creation to the `plan_generator`, and upon approval hands off to the `research_pipeline`. Inside the pipeline, the `section_researcher` executes Google searches and synthesizes findings, the `research_evaluator` grades coverage quality, and the `enhanced_search_executor` fills any gaps — looping up to three times until the evaluator passes. Finally, the `report_composer` writes a Markdown report with inline source citations.

```python
# Derived from: https://github.com/google/adk-samples/tree/main/python/agents/deep-search

import re
import datetime
from typing import Literal, AsyncGenerator

from pydantic import BaseModel, Field
from google.genai import types as genai_types

from google.adk.agents import BaseAgent, LlmAgent, LoopAgent, SequentialAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.agents.invocation_context import InvocationContext
from google.adk.apps.app import App
from google.adk.events import Event, EventActions
from google.adk.planners import BuiltInPlanner
from google.adk.tools import google_search
from google.adk.tools.agent_tool import AgentTool

# Defaults to Gemini 2.0 Flash for balanced speed/reasoning
MODEL_NAME = "gemini-3-flash-preview"

# Note: GOOGLE_API_KEY shuld be in your environment


# --- Structured Outputs ---
class SearchQuery(BaseModel):
    search_query: str = Field(description="A specific, targeted query for web search.")

class Feedback(BaseModel):
    grade: Literal["pass", "fail"]
    comment: str
    follow_up_queries: list[SearchQuery] | None = Field(default=None)

# --- Callbacks ---
def collect_sources(callback_context: CallbackContext) -> None:
    """Aggregates sources from grounding metadata into state."""
    session, state = callback_context._invocation_context.session, callback_context.state
    url_map, sources = state.get("url_to_short_id", {}), state.get("sources", {})
    next_id = len(url_map) + 1

    for event in session.events:
        if not (md := event.grounding_metadata): continue
        
        # Map URLs to short IDs (src-1, src-2)
        chunk_map = {}
        for idx, chunk in enumerate(md.grounding_chunks or []):
            if not chunk.web: continue
            url = chunk.web.uri
            if url not in url_map:
                short_id = f"src-{next_id}"
                url_map[url] = short_id
                sources[short_id] = {"title": chunk.web.title or chunk.web.domain, "url": url}
                next_id += 1
            chunk_map[idx] = url_map[url]

    state["url_to_short_id"] = url_map
    state["sources"] = sources

def replace_citations(callback_context: CallbackContext) -> genai_types.Content:
    """Converts <cite source='src-1'/> tags to Markdown links."""
    text = callback_context.state.get("final_cited_report", "")
    sources = callback_context.state.get("sources", {})

    def replacer(match):
        sid = match.group(1)
        info = sources.get(sid)
        return f" [{info['title']}]({info['url']})" if info else ""

    # Replace tags and fix spacing
    text = re.sub(r'<cite\s+source\s*=\s*["\']?(src-\d+)["\']?\s*/>', replacer, text)
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
    Date: {datetime.datetime.now().strftime("%Y-%m-%d")}
    """
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
    """
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
    """
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
    """
)

# 5. Search Executor: Fixes gaps found by Evaluator
enhanced_search_executor = LlmAgent(
    model=MODEL_NAME,
    name="enhanced_search_executor",
    tools=[google_search],
    output_key="section_research_findings", # Merges results back
    after_agent_callback=collect_sources,
    instruction="""
    You are fixing a failed research attempt.
    1. Execute all 'follow_up_queries' from the evaluation.
    2. Synthesize new findings and merge them into 'section_research_findings'.
    """
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
    Write a professional report using 'section_research_findings' and 'report_sections'.
    **CITATIONS:** You MUST cite sources using this format: `<cite source="src-ID" />`.
    Do not create a bibliography; use inline citations only.
    """
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
            sub_agents=[research_evaluator, EscalationChecker(name="checker"), enhanced_search_executor],
        ),
        report_composer,
    ],
)

# The Root Agent: Interfaces with the user
interactive_planner = LlmAgent(
    name="interactive_planner",
    model=MODEL_NAME,
    output_key="research_plan",
    tools=[AgentTool(plan_generator)], # Uses the generator as a tool
    sub_agents=[research_pipeline],    # Delegates to pipeline upon approval
    instruction=f"""
    You are a research assistant.
    1. Receive user topic.
    2. Call `plan_generator` to create a plan.
    3. Show plan to user.
    4. If user requests changes, call `plan_generator` again.
    5. If user agrees, delegate to `research_pipeline`.
    """
)

# --- Application ---
app = App(root_agent=interactive_planner, name="DeepSearchApp")

if __name__ == "__main__":
    import asyncio
    import sys
    from google.adk.runners import InMemoryRunner

    async def main():
        print("\n--- Deep Search Agent Initialized ---")
        topic = input("Enter the research topic: ")
        print(f"Starting research for topic: {topic}\n")

        runner = InMemoryRunner(app=app)
        
        user_id = "cli_user"
        session_id = "cli_session"
        
        # Ensure session exists
        await runner.session_service.create_session(
            app_name=app.name,
            user_id=user_id,
            session_id=session_id
        )

        current_input = topic

        while True:
            try:
                message = genai_types.Content(parts=[genai_types.Part(text=current_input)])
                print("\n--- Agent Response ---")
                
                async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=message):
                    # Debug printing
                    print(f"DEBUG: Event: {type(event)}") 
                    if hasattr(event, 'content') and event.content:
                        print(f"DEBUG: Content parts: {len(event.content.parts)}")
                        for p in event.content.parts:
                             print(f"DEBUG: Part type: {type(p)}")
                             if p.function_call:
                                 print(f"DEBUG: Function call: {p.function_call.name}")

                    if hasattr(event, 'content') and event.content and event.content.parts:
                        for part in event.content.parts:
                            if part.text:
                                print(part.text, end="", flush=True)
                
                print("\n----------------------")
                
                current_input = input("\n(Enter to continue, or type feedback/instruction. Type 'quit' to exit)\n> ")
                if current_input.lower() in ["quit", "exit"]:
                    break
                if not current_input.strip():
                     current_input = "proceed"

            except KeyboardInterrupt:
                print("\nExiting...")
                break
            except Exception as e:
                print(f"\nError: {e}")
                import traceback
                traceback.print_exc()
                break

    asyncio.run(main())
```

The deep search agent demonstrates several patterns that are broadly useful when building agentic AI systems: breaking a complex task into focused sub-agents, using structured Pydantic outputs to enforce data contracts between agents, implementing self-improving loops with quality evaluation, and tracking provenance through source citation callbacks. These same patterns can be adapted for other workflows such as competitive analysis, literature review, market research, or any task where iterative search and synthesis produces better results than a single LLM call.
