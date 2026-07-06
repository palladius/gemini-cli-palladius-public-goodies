---
title: "Gemini CLI: vibecode a Next.js app and push to the Cloud!"
author: Riccardo Carlesso
pubDate: Fri, 27 Jun 2025 09:48:51 GMT
link: https://medium.com/google-cloud/gemini-cli-vibecode-a-next-js-app-and-push-to-the-cloud-c1f30c50136d?source=rss-b5293b96912f------2
tags: google, google-cloud-run, google-gemini-cli, next-js-13, gemini-cli
---

# Gemini CLI: vibecode a Next.js app and push to the Cloud!

*Originally published at [Medium](https://medium.com/google-cloud/gemini-cli-vibecode-a-next-js-app-and-push-to-the-cloud-c1f30c50136d?source=rss-b5293b96912f------2) by Riccardo Carlesso on Fri, 27 Jun 2025 09:48:51 GMT.*

On June 25rd, the [DeepMind team has dropped a bomb](https://blog.google/technology/developers/introducing-gemini-cli-open-source-ai-agent/?utm_campaign=CDR_0x89ad3e41_awareness_b424096451&utm_medium=external&utm_source=blog) 💣: gemini-cli!

I’m so excited to show you how it works so.. why don’t we **code an application from scratch**?

I had this idea of making a more complex and good looking version of [palladius/my-sessions-and-bio](https://github.com/palladius/my-sessions-and-bio) and.. let’s choose a language that I don’t speak? What did you say, Latin? *Tamen Latine loquor*. Uhm, let’s try something more esoteric and incomprehensible, like… **Javascript**!

![](https://cdn-images-1.medium.com/max/1024/0*uYs9_1djT6uxOkte.png)

If you’re curious:

- [Download gemini CLI](https://github.com/google-gemini/gemini-cli) or try this [Getting Started codelab](https://codelabs.developers.google.com/codelabs/codelabs/gemini-cli-getting-started?utm_campaign=CDR_0x89ad3e41_awareness_b424096451&utm_medium=external&utm_source=blog)!
- My App — [**code** (complete with juicy prompts!)](https://github.com/palladius/vibecoding/tree/main/apps-portfolio) and [on Cloud Run](https://portfolio-app-272932496670.europe-west1.run.app/) 😉. Code features: Terraform, Build scripts, .. all written by Gemini CLI!

### How to get started with Gemini CLI

You can get access to Gemini CLI upon launch via either:

```
npm install @google/gemini-cli
npx @google/gemini-cli
brew install gemini-cli
```

![](https://cdn-images-1.medium.com/max/562/0*PY167B_XQG7YcS36.png)

### It all starts with a prompt..

You have an idea for an app? Put it in GEMINI.md. This should have both your schema/database requirements, functional and non functional requirements, UI, language and everything. In my case, I started with this:

Curious to know **my initial prompt? **Here you are:

![](https://cdn-images-1.medium.com/max/977/1*E9TCwJ_jFU5Ddnn45v6NPQ.png)
*Copy from here if you wish:[INITIAL_PROMPT.md](https://github.com/palladius/vibecoding/blob/main/apps-portfolio/INITIAL_PROMPT.md)*

Note my Initial prompt changed a lot over time — note the differences between [INITIAL_PROMPT.md](https://github.com/palladius/vibecoding/blob/main/apps-portfolio/INITIAL_PROMPT.md) (first version) and my [GEMINI.md](https://github.com/palladius/vibecoding/blob/main/apps-portfolio/GEMINI.md) (latest version).

You can then keep interacting. When Vibe Coding, I find useful asking Gemini to thoroughly **document** what he’s doing: README, VERSION/CHANGELOG and why not, Mermaid graphs!

![](https://cdn-images-1.medium.com/max/1024/0*2Wws67SSNw-2FEQ6.png)
*Mermaid in markdown…*

Oh wow, first thing you do a READMEwith a mermaid graph of your proposed schema?!? I dig that! Best start ever!

![](https://cdn-images-1.medium.com/max/686/0*MRY-iAiNpkyHCnmr.png)
*.. and mermaid rendered! So easy to spot mistakes in this form!*

Then it adds a justfile, since i asked politely in the GEMINI.md file. Time to create the app (gemini chose **Next.js**):

![](https://cdn-images-1.medium.com/max/1024/0*dzgJxQYWH_vaikUa.png)

And here’s the first hiccup: Gemini tries to create the app in a non-empty directory, fails, and then course-corrects by moving the files, creating the app, and moving them back. This is the part I love the most: he tries, makes a mistake, and adjusts based on CLI output!

All without me doing anything except *<ACCEPT>*. Love it!

### Populating the data

Next, we started populating the data, first into a YAML file, then to SQLite. Gemini created the etc/data.yml file and a script to import the data. I asked to rename the file to .yaml and Gemini did it, along with updating the import script.

Then we hit our first real error. I could have copied and pasted the error, but I decided to teach Gemini to fish.

> *Dear Gemini, I can see there is a module not found error on UI (which you can’t see). But the same error appears on **just run . So I ask you: can you teach me to run npm in a way that we log somewhere under a git-ignored log/ folder which you can comfortably read and grep? Teach me how to run npm to dump its output to log so we can automate this.*

And Gemini did it! It created a log directory, updated .gitignore, and modified the justfile to add a run-dev command that redirects all output to log/dev.log.

### This was a **magic moment** where I understood that GeminiCLI can find the errors and fix them himself!

![](https://cdn-images-1.medium.com/max/1024/0*pCvu6gbsLDKs58lh.png)
*A bit ugly, but data are correctly displayed.*

### Pushing to the Cloud

With the app running locally, it was time to push it to the cloud. I asked Gemini to create a cloudbuild.yaml file and it even taught me how to configure my project. We hit a few bumps along the way, including some company policies, but Gemini was able to navigate them and get the app deployed.

We got interrupted a few times, but Gemini was able to pick up where we left off. I even added some information to GEMINI.md to help it, a practice I called "prompt reflection".

And finally… we’re [**live**](https://portfolio-app-272932496670.europe-west1.run.app/)!

![](https://cdn-images-1.medium.com/max/1024/0*IQVYmQYoaToOvsQi.png)
*Still ugly, but online!*

### What about terraform?

I’ve always sucked at Terraform. What if the AI can do it for me? I asked Gemini to set up a Cloud Build trigger with Terraform. It was a dream!

![](https://cdn-images-1.medium.com/max/888/0*x_XxHXix9XwOph1v.png)

### Back to the UI

With the CI/CD pipeline set up, we could focus on the UI. We added a footer, cards for the talks and articles, and even country flags for the events.

![](https://cdn-images-1.medium.com/max/1024/0*fMx52EO9ppX2gvrK.png)

But I have no time to download one image per event, I’m a **lazy developer (TM)**!

I wanted to **automate** image picking, so I asked Gemini to find a service that could take screenshots of URLs. It found one, and we were able to generate images for the articles and talks.

![](https://cdn-images-1.medium.com/max/840/0*eMcWVGeYZMIwIE6K.png)

We added tests, a navigation bar, and an “About Me” page. We even made the app responsive, with a calendar view for upcoming talks.

![](https://cdn-images-1.medium.com/max/1024/0*WDgdQ67g81cdTqQR.png)

The only effort on my side was to get a key online on [Api Flash](https://apiflash.com/) and add one line to my .env -> lazy enough for me!

```
# retrieved here: https://apiflash.com/
APIFLASH_ACCESS_KEY="my-key"
```

Until 5 minutes ago, I wasn’t aware Api Flash site existed!

💡Lesson learnt: ***YOU concentrate on the outcomes, and Gemini likely will find a way.***

### My first bug: Test-Driven Development with Gemini

I found a regression in the API. Instead of just asking Gemini to fix it, I asked it to write a test first.

> *Hey Gemini, I see there’s an error in this URL: *[*http://localhost:3001/talks/2025-10-14-agents-on-a-plane-a-deep-dive-into-building-a-real-time-travel-agent*](http://localhost:3001/talks/2025-10-14-agents-on-a-plane-a-deep-dive-into-building-a-real-time-travel-agent)* Seems like the /talks/<talk_id> route is broken. (1) can you verify this error yourself without me telling you? Show me the error you see. (2) can you first add a test that fails if this route gives 4xx/5xx? (3) after you show me that **just test fails with it, please fix it 😃 And resist the temptation to fix it first! 😃*

Gemini crafted the test…

![](https://cdn-images-1.medium.com/max/1024/0*74XxVbXwCcjvU1Zf.png)

…and it failed, just as expected!

This is a great example of how you can use gemini-cli to follow a [TDD ](https://en.wikipedia.org/wiki/Test-driven_development)workflow.

### 🪫Wait: The database is empty!

At some point, we realized the production database was empty. After some troubleshooting, we found the issue and fixed it. This was another great example of how Gemini can help debug complex issues.

### A big mistake… and a lesson learned

Gemini made a big mistake and tried to overwrite my .env file. I was so angry I started using capital letters **DO NOT TOUCH .env EVER!**, but it was a good learning experience for both of us. Gemini now knows to never touch .env files.

![](https://cdn-images-1.medium.com/max/1024/0*Ugy8vKKrAz_HAF_b.png)
*Riccardo getting angry with poor Gemini*

How? By using [**Memory**](https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/commands.md)!

![](https://cdn-images-1.medium.com/max/800/0*tgkhOORMavkZ7CwR.png)
*Thanks to Memory, B̶a̶r̶t̶̶ Gemini has learnt not to do it again!*

### The final result

After a lot of work, we have a beautiful portfolio app, built from scratch with the help of gemini-cli.

![](https://cdn-images-1.medium.com/max/1024/1*5E6SFBbHaHOT0MtjISuSDw.png)
*[Pretty UI for a Dev guy](https://www.youtube.com/watch?v=QtTR-_Klcq8)*

### Conclusions

We were able (Gemini CLI and I) to:

1. Create an app from scratch with gemini-cli.
2. Set up **Terraform** for some of its infrastructure.
3. Set up a working **CI/CD **pipeline with **Cloud Build **to push to **Cloud Run**.
4. Set up a justfile to help Gemini dig Cloud Build errors and other customer errors.
5. Create a consistent Database of usable data ([data.yaml](https://github.com/palladius/vibecoding/blob/main/apps-portfolio/etc/data.yaml)) with very little help from me.
6. Current version took me ~**7 hours** to achieve current version 0.12.4

All without knowing anything about Javascript or Typescript. I’m not even sure which language I’m using!

### Lessons Learned

- [GEMINI.md](https://github.com/palladius/vibecoding/blob/main/apps-portfolio/GEMINI.md) is your best friend!
- Teaching the AI to fish is more rewarding than endlessly copying and pasting error logs. “Teach them to fish” became my mantra. It’s about giving the AI the tools and context it needs to solve problems on its own.
- Gemini CLI is really good at local tools like git and similar — weaponize your CLI! And beware of uncommited files ;)
- Gemini is good at managing both **CODE** and **DATA **interchangeably**.**
- Use [justfile](https://github.com/palladius/vibecoding/blob/main/apps-portfolio/justfile)/Makefile to streamline/DRY actions you want Gemini to do (check my [justfile](https://github.com/palladius/vibecoding/blob/main/apps-portfolio/justfile)!)

Remember, it’s all about weaponizing the 🔁 Feedback Loop!

![](https://cdn-images-1.medium.com/max/1024/1*6vLb0UdvjKZmR9pYpVPFrg.png)
*Check my frank discussion with my coding mate — Gemini CLI!**I**do run dev,**YOU**check the logs!*

### Get started with Gemini CLI

You can get access to Gemini CLI upon launch via either:

```
npm install @google/gemini-cli
# or
npx @google/gemini-cli
```

What are *you* waiting for?

![](https://medium.com/_/stat?event=post.clientViewed&referrerSource=full_rss&postId=c1f30c50136d)

---

[Gemini CLI: vibecode a Next.js app and push to the Cloud!](https://medium.com/google-cloud/gemini-cli-vibecode-a-next-js-app-and-push-to-the-cloud-c1f30c50136d) was originally published in [Google Cloud - Community](https://medium.com/google-cloud) on Medium, where people are continuing the conversation by highlighting and responding to this story.