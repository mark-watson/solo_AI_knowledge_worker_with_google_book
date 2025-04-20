# Gemini integration with Gmail, Google Docs, Google Sheets and Google Meet, Google Drive, Google Calendar

In the last section of this book we will look at short Python programs that utilize the Gemini APIs accessing Google WorkSpace apps like Gmail, etc. Here we show examples of interacting with the WorkSpace web apps and Gemini.

## Combining Gemini in Gmail with Google Docs, Drive, and Calendar

As I write this in April 2025, Gemini in Gmail is tightly integrated with your document files in Google Docs and also supports:

- Google Drive: Gemini can find and summarize information from your files stored in Google Drive directly within Gmail.
- Google Calendar: You can ask Gemini in Gmail to find information about events on your primary calendar or even create new calendar events.

Currently there is some support for:

- Google Sheets & Slides: While the core integration is strong in Docs, Gemini capabilities extend to Sheets (like analyzing data) and Slides (like creating presentations), often accessible via the Gemini side panel within those apps or the main Gemini interface connected to your Workspace account. Information from these might be referenced or summarized within Gmail.
- Google Meet: Gemini can help with meeting-related tasks like taking notes or summarizing, and this information might be accessible or summarized through Gmail.

A few days ago I received a request for [free mentoring](https://markwatson.com/#mentoring) and while I was reading this person’s email I activated Gemini inside Gmail and prompted “Find my @doc Google Docs that might be useful for answering this person's questions?”

This was useful because it surfaced two notes in Google Docs that were relevant to the mentoring request email. I didn’t want to use this person’s email as a book example so I sent myself a similar question, opened the email in Gmail and activated Gemini. Again, I used the prompt “Find my @doc Google Docs that might be useful for answering this person's questions?” And show the screenshot of this here:

![Example combining Gemini with Google Docs and Gmail](gmail_gemini_docs.jpg)


## Combining Gemini with Google Calendar and Gmail

This example uses the same test email but now the prompt is “Please find Calendar entries for tasks relating to this email” and here is the calendar entries it found:

![Example combining Gemini with Google Calendar and Gmail](gmail_gemini_calendar.jpg)

## Using Gemini in a Google Doc Specifying a Design Document for a New Software Project

Here we open an old design document in Google Docs that I wrote many years ago and after activating Gemini, I prompted “Write the software specified in this design document” and Gemini used the text in the document to write an initial Haskell implementation:

![Example combining Gemini with Google Calendar and Gmail](google-doc-gemini.jpg)


## Wrap Up for Gemini Integration with Google WorkSpace Apps

I have been experimenting with Gemini integration in Google apps since the summer of 2024 and tool features and capabilities have greatly improved. As I write this in April 2025 I now use Gemini integration with Google apps as a daily tool.