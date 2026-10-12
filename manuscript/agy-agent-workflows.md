# An Introduction to AI Agentic Workflows Using the Antigravity CLI

Here we look at a few high level scenarios for using the Antigravity CLI, with sample prompts you can adapt.

**Note:** Some of the examples in this chapter are screenshots (light brown background) and others are output text copied into this manuscript file.

## Beyond Single Prompts: Thinking in Workflows

Our objective here, dear reader, is to move your interaction model from question and answer to delegation and process automation.

What is an agentic workflow? It is not a single prompt such as "Summarize this document." An agentic workflow is a series of dependent steps that the agent carries out in one continuous context:

- Analyze this folder of documents.
- Identify the three key themes.
- Search the web for recent developments on those themes.
- Draft a summary report and write it to a file.

The last step matters. The deliverable is a file on your disk, not a wall of text in a terminal.

## The Reason and Act Loop

An agent earns the name by using tools. It reasons about the goal, acts by calling a tool, reads the result, and reasons again. In `agy` that loop runs inside one session, with one context, across as many steps as the task needs.

The tools fall into a few families:

| Family | What the agent can do |
| --- | --- |
| Files | Read a file, read many files at once, search file contents, find files, write a new file, edit an existing file |
| Shell | Run a command and read its output |
| Web | Search with Google Search, fetch a URL |
| Context | Add a directory with `/add-dir`, hold a whole folder in the working context |
| Extensions | Call tools from MCP servers, follow Agent Skills you install |

You do not have to memorize this list. Ask the agent what it can do, and check `/permissions` to see and change what it is allowed to do. The agent reports each tool call as it happens, so you always know how a conclusion was reached.

Two habits keep the loop honest. First, approve tool calls rather than waving them all through, at least until you trust the workflow. Second, read the diff before you accept a change to an existing file. The `/diff` command shows what changed.

Agentic tools like `agy` change the shape of solo work:

- Tedious multi-step research and content creation becomes a single delegated task.
- Output stays consistent because the same instructions run every time.
- Your attention goes to judging the result rather than producing it.

## Your First Agentic Workflow: The Automated Research Brief

This is the most common task for a consultant or independent researcher, so it is the right first workflow.

Goal: produce a one page research brief on a new technology, for example "Federated Learning."

Step 1: Setup. Create a project folder and start the agent there.

```bash
mkdir federated-learning-brief
cd federated-learning-brief
agy
```

Step 2: Plan before you gather.

Prompt:

```text
I need to create a research brief on "Federated Learning". First, break down the
key topics I need to cover to explain this to a non-technical business executive.
```

Agent action: the agent outlines a structure, for example what it is, why it matters, use cases, and challenges.

Step 3: Research against that structure.

Prompt:

```text
Good. Now use web search to find and summarize two or three recent articles for
each topic you just listed. Cite the URL for each one.
```

Agent action: the agent runs several searches, keeps the plan in context, and returns summaries with sources. It does not start over, because the plan is still in the session.

Step 4: Draft the deliverable.

Prompt:

```text
Now synthesize our whole conversation, the plan and the research summaries, into a
one page research brief. Write it to brief_draft.md.
```

Agent action: the agent consolidates the session context and writes the file. You now have a draft on disk that you can edit in your own editor.

Step 5: Verify before you trust it. This step is not optional for research work.

Prompt:

```text
Check every factual claim and every citation in brief_draft.md against the sources
you found. Mark anything you cannot support and fix what you can.
```

If you want the sources listed at the end, ask for that before the agent writes the file. Asking for output format after the fact costs you a second revision round.

## The Content Repurposing Workflow: From Blog Post to Social Media

This workflow suits freelance creatives and marketers.

Goal: turn one long form blog post into a LinkedIn article, a short thread, and three discussion questions.

Step 1: Load the source.

Prompt:

```text
@my-article.md I am going to ask you to repurpose this article for several
platforms. First, confirm you have read it and state its main argument in two
sentences.
```

Confirming understanding first is a cheap check. If the agent states the argument wrongly, fix that before spending tokens on four rewrites.

Step 2: LinkedIn.

Prompt:

```text
Create a professional 300 word LinkedIn article from the document. Include a strong
headline and use bullet points for the key takeaways.
```

Step 3: Short thread.

Prompt:

```text
Now turn the core message into a five post thread. The first post is a hook, the
last has a call to action, and every post stays under 280 characters.
```

Step 4: Engagement questions.

Prompt:

```text
Finally, write three open ended questions based on the article that I can use to
spark discussion in the comments.
```

Each step reuses the same source document and the same context. That is the time saving. You loaded the article once and got four different deliverables from it. Write each one to its own file when you want to keep them:

```text
Write the LinkedIn version to linkedin.md and the thread to thread.md.
```

## The Simple Data Analysis Workflow: From CSV to Insights

This workflow is for readers who work with data but do not consider themselves programmers.

Goal: analyze a CSV file of sales data and identify the top performing products.

Step 1: Describe before you analyze.

Prompt:

```text
@sales_data.csv This file holds sales data. Describe the columns and give me a
quick summary of what the data contains.
```

Agent action: the agent reads the file and reports the columns, their ranges, and obvious problems such as missing values. Always look at this output. An agent that misreads your columns will produce confident nonsense.

Step 2: Write the script, do not run it yet.

Prompt:

```text
Write a Python script using pandas that reads this CSV and finds the top three
products by "Units Sold". Do not run it yet. Write it to analyze.py.
```

Separating writing from running gives you a chance to read the code first. For a solo worker this is the whole point of keeping the human in the loop.

Step 3: Run it through the shell.

Prompt:

```text
Now run analyze.py and show me the output.
```

The agent runs the command in your shell and reports the result. You can also run it yourself with `!python analyze.py`.

Step 4: Summarize for a stakeholder.

Prompt:

```text
Based on that output, write one paragraph for a business stakeholder explaining
which products are the top performers and what it might mean.
```

Step 5: Keep the work. Ask the agent to write the summary into a file next to the script, for example `analysis_summary.md`, so the next person to open the folder understands what happened.

## Turning a Workflow into a Skill

Once a workflow works, stop retyping it. The Antigravity CLI supports Agent Skills, which are reusable instruction files the agent loads on demand. Open `/skills` to see what is loaded and where the files live.

The practical pattern is to take the five steps above, write them into a Markdown file as instructions, and keep that file with the project. A research brief skill, a weekly review skill, and a newsletter skill cover most of what a solo knowledge worker repeats. A skill also documents the process for the version of you who comes back to it in six months.

## Wrap Up

An agentic workflow is a plan, a sequence of tool calls, and a deliverable written to disk. The Antigravity CLI holds all three in one session, which lets you delegate a multi-step task instead of babysitting a chat window. Start with the research brief, because it exercises planning, web search, and file writing at once. Then move the workflows you repeat into skills and into headless scripts, which is where the real time savings appear.
