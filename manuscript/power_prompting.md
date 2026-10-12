# The Power of Prompts: Engineering Good Inputs for LLMs

A prompt is the only interface you have to a large language model. Everything the model knows about your task arrives in that text, and everything it produces comes back in response to it. This chapter is about writing prompts that produce work you can use.

If you take one idea from this chapter, take this one: **you are not asking a question, you are briefing a capable colleague who has never met you, cannot see your screen, and knows nothing about your project.** A colleague in that position needs the goal, the context, the audience, and the shape of the answer you want. Give them that and you get something useful. Leave them to guess and you get something generic.

## Why Prompt Quality Matters More Than Model Choice

People spend a lot of energy comparing models. Model choice matters, but for most knowledge work the gap between a well written prompt on a mid-tier model and a lazy prompt on the best model is larger than the gap between the models themselves. A prompt that names the audience and the format does more for the output than a model upgrade does.

The reason is mechanical. Language models predict what comes next given the text so far. A vague prompt leaves a large space of plausible continuations, so the model picks something average. A specific prompt narrows that space. The model still does the writing, but you have told it which of the many possible answers you want.

There is a second reason, and it is practical. A good prompt is reusable. Once you have one that works, it becomes a template, then a saved instruction, then a custom Gem or an Agent Skill. Bad prompts are used once and thrown away.

## The Six Parts of a Strong Prompt

You will not use all six parts every time. A quick question needs one. A task that matters needs all six.

1. **Role and goal.** Who is the model acting as, and what is the outcome? "You are an editor for a technical book" is a role. "Cut this chapter by twenty percent without losing an argument" is a goal.
2. **Context.** What does the model need to know that it cannot infer? Your audience, your constraints, the document, the data, the decision this feeds into.
3. **Input.** The material to work on. Paste it, attach the file, or point at it with `@path/to/file` in a CLI session.
4. **Instructions.** The steps, in order, when order matters. If you want analysis before a recommendation, say so.
5. **Output format.** A paragraph, a table, a Markdown file, a JSON object with named fields, a 200 word email with a subject line. Say which, and give an example when structure matters.
6. **Constraints.** Length, tone, reading level, what to leave out, what to do when information is missing. "If a claim is not supported by the sources, write UNSUPPORTED rather than guessing" is a constraint worth having.

Here is a weak prompt:

```text
Write about our new pricing.
```

Here is the same request with the six parts:

```text
You are writing for existing customers of a small consulting business, not for
prospects. Write a 250 word email announcing our new pricing, effective March 1.
Keep the tone plain and direct, no marketing language. Do not apologize for the
increase, and do not invent reasons for it. Context: our hourly rate moves from
$180 to $195, and existing retainers are held at the old rate for six months.
Format: a subject line, then the body. End with one sentence telling the reader
what to do if they have questions.
```

The second prompt takes two minutes to write and usually removes the need for three revision rounds. That is the trade.

## Specific Techniques That Earn Their Keep

### Give an example of the output

When you want a structure, one example beats a paragraph of description. This is called few-shot prompting, and it is especially valuable for structured extraction. If you want JSON, show the JSON you want:

```text
Extract the vendor, invoice number, and total from each invoice below. Return a
JSON array. Example of the format:

[{"vendor": "Acme Supply", "invoice_number": "INV-1043", "total": 1284.50}]
```

The model follows the shape of the example, including the field names and the number format.

### Ask for reasoning before the answer

For any task that involves judgment, ask the model to work through the problem before it commits to a conclusion. "First list the tradeoffs, then recommend one" produces a better recommendation than "recommend one". Visible reasoning also gives you something to argue with, which beats receiving a conclusion you cannot audit.

Some models do this work internally through a thinking setting. Even then, ask for the short version of the reasoning in the answer when you will act on the result. The chapter on thinking levels covers the API side of this.

### Assign a role, but keep it honest

A role focuses vocabulary and expectations. "You are a patent examiner" changes what the model considers relevant. A role does not give the model knowledge it lacks, so pair roles with context. "You are a patent examiner reviewing a filing in a field you know" is weaker than "You are a patent examiner. Here is the relevant statute and the claim text."

### Break large tasks into steps

A prompt that asks for research, analysis, a draft, and an edit in one pass produces a mediocre version of all four. Run them as separate turns. Each turn gives you a checkpoint where you can correct course, and correction is cheaper than regeneration. This is also how agentic tools work: the agent plans, acts, checks, and acts again.

### Set the length explicitly

Models default to a length that matches the prompt. Ask for 150 words and you get roughly 150. Ask for "a summary" and you get whatever fits. When length matters, state a number.

### Tell it what to do when it does not know

Models fill gaps with plausible text. That is the most dangerous behavior for knowledge work. Add an instruction that gives the model a way out:

```text
Use only the sources below. If the sources do not answer part of the question,
say which part is unanswered. Do not fill gaps from general knowledge.
```

That one line turns a confident document into a useful one.

## Prompts for the Work You Actually Do

### Summarizing a document

```text
Summarize the attached document for someone who has ten minutes and needs to
decide whether to read the whole thing. Give me: the main argument in two
sentences, the three strongest supporting points, and anything the document
asserts without evidence. Do not add information from outside the document.
```

The last sentence is what makes the summary trustworthy. Without it, a summarizer quietly blends in what it already knows about the topic.

### Drafting

```text
Draft a one page project proposal for [project]. Audience: a skeptical operations
director who has budget authority and limited patience. Include: the problem, what
we will do, what it costs, how we will know it worked. Use headings and short
paragraphs. Do not use the words "leverage", "synergy", or "cutting-edge".
```

Naming the audience and banning specific words does more for a draft than any general instruction about style.

### Editing your own writing

```text
Here is a section of my book. Cut it by twenty percent without removing an
argument. Keep my voice: first person, plain words, short sentences. Return the
edited text, then a short list of what you cut and why.
```

Asking for the list of cuts is the useful part. You learn what your own writing does that you did not intend.

### Analyzing data

```text
The file sales_data.csv has one row per order. Describe the columns and their
ranges first. Then find the top five products by revenue. Show the code you used.
If a column has missing values, say how many and how you handled them.
```

Asking for the code makes the analysis checkable. You can run it yourself, which is the difference between a claim and a result.

## Where Good Prompts Live

A prompt that works is an asset, so store it where you will find it again.

- **A notes file** is enough at first. One file per project, each prompt followed by a line saying what it produces.
- **Gems** in the Gemini app save instructions and knowledge files, so a recurring task becomes a named tool you can select.
- **Agent Skills** in the Antigravity CLI save instructions as files in your project, which the agent loads when the task matches. This is the right home for a multi-step workflow, such as the research brief workflow in Part 3.
- **A script** is the right home when the prompt runs on a schedule. Headless mode plus your saved prompt gives you a repeatable job with no typing.

The progression is the point. You start by typing a prompt, and you end with a process that runs without you.

## Common Mistakes

- **Asking several unrelated things at once.** Split them. A prompt with three goals gets one done well.
- **Describing a style instead of showing it.** Paste a paragraph you like and say "match this".
- **Assuming the model remembers.** Each new chat starts fresh. Put the context in, or keep the work in one long session on purpose.
- **Trusting a citation you did not open.** Models produce convincing looking references. Open them.
- **Never revising the prompt.** When a prompt works, edit it into a better version and save it.
- **Blaming the model for a vague brief.** If the output is generic, the prompt probably was too.

## Wrap Up

Prompt writing is a skill you build by writing prompts down, keeping the ones that work, and editing the ones that almost work. Start with the six parts: role and goal, context, input, instructions, format, constraints. Add the two habits that protect you: give an example when structure matters, and give the model a way to say "I do not know". Then store what works, because a saved prompt is time you get back every time you reuse it.

If you want to go further with prompting for the Gemini app and Gems specifically, the ecosystem chapter covers those tools in more detail.
