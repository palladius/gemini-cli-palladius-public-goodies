---
title: "AI-Powered SRE: How Antigravity Saved My Netlify Build"
author: Riccardo Carlesso
pubDate: Wed, 04 Feb 2026 00:00:01 GMT
link: https://medium.com/@palladiusbonton/ai-powered-sre-how-antigravity-saved-my-netlify-build-1cf5eb69f0e6?source=rss-b5293b96912f------2
tags: gemini-cli, sre, antigravity, ruby, netlify
---

# AI-Powered SRE: How Antigravity Saved My Netlify Build

*Originally published at [Medium](https://medium.com/@palladiusbonton/ai-powered-sre-how-antigravity-saved-my-netlify-build-1cf5eb69f0e6?source=rss-b5293b96912f------2) by Riccardo Carlesso on Wed, 04 Feb 2026 00:00:01 GMT.*

Everyone knows GenAI is good for coding. I mean, even [Linus is vibecoding with Antigravity](https://news.ycombinator.com/item?id=46569587) now!

However, **how AI can help SREs and Operators is still up for debate;** This article by Ramon and me sheds light on how Google is approaching this now.: [***How Google SREs Use Gemini CLI to Solve Real-World Outages***](https://cloud.google.com/blog/topics/developers-practitioners/how-google-sres-use-gemini-cli-to-solve-real-world-outages)***.***

I’m at work when my friend Elia from the [Rubycon](https://rubycon.it/) team tells me: *“Riccardo, Netlify can’t update *[*our site*](https://rubycon.it/)* anymore!”*

Luckily, the site is not down, it’s just stuck!

![](https://cdn-images-1.medium.com/max/1024/0*hVxaq3mn29z3h_17.png)
*This Image generated at the very end of this story :)*

In this article, we’ll see how Antigravity and Gemini CLI can help:

1. Troubleshoot [Netlify](https://www.netlify.com/) build issues, quite brilliantly.
2. Implement fixes and document changes for future reuse.
3. Build a **Post Mortem** (timeline + action items!) via **Custom Commands**. Use the Workspace MCP to create an actual [Google doc](https://docs.google.com/document/d/1ba21A7ShDCqPhNBJxpH6sV3dSFQaOeDxy4VgrkurouM/edit?tab=t.0)!

All links on how I did it are at the bottom of this page.

### Honey, I Shrunk the CI/CD!

*aka How I broke Netlify auto-build.*

I love [Netlify](https://www.netlify.com/). I use it to maintain my countless websites and blogs, built with jekyll or hugo. Sometimes, the pipeline breaks, and you need to read the logs. I used to fix things manually, before AI. Now I just paste the logs or, better, use an MCP or CLI to have it downlod it for me :) ("teach them to fish" strategy).

This morning, I get pinged by my friend Elia from the Rubycon team: “Riccardo, Netlify can’t update our site anymore!”.
“Sure, file a GitHub issue and I’ll fix it”, I reply. I’m from the old “If it’s not on [buganizer](https://issuetracker.google.com/), it doesn’t exist” Google school of thought.

![](https://cdn-images-1.medium.com/max/762/0*JXdzM4VcUtPJe1_R.png)

Sounds familiar? Luckily I have **Antigravity**, **Gemini CLI**, and a number of tools at my disposal to right the wrong! Time to put my Ops hat on and fix this. So let’s start with…

![](https://cdn-images-1.medium.com/max/1024/0*a7G3QdDlE510wH-N.png)
*You’ll never guess my nationality from my PS1 ;)*

```
$ cd ~/git/rubycon.it/
$ antigravity .
```

### Antigravity keeps me in the Loop

Antigravity is great at keeping me in the loop, and surviving software crashes and computer reboots.

I write lazily (I could be a CEO now!) on the right side of Antigravity:

> *Help me troubleshoot this: *[*https://github.com/palladius/rubycon.it/issues/58*](https://github.com/palladius/rubycon.it/issues/58)

![](https://cdn-images-1.medium.com/max/1024/0*kuoOYS24mmDOU6Q1.png)
*Asking Antigravity to analyze the GitHub issue — notice how I can just paste the URL and it fetches the context automatically!*

After some thinking, Antigravity analyzes the issue, identifies the problem, and proposes a fix:

![](https://cdn-images-1.medium.com/max/1024/0*yFMWx_l--mNfBnF9.png)

Once the fix is ready, I simply tell Antigravity:

> *Comment on issue 58 with: 1. what the problem was, 2. what your fix was. Ensure you sign yourself as Antigravity.*

![](https://cdn-images-1.medium.com/max/1024/0*AVzFfAR_3salIp4E.png)
*Wham! The comment is posted automatically.*

Then I type:

> *ok git commit with gitmoji and push now!*

![](https://cdn-images-1.medium.com/max/1024/0*QN7OZ0-Lx-OtOrED.png)
*And we’re done! The fix is deployed.*

gitmoji is fancy and meaningful at the same time!

### The Post Mortem: “Have I told you about that time I broke PROD?”

*aka “An Operator enters the bar and tells his friends “Have I told you about that time I broke PROD?”. His friends sit down and sip calmly their beer while waiting for a great story to be told. It starts like this…”*

I’m Riccardo, the kind of Engineer who commits to PROD, no reviews, no questions asked. Last Saturday, I mistakenly committed a [new Equity page](https://rubycon.it/equity) and all of a sudden my website was all white! I’m not a chromatic snob, but I can tell if white over white is hard to read (when “Rubycon” reads “con”).

![](https://cdn-images-1.medium.com/max/1024/0*TSeGsjsTq6OniLEm.png)
*Broken on top (white over white) — correct below (white over red)*

But I’m also a tidy person, before fixing prod [I document it](https://github.com/palladius/rubycon.it/issues/57) and warn my friends on Whatsapp. The world can go on 🔥, but it needs to be tidy.

### The issue

As always, the problem was a commit: [a61a79d](https://github.com/palladius/rubycon.it/commit/a61a79d6e015bf4c8b05e2750fcee3342a89364a) . On Sat Jan 10 11:36:14 2026 I pushed a new page and all of a sudden my website was all defaced!

### The solution

- I’ve asked Gemini to fix it, and it did.
- I’ve also asked it to write a mini Post-Mortem, and [it did](https://github.com/palladius/rubycon.it/blob/main/doc/post_mortems/20260110-css-outage.md).

I won’t tell you how the fix was done; it’s the good old **feedback loop**:

- check git diff for culprit (breaking change was minutes ago, after all!)
- check curl localhost:8080 to reproduce the bad CSS until you fix it. This is a bit harder as the system has no EYES, but CSSs *can* be tested.

### The Post Mortem (via Custom Command)

Yesterday, I opened sourced a new Post Mortem Gemini CLI **Custom Command** *and* a **Skill**!. Today, I’ll try to reproduce the PoMo and show you some magic here. Let’s see it in action here:

> */sre:postmortem-create Look at breaking and fixing commits in *[*https://github.com/palladius/rubycon.it/issues/57*](https://github.com/palladius/rubycon.it/issues/57)* and follow
the PoMo procedure to create a PoMo doc. Ignore doc/post_mortems/20260110-css-outage.md — you’re smarter than that*

![](https://cdn-images-1.medium.com/max/1024/0*vju5gP_fUkbUhun8.png)

Code for /sre:postmortem-create Custom Command is available [here](https://github.com/palladius/gemini-cli-custom-commands/blob/main/commands/sre/postmortem-create.toml) ([SKILL.md](https://github.com/palladius/gemini-cli-custom-commands/blob/main/skills/post-mortem/SKILL.md) available too!).

Let’s see what happens with a few screenshots:

![](https://cdn-images-1.medium.com/max/1024/0*aQV0w46q3SnuLpKK.png)
*Gemini CLI starts reading GitHub, and then starts looking at the two interesting commits.*

![](https://cdn-images-1.medium.com/max/1024/0*ZeG0EdgTJD3oX0c4.png)
*It then created a CSV with the timeline, as instructed:*

![](https://cdn-images-1.medium.com/max/1024/0*TjnDJp-buUVDVvLk.png)
*Updates the PLAN.md (stateful)*

![](https://cdn-images-1.medium.com/max/1024/0*cnr3tys49oVlQeF0.png)
*… and finalizes it all.*

Finally, [*Gemini CLI*](https://github.com/google-gemini/gemini-cli) uses **Workspace MCP** to generate the final document.

![](https://cdn-images-1.medium.com/max/1024/0*DAjTHWKC4o6hxluz.png)
*You can find the Workspace MCP server[here](https://github.com/gemini-cli-extensions/workspace). It’s maintained by my friend[Allen](https://github.com/allenhutchison).*

![](https://cdn-images-1.medium.com/max/1024/0*609wGO1d8ijysFGX.png)
*And the doc is ready!*

- Gemini: *Would you like me to share it with anyone or file those action items as GitHub issues now? 🇮🇹🤌*
- Riccardo: *Yes why not. file AIs and then link them in the GDoc too.*

And that’s it!

- [Google Doc created](https://docs.google.com/document/d/1ba21A7ShDCqPhNBJxpH6sV3dSFQaOeDxy4VgrkurouM/edit?tab=t.0) :

![](https://cdn-images-1.medium.com/max/1024/0*i8lCtXie4-qAdX3r.png)
*This doc is a public copy. Note the Action Items and Timeline below.*

![](https://cdn-images-1.medium.com/max/1024/0*YN8f9acQoJ9jB96Y.png)
*… and the Action Items on GitHub!*

I then asked Gemini CLI to link the two AIs onto the original GH issue. We have a similar dependency mechanism in our internal Google Issue Tracker.

### Some final fun 🍌

I still need a nice image for article, don’t I?

> *finally use Nano Banana MCP to create an image of the outage in the same folder!*

![](https://cdn-images-1.medium.com/max/1024/0*Ze1uIIsIRNj_C-8c.png)

And the result is:

![](https://cdn-images-1.medium.com/max/1024/0*hVxaq3mn29z3h_17.png)

TA-DAH! Good enough!

If you’re interested, all steps are in: [doc/post_mortems/issue-57/](https://github.com/palladius/rubycon.it/tree/main/doc/post_mortems/issue-57). You can find the old PostMortem (created without any CC) in [doc/post_mortems/20260110-css-outage.md](https://github.com/palladius/rubycon.it/blob/main/doc/post_mortems/20260110-css-outage.md).

### Conclusions

This is how AI-assisted operations work in practice. With **Gemini CLI** and **Antigravity**, I can:

1. **Troubleshoot issues** faster by having AI analyze GitHub issues
2. **Implement fixes** with AI assistance
3. **Document changes** automatically. See [Issue #2](https://github.com/palladius/ricc.rocks/issues/2) for the fix and [Issue #3](https://github.com/palladius/ricc.rocks/issues/3) on how to do beautiful image captions with Hugo figures ("go figure", literally!)
4. **Handle parallel requests** thanks to Antigravity’s multi-threading.

The future of SRE work is here, and it’s powered by AI! 🚀

### Follow me for more, since Skills are coming for Gemini CLI!

- Do you love CLI? Download Gemini CLI here: 🔗 [Gemini CLI](https://github.com/google-gemini/gemini-cli)
- Want to pump it up with Riccardo’s Custom Commands, such as the PostMortem you’ve seen in action? 🔗 [Extension](https://github.com/palladius/gemini-cli-custom-commands/)
- Want to pump it up with Allen’s Workspace MCP? 🔗 [Extension](https://github.com/gemini-cli-extensions/workspace)
- Do you love vscode-type IDEs? Download 🔗 [Antigravity](https://antigravity.google/): it has Gemini CLI inside, like Tony Stark is powered by [Arc Reactor](https://ironman.fandom.com/wiki/.Arc_Reactor)
- Do you love **Ruby**? Want to know more about the classiest Ruby Italian conference? Check out 🔗 [Rubycon](https://rubycon.it/) ♦️

*Originally published at *[*https://ricc.rocks*](https://ricc.rocks/en/posts/medium/2026-02-04-gemini-cli-sre-build-redux/)* on Jan 14, 2026.*

![](https://medium.com/_/stat?event=post.clientViewed&referrerSource=full_rss&postId=1cf5eb69f0e6)