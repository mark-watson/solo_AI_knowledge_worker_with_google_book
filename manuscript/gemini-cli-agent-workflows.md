# An Introduction to AI Agentic Workflows Using gemini-cli

Here we look at a few high level scenarios for using gemini-cli including sample prompts.

**Note:** Some of the following examples using gemini-cli are screenshots (light brown background) and other are the output text copied to this manuscript file for this chapter.

## Beyond Single Prompts: Thinking in Workflows

Our objective here, dear reader, is to redefine your personal interaction model from a simple question-and-answer format to one of delegation and process automation.

What is an agentic workflow? An agent workflow is not a simple single prompt ("Summarize this document”). With an agentic workflow we use a series of steps like:

- Analyze this folder of documents.
- Identify the three key themes.
- Search the web for recent developments on those themes.
- Draft a summary report.

The "Reason and Act" Loop in gemini-cli: Use the power of an agent that comes from its ability to use tools (/tools), access local files (@folder), search the web, and write new files all within a single, continuous context. This is the core of its "agent-like" behavior. You can use the command **/tools** to see what is available builtin in gemini-cli:

- ReadFolder
- ReadFile
- SearchText
- FindFiles
- Edit
- WriteFile
- WebFetch
- ReadManyFiles
- Shell
- Save Memory
- GoogleSearch


Agent based tools like gemini-cli are game-changers for Solo Workers:

- Automating tedious multi-step research and content creation tasks
- Ensuring consistency
- Freeing up cognitive energy for higher-level strategic thinking.

## Your First Agentic Workflow: The Automated Research Brief

Our objective here is to provide a complete, step-by-step walkthrough of a common task for consultants and researchers. This builds directly on skills you may already have.

Workflow Example:

Goal: Create a 1-page research brief on a new technology (e.g., "Federated Learning").

Step 1: Setup. Create a new project folder (e.g., federated-learning-brief). cd into it and start gemini-cli.

Step 2: Initial Brainstorm & Planning.

Prompt: "I need to create a research brief on 'Federated Learning'. First, break down the key topics I need to cover to explain this to a non-technical business executive."

Agent Action: Gemini will outline a structure (e.g., What it is, Why it's important, Use Cases, Challenges).

Step 3: Web Research (Using the /tools command).

Prompt: "Great. Now, using the web search tool, find and summarize 2-3 recent articles for each of the topics you just identified."

Agent Action: gemini-cli will perform web searches and provide summaries, maintaining the context of the initial plan.

Step 4: Draft Generation & File Creation.

Prompt: "Excellent. Now, synthesize all of our conversation—the plan and the research summaries—into a coherent, 1-page research brief. Write the output to a new file named brief_draft.md."

Agent Action: The agent consolidates the entire session's context and writes the result directly to a local file.


## The Content Repurposing Workflow: From Blog to Social Media

Our objective here is to show freelance creatives and marketers how to automate content adaptation across different platforms.

Workflow Example:

Goal: Convert a long-form blog post into a LinkedIn article, a Twitter/X thread, and three discussion questions.

Step 1: Context Loading. Start gemini-cli in a folder containing the blog post (e.g., my-article.md).

Prompt: "@my-article.md I am going to ask you to repurpose this article for different social media platforms. First, confirm you have read and understood the main arguments of the article."

Step 2: Generate LinkedIn Post.

Prompt: "Create a professional, 300-word LinkedIn article based on the document. Include a strong headline and use bullet points to highlight the key takeaways."

Step 3: Generate Twitter/X Thread.

Prompt: "Now, transform the core message into a 5-tweet thread. The first tweet should be a hook, and the last should have a call-to-action. Make sure each tweet is under 280 characters."

Step 4: Generate Engagement Questions.

Prompt: "Finally, generate three open-ended questions based on the article that I can use to spark discussion in the comments."

Chapter Wrap-up: Explain how the agent maintained a deep understanding of the source document across multiple, distinct requests, saving massive amounts of time.

## The Simple Data Analysis Workflow: From CSV to Insights

Our objective here is to demonstrate a workflow for readers who work with data, like marketers or consultants, without requiring them to be expert programmers. This connects perfectly to the previous Colab chapter.

Workflow Example:

Goal: Analyze a simple CSV file of sales data to identify top-performing products.

Step 1: Setup and Context. Place sales_data.csv in your project folder.

Prompt: "@sales_data.csv This file contains sales data. First, describe the columns and provide a quick summary of the data it contains."

Step 2: Code Generation.

Prompt: "Write a Python script using pandas to read this CSV and identify the top 3 products by 'Units Sold'. Don't run it yet, just write the code to a file named analyze.py."

Agent Action: Generates the Python code and saves it. This leverages the coding skills previously mentioned in this book.


Step 3: Code Execution (Shell Passthrough).

Prompt: "Now, execute the script you just wrote."

Command: !python analyze.py

Agent Action: gemini-cli runs the command in the shell and shows the output.

Step 4: Human-in-the-Loop Summary.

Prompt: "Based on the output from the script, write a one-paragraph summary for a business stakeholder explaining which products are the top performers."
