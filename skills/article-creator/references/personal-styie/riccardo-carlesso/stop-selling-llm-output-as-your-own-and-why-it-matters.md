---
title: "Stop selling LLM output as your own, and why it matters"
author: Riccardo Carlesso
pubDate: Tue, 06 Jan 2026 11:07:50 GMT
link: https://medium.com/@palladiusbonton/my-2026-year-resolution-build-and-maintain-an-llm-netiquette-0e38ea588314?source=rss-b5293b96912f------2
tags: gemini-cli, etiquette, business-etiquette, llm, best-practices
---

# Stop selling LLM output as your own, and why it matters

*Originally published at [Medium](https://medium.com/@palladiusbonton/my-2026-year-resolution-build-and-maintain-an-llm-netiquette-0e38ea588314?source=rss-b5293b96912f------2) by Riccardo Carlesso on Tue, 06 Jan 2026 11:07:50 GMT.*

It’s a new year, and my 2026 resolution is to be nicer to people after reading an inspiring article ([The gift of Nice](https://josvisser.substack.com/p/the-gift-of-nice)) by my former colleague Joe Visser. **Not today**! Today I’m going to be snarky since I’ve had something in my heart I wanted to share for the past 2 years, so here we are. I know, **my 2026 year resolution is how to tell 10 billion people how to behave**.. but a man can dream, can’t he? So forgive my arrogance just this once.

![](https://cdn-images-1.medium.com/max/1024/1*3Ck0M5qmULqxN6ZGpo6-Ag.jpeg)
*A person sharing LLM results from a 3-bullet pront. Courtesy of NanoBanana (yes, AI generated!)*

We’ve all been there, you get dumped a HUGE text/document from someone at work, a friend, someone on whatsapp. It’s super polished, the English is brilliant, academic, and this person (I live in Europe, where English is usually our second language) is a B1 at most; yet it seems authored by Shakespeare if he had the IQ of Stephen Hawking. The person claims they’ve written it, but you both know it was AI from some possibly smart prompt.

I always feel guilty to ask “did you write it with AI?” as it seems offensive (as it might imply some unsaid words like “**this seems too good to be yours**”, or as we say in italian “*flour from your sack*”). I’m so mortified I end up never asking; and I would feel much more relaxed to review content which I KNOW to be AI-generated, as it probably won’t hurt the feeling of the person.

Note the problem I’m trying to address here is not typo-fixing or polishing a few words (which are absolutely fine!), it’s about **content augmentation** and the creation of un-needed paragraphs, to obey the illusion of great authoring. Also this might be my tech bias — in some industries this might resonate differently.

### LLM Etiquette (or lack thereof)

Since the advent of LLMs, I’ve been surprised how everyone consumes them: everyone in my family uses Gemini or ChatGPT or Claude. However, I’m surprised how nobody bothered to write some LLM Netiquette. Google it: I can’t find existing LLM etiquette (write me a comment if you do find one)!

We all know that WRITING IN ALL CAPS ON THE INTERNET IS EQUIVALENT TO SHOUTING, and it’s widely regarded as rude; however, what’s not considered rude is the following:

1. I ask you for a doc to highlight your thoughts on a topic
2. You share with me a 3-page GDoc which sounds suspiciously LLM generated: **and in the middle of dozens of fluffy words, **I fail to grasp anything relevant to the topic, any decision, any personal point of view.
3. I spend 15min reading it, and trying to understand what it says (sometimes asking an LLM to summarize it for me). I would have much preferred a 3-line prompt, as part of the doc, and maybe a line saying “Generated with Gemini 2.5 flash on YYYYMMDD via web interface” (what a nerd).

#### The solution: resuscitating the [MVC](https://en.wikipedia.org/wiki/Model%E2%80%93view%E2%80%93controller) model

I’m an old fart, and as a [Rails](https://rubyonrails.org/) developer I still think [MVC](https://en.wikipedia.org/wiki/Model%E2%80%93view%E2%80%93controller) is cool. I think in MVC terms when I write software or documents, or even interact with people at work.

- **Model**: the chubby model contains your business logic: context, intentions, constraints, style, ... This is your system instructions — [GEMINI.md](https://github.com/google-gemini/gemini-cli) (or AGENTS.md, CLAUDE.md) — or your one-off prompt. It’s the most precious part of your IP!
- **View**: the view is how this data is presented. You can have multiple views for the same model/object (HTML, JSON, maybe image, ..). In this context it could be different languages, presence/lack of emojis, formal/informal tone, ..
- **Controller**: controls how M and V interact. In this metaphor, this is you interacting with LLMs. Or I might just fall short in my metaphor by 33% :)

Here are some simple golden rules I apply to myself and I’m trying to get my friends and colleagues to apply to.

1. **“Do not sell LLM output as your own”**. That’s cultural appropriation and LLMs might strike soon on that :)
2. Understand the MVC model for LLMs; in other words: **The prompt is what REALLY matters, not the output**. You can always find a better LLM or a better prompt to write a better output. I’ll spell it in simpler terms for devs: “*add the prompt to git , NOT it’s output” *(even if it looks a lot nicer!). Ugly is more important than beautiful, here. The output is an after thought, and can be regenerated in 3 seconds.

#### How does this solve all world’s problems?

Sometimes you have an idea (let’s call it *idea_v1*), and that idea is distilled in your mind. You want to communicate it to your stakeholders. You could just share that brilliant idea, but decide dress it up nicely with an LLM. Now it’s not only smart, it also LOOKS great! Problem is, people won’t GET your idea, buried under a lot of sophisticated words that an English-as-a-second-language person like me won’t get.

![](https://cdn-images-1.medium.com/max/1024/1*ypCe6L6GvwDPUus7VPXzOg.jpeg)
*Idea v1: prompt on the left and AI blurb on the right — indeed generated with NanoBanana.*

**How about:** you share your BEAUTIFUL idea with SIMPLE/UGLY words to your stakeholders. We iterate quickly over it, maybe your 3 bullet points diverge a little and become 4, and we reach an agreement. After we all are in agreement, THEN it’s time to llm-coat it with nice words. Now the idea has been agreed, distilled, and we can afford to have a nice LLM “view” of it, in English or Italian, in Harvard / working-class style, with emojis or without. **The most important thing is**, we still have a cut-and-paste version of those 4 bullet points (*idea_v2*) as a second tab of that Google Doc to take it from. This way, we can always iterate over a new v3, or regenerate in a diferent language/tone/emojiness/..

#### Conclusions

The **model** is key! Don’t over-focus on the view**,** just because it looks so nice. Yes, I’m speaking to you JS/TS front-enders out there!

Please be more respectful and mindful of your audience:

- **Do not send whatsapp voice messages**. They’re faster for you to produce, slower for me to consume. This seems off topic, but it’s still about distilling input/output, just without LLMs. *(This linesaves me a second article).*
- **Admit when you use LLMs**. Transparency is ~always good. Also remember: people are usually cautious in giving feedback, as it can potentially offend the writer; if you say it was LLM generated, they will have NO problem redacting/correcting parts that they would be afraid of changing ig it was *you*.
- If possible, **share the source too **(your LLM prompt). I understand this is not always feasible (business, affection, fear of offending, .. and it would ruin politics). It’s so much better to say “here’s my idea and here’s my possible output”.
- *[If you’re not a developer, you can skip this]* Add ALL your prompts to source control. Personally, I try to have some standard locations to configure my [Gemini CLI](https://github.com/google-gemini/gemini-cli) : docs/ideas/ (Something I’d like to do in the future, and park here for future promption to a task, etc/prompts/ (If I use them inside a software, maybe with jinja templating), or docs/tasks/ (If I want Gemini to execute upon them , with a mental note: one file one task one GH issue). Finally, use metadata/conventions to label human vs machine-generated output.

**Note**. Usually I use LLMs to polish my writing. Not this time. This article contains Italianisms (which i’ve purposefully disseminated here and there), and poor English. My mistakes are my proud point today :) If something sounds like an LLM, well, you’re wrong this time. Except for graphics.

If you disagree with me, please tell me why in a comment! If you agree, send it to that person who does it; maybe we can all learn a bit more from each other in [this new “Intelition” AI era](https://venturebeat.com/technology/intelition-changes-everything-ai-is-no-longer-a-tool-you-invoke).

![](https://medium.com/_/stat?event=post.clientViewed&referrerSource=full_rss&postId=0e38ea588314)