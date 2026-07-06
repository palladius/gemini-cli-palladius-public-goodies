---
title: "Vibe coding my first Chrome Extension with gemini-cli !"
author: Riccardo Carlesso
pubDate: Wed, 25 Jun 2025 16:26:43 GMT
link: https://medium.com/google-cloud/vibe-coding-my-first-chrome-extension-with-gemini-cli-da5630d00434?source=rss-b5293b96912f------2
tags: cli, claude-code, gemini, gemini-cli, onyx
---

# Vibe coding my first Chrome Extension with gemini-cli !

*Originally published at [Medium](https://medium.com/google-cloud/vibe-coding-my-first-chrome-extension-with-gemini-cli-da5630d00434?source=rss-b5293b96912f------2) by Riccardo Carlesso on Wed, 25 Jun 2025 16:26:43 GMT.*

### Vibe coding my first Chrome Extension with Gemini CLI !

A few months ago, a colleague told me about an internal tool that my colleagues were building: ([Blog Post](https://blog.google/technology/developers/introducing-gemini-cli-open-source-ai-agent/?utm_campaign=CDR_0x89ad3e41_platform_b422075371&utm_medium=external&utm_source=blog) — [GitHub](https://github.com/google-gemini/gemini-cli)).

![](https://cdn-images-1.medium.com/max/1024/0*VWbUzB6s5CNkMeZe.gif)

**What is Gemini CLI?**

It’s a CLI version of an LLM code assist which is code and file-system aware, and can help you create/fix code, and maybe also create a feature branch for you and push to production.

Think of a “bash version” of Cursor/Windsurf” (or a free version of Claude Code / Codex CLI), and built with my favourite model, ♊ [**Gemini**](https://ai.google.dev/gemini-api/docs/models)!

Since I’m a “cleek” (*CLI geek *— my neologism), you can imagine my excitement to try it! But where to start?

**TL;DR **In this article you will find:

- A guided tour of gemini-cli .
- A deep dive of its features (yep, also **MCP**!)
- How to handle errors.
- Power tips to make it 🚀 rock!

Impatient to try it out? Click [here](https://github.com/google-gemini/gemini-cli/): ⏩ [https://github.com/google-gemini/gemini-cli](https://github.com/google-gemini/gemini-cli/) ⏪

![](https://cdn-images-1.medium.com/max/421/0*29ChwwTVDcIQPRIM)
*What a cute logo*

### I’ve never written a Chrome Extension — let AI do it for me!

***My use case. ****It’s been my dream since 2010 to create a Chrome Extension which would be some sort of colored bar which would present some Riccardo-customized data based on the URL. It could be some sort of “contextual bookmark” (“This is the repo that Roberto showed you last week”) or some rudimental *[*fake news checker*](https://en.wikipedia.org/wiki/List_of_fake_news_websites)* (if url =~ /*[*byoblu*](https://mediabiasfactcheck.com/byoblu-bias/)*/ then “don’t trust this site!”).*

*Initial prompt:*

```
"It's always been my dream to create a magic bookmark Chrome Extension
which works this way. Every time I'm on a website, say a youtube page
 "https://www.youtube.com/watch?v=1vTOG5QFOWY" or a medium article, this 
extension looks up a DB (say Google Cloud Firestore, for instance, to keep 
schema flexible and size low) and if there is some sort of bookmark (url, 
title, description) it renders that note. So the app is basically a post 
it note which gets triggered by me navigating a certain bookmark, stored 
by [ url, user_id, title, description, .. and usual timestamp modifiers as 
in rails]. Initially we make it work just for myself (user_id = 1, 
email=pbt@gmail.com) but keep it multi tenant for the future. I've never
 written a chromext, can you please help me?"
```

### 30 minutes later..

![](https://cdn-images-1.medium.com/max/418/0*qxYemjUz9MdjglJa)
*This is Chrome showing me my Chrome Extension is succesfully loaded!*

And after a few iterations, there you are!

![](https://cdn-images-1.medium.com/max/1024/0*1q0GwDLLdJiENofV)

- Me adding a bookmark:

![](https://cdn-images-1.medium.com/max/1024/0*ABCuY1e3XyBl9y_P)

- and me visiting the page afterwards:

![](https://cdn-images-1.medium.com/max/1024/0*KI6uwEira8nShfGV)

**Note**: it looks like my idea was silly after all, since 90% of websites prevent chrome extensions from “external manipulation of the DOM” (see MutationObserver, Content Security Policy, ..) , but a man can dream can’t he?

### How to get started

The simplest way to get started is this:

- A **Gemini API KEY**, which you can generate for free in [**AI Studio**](https://aistudio.google.com/). You can also
- To run this command: npx [https://github.com/google-gemini/gemini-cli](https://github.com/google-gemini/gemini-cli)

![](https://cdn-images-1.medium.com/max/748/0*_lKY_UVAiDz0-g-A)

Follow the [README](https://github.com/google-gemini/gemini-cli) for more options.

### Customization: It all starts with a `GEMINI.md` ..

What if you have a particularly colorful, emoji-ful coding style? Or like a particular language, library or file structure? What if you want everything to be tail-recursive?

[DHH](https://dhh.dk/) and [Rails](https://rubyonrails.org/) taught us that [*Convention over configuration*](https://en.wikipedia.org/wiki/Convention_over_configuration) is good. gemini-cli is no exception: it has solid and friendly defaults. One of them? Dump your brain into a** ****GEMINI.md **(or multiple ones, over different folders) and let it do the job! The CLI will start picking it up automatically. Why markdown? Haven’t you heard Karpathy? “The hottest new programming language is English.” . And it’s extension is md :)

**💡 Tip**: After a few weeks using gemini-cli, I noticed I was often asking the same thing; of course, my Software engineering practices are very personal yet consistent to me! So I decided to [DRY](https://en.wikipedia.org/wiki/Don%27t_repeat_yourself) my GEMINI.md into one which will get called ALL the time. I’m also telling my other GEMINI.md’s to first read that, in delegation style.

![](https://cdn-images-1.medium.com/max/1024/0*cktBMjbPmEJR_uLg)

[Here’s](https://github.com/palladius/vibecoding/blob/main/GEMINI.md) my current GEMINI.md “proto-configuration”.

### URL Fetch anyone?

**💡 Tip**. Since `gemini-cli` is able to retrieve URLs, you can do “RAG” with your GEMINI.md, and instruct him to read some documentation online. Example:

```
For LLM, best to use python and `google-adk`.
* tutorial to get started: https://google.github.io/adk-docs/tutorials/agent-team/
* For function calling, read docs in https://google.github.io/adk-docs/tools/built-in-tools/
* For MCP: https://google.github.io/adk-docs/tools/mcp-tools/
* For deployment to Cloud Deploy use https://google.github.io/adk-docs/deploy/cloud-run/ (but beware, we might want to do Cloud Run our way as i've explained above).
```

### It has memory!

You can memorize your preferences which persist across future calls.

![](https://cdn-images-1.medium.com/max/1024/0*Qxr5-WISAuswesIC)

### ..and It supports MCP!

I’ve just found out it also supports MCP, so you can connect it to your favorite MCP servers. I particularly like [SERP](https://www.searchapi.io/) [API](https://serpapi.com/) (building one myself as we speak).

You can both use a publicly available MCP server; if you are also a [Cloud Run](https://cloud.google.com/run?hl=de) fan, you can try Steren’s [cloud-run-mcp](https://github.com/GoogleCloudPlatform/cloud-run-mcp)…

![](https://cdn-images-1.medium.com/max/1024/0*miTPRvJV6nn0hle7)

.. or build your own! Note: ricc-turbo-rails8-chat ([app ](https://rails8-turbo-chat-dev-272932496670.europe-west10.run.app/)— [code](https://github.com/palladius/rails8-turbo-chat)) is a ruby chat i’ve created and I expose some data publicly, as a test.

![](https://cdn-images-1.medium.com/max/1024/0*nK-F5CVisv1KTqWs)

And the AppMetadata function returns important here’s a meaningful JSON status of my app:

![](https://cdn-images-1.medium.com/max/1024/0*3KrGNszhHlFhJS8M)

Link to some of my favorite MCP servers and to docs of MCP readme /mcp.

If you want to browse more MCP servers, you can look [here](https://modelcontextprotocol.io/examples) and [here](https://github.com/modelcontextprotocol/servers).

### It can make mistakes, but you can automate checking!

On an instance, I’ve found that the model would make mistakes and “hallucinate” events/talks I’ve never been to. I’ve just added one line to [GEMINI.md](http://gemini.md) to check with me for every event he’d add and look:

![](https://cdn-images-1.medium.com/max/1024/0*ZQFWIkCr3wWlGBm5)

Now this kind of error won’t happen again!

### Ok Riccardo, I buy. But what is it good for?

I believe the sky is the limit 🩵 . I’ve been using gemini-cli with GEMINI.md to automate a number of different jobs. For instance:

1. **Long-standing background job.** Use a mix of git log for “historical git blame” to get the timestamp of when I added each line of an array of repositories I have somewhere. Note the “created on” comments are from Gemini and it took minutes to fetch, during my lunch break of course 🙂. Result:

![](https://cdn-images-1.medium.com/max/588/0*0v7MiIum0FPHEiaZ)

Let me repeat it in case you missed it: Gemini CLI just used git log to find when each repo was added! This job would have taken *me *a few hours.

1. **Search the web.** Use GoogleSearch Tool to search on the internet if I forgot any article or video of myself; if so, add them to my [palladius/my-sessions-and-bio/](https://github.com/palladius/my-sessions-and-bio/) repo with a meaningful [commit message](https://github.com/palladius/my-sessions-and-bio/commit/5f6b5c2e2a530c1563834fc65f167cef40bd807e) and [changelog](https://github.com/palladius/my-sessions-and-bio/blob/main/CHANGELOG.md) entry. It just works!
2. **Gemini2Gemini loops**. Anything where you can set it up for “closed loop”, any task you can think of where Gemini can try things out, check the output, and refine it. Since it’s a CLI, anything which runs in CLI is a good possibility. An hour ago I’ve tried my first “optimize my super long .bashrc and ensure it runs in less than a second”

![](https://cdn-images-1.medium.com/max/1024/0*qRQ9RDPTf1prc_wP)

💡To unleash the true power of gemini-cli, give it a task where the feedback is in the CLI output, not in the browser!.

### Lesson learnt / Pro tips

- **AutoMagic Feedback Loop.** The tool works best when the “developer Feedback Loop” is self contained within the gemini cli invocation. Let me explain with an example. If the CLI *can see *the error, you can automate the loop until the error is fixed. This is actually a fun to observe (eg, “Wait Gemini, there’s an error -> do make test and solve it yourself”). This is of course impossible if for instance you need a visual UI feedback where human intervention is needed (but there are JS to simulate browser interactions, just saying..).

![](https://cdn-images-1.medium.com/max/1024/0*4eg2GavLkL6mJBaK)

- **Declarative** vs **imperative** [GEMINI.md](http://gemini.md) (weekend lessons). This weekend I found something weird happened: my [GEMINI.md](http://gemini.md) contained instructions to create function a and b. But after that, my codebase grew to also have function c. When I restarted the session and told Gemini CLI to fix my code, it read the instructions, and proposed a change to remove function c. I was puzzled! But it made sense! Solution: change the phrase from “do x y z” to “ensure x y z”. Think you’re `kubectl apply`-ing a YAML 🙂 In alternative, tell Gemini CLI to piggyback what they do and update GEMINI.md. That also works!
- **Folders matter**. The folder where you invoke gemini-cli does matter, particularly in sandbox mode. For instance, if you have a monorepo and you invoke gemini-cli on the subfolder with your app, which seems absolutely reasonable to avoid confusing the LLM with code you don’t care about at the moment, it loses the ability to do git commits or git pushes. Why? Because it tries to mutate files outside your chroot’ed folder. Feature or bug? In Google we say “working as intended” 🙂
- 💡**Markdown memory.** If you don’t want to use gemini-cli magic memory, but you want to persist it over time, you can add a sentence like this:* “Choose any language between Go, ruby, Python, javascript, rust. Whichever language has the most appropriate libraries to get the job done without bloating the code. Explain your reasoning to me, and keep adding it to a `AI_REASONING.md` file.” *Now, whichever choice gemini will do will be persisted in the [AI_REASONING.md](https://github.com/palladius/vibecoding/blob/main/vibecheck/AI_REASONING.md) file which you instruct gemini to go an read on subsequent invocations. And of course, you can tweak that file to change further behaviours — after all, it’s English text! We just invented a fluid memory. Note — I came out with this trick before learning that gemini-cli also has built-in memory so — please try them both!
- 💡 export SEATBELT_PROFILE=none to disable the seatbelt sandbox on macOS.

Did I trigger your curiosity?

- Check this out: [https://github.com/google-gemini/gemini-cli/](https://github.com/google-gemini/gemini-cli/)
- Try this [“Getting started with Gemini CLI” codelab](https://codelabs.developers.google.com/codelabs/codelabs/gemini-cli-getting-started?utm_campaign=CDR_0x89ad3e41_platform_b422075371&utm_medium=external&utm_source=blog) from Aaron and me!

![](https://medium.com/_/stat?event=post.clientViewed&referrerSource=full_rss&postId=da5630d00434)

---

[Vibe coding my first Chrome Extension with gemini-cli !](https://medium.com/google-cloud/vibe-coding-my-first-chrome-extension-with-gemini-cli-da5630d00434) was originally published in [Google Cloud - Community](https://medium.com/google-cloud) on Medium, where people are continuing the conversation by highlighting and responding to this story.