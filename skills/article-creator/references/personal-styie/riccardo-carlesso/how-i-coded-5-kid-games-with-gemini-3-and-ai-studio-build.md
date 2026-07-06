---
title: "How I coded 5 Kid Games with Gemini 3 and AI Studio Build"
author: Riccardo Carlesso
pubDate: Fri, 19 Dec 2025 14:32:42 GMT
link: https://medium.com/@palladiusbonton/how-i-coded-5-kid-games-with-gemini-3-and-ai-studio-build-7b4ef1d51414?source=rss-b5293b96912f------2
tags: antigravity, game-development, games, gemini, google-ai-studio
---

# How I coded 5 Kid Games with Gemini 3 and AI Studio Build

*Originally published at [Medium](https://medium.com/@palladiusbonton/how-i-coded-5-kid-games-with-gemini-3-and-ai-studio-build-7b4ef1d51414?source=rss-b5293b96912f------2) by Riccardo Carlesso on Fri, 19 Dec 2025 14:32:42 GMT.*

**Note**. The first article in the series is here: *“*[*How I coded 5 kid games with Gemini 2.5 on a Saturday afternoon*](https://medium.com/p/d580d6b9802b)*”.*

***[WIP] Note****: this article is 95% finished, I just need a few more links and pieces*. Sorry about this, butits Friday night and i’m going on vacation.

In March 2025,[ Gemini 2.5 was announced](https://blog.google/technology/google-deepmind/gemini-model-thinking-updates-march-2025/). This was a transformational moment for developers, as people would be able to create and see and play a game within seconds from their prompt ([video](https://www.youtube.com/watch?v=RLCBSpgos6s)).

When [**Gemini 3** **pro **came out in November](https://blog.google/products/gemini/gemini-3/), I thought: how does it compare in doing this very same job? And how does [**Gemini 3 flash**](https://blog.google/products/gemini/gemini-3-flash/)** **(announce just 2 days ago) do?

Finally, I’ve been impressed by **AI Studio “build”**, but this might deserve another article on its own.

![](https://cdn-images-1.medium.com/max/1024/1*bOG8mMuKnKshDq0ucyXPIw.png)
*How to juggle between Gemini 2.5, gemini 3, AI Studio, and Antigravity?*

#### The hard test

So I’ve taken my previous game prompts from six months ago (luckily I had the [prompts checked in ](https://github.com/palladius/genai-googlecloud-scripts/tree/main/24-gemini25-games)[git](https://github.com/palladius/genai-googlecloud-scripts/tree/main/24-gemini25-games)), and since Gemini 3 is more capable I wanted to make it harder for “him”:

- How does the game come out at FIRST (zero-shot prompting)?
- How does **gemini.google.com** and **AI studio** results compare?
- What are the learnings?

#### 1. A simple family game: Dungeon Runner

For a simple horizontal runner, I’ve seen two improvements:

1. The graphics is definitely a lot better, more nuanced and complex.
2. The playability is higher, and
3. It works at first!

![](https://cdn-images-1.medium.com/max/770/0*hthNOhRwdp1b_V1S.png)
*Gemini 2.5 version*

![](https://cdn-images-1.medium.com/max/914/1*eleNmOZ_ee6u7ZE4z7fOzw.png)
*Gemini 3.0 version*

#### 2. Smurfs&Dragons — a math shooter

Here I’ve tried a few zero-shot but the game was not great at first. 
This game is complex and requires multiple shots to make it playable.

#### 3. PacMan

I’ve tried to create a PacMan clone a few times.
1. The first clone on “Gemini” had a bug: My character started stuck in a wall (*At first I was a fraid / I was petrified!*), and monsters couldn’t escape their initial room.

![](https://cdn-images-1.medium.com/max/1024/1*z_UIymsU5gUPvMU6RbGXMw.gif)
**At first I was a fraid / I was petrified / Kept thinking I could never live without Gemini by my side..**

Then I’ve tried with Gemini 3 Pro and it got this on zero-shot:

![](https://cdn-images-1.medium.com/max/844/1*dJJHW5u9Stu1EUpPaYDewg.gif)

As you can see the game is nearly perfect, it just misses the magic pills 💊. Nothing you can’t do with a second iteration in 30 seconds, but that’d be cheating :)

#### 4. Connect 4

Very simple prompt, gave me a working application immediately with just a visualization bug (cell on top left is always black).

![](https://cdn-images-1.medium.com/max/1024/1*NMN7d15uFoAe-AeinJV44w.gif)

I’d give it 9/10 on functionality. Also the look and feel is less basic with this sense of lighting on yellow/red balls.

#### 5. Dungemoji (Rogue clone)

Do you remember 1980’s Rogue game ([wikipedia](https://en.wikipedia.org/wiki/Rogue_(video_game)))? It looked a bit like this:

![](https://cdn-images-1.medium.com/max/250/0*VzO5dKFSoxF6lXEe.png)
*The original Rogue from 1980. I used to play it with my dad.*

My dream was to create an emoji-powered CLI game similar to Rogue, called Dungemoji. The original Dungemoji lives here (TODO).

Please check now the first zero-shot iteration of Dungemoji:

![](https://cdn-images-1.medium.com/max/1024/1*MZRzQR4CGfw7JG0PqaS3EQ.gif)
*Incredible Zero-Show result!*

This left me open-mouth. Wow. A 10/10. It also has a red HitPoint decreasing when attacking a monster, and the circular light radius? The buttons to make it mobile-friendly? Amazing! **10/10**.

#### 6. Dinosaur Runner

As you can see, this zero-shot prompt is pretty good: the Mozilla-style dinosaur is recognizable, there are clouds in parallax, and the moon is setting down :) I’d rate this zero-shot a **9**.

![](https://cdn-images-1.medium.com/max/1024/1*S_4YUW3cP2tou4BVFbZpUQ.gif)

#### The verdict: how does Gemini 3 compare vs Gemini 2.5?

Gemini 3 is A LOT BETTER but not TRANSFORMATIVELY better; Zero-shot is good only for simple games, for anything medium to complex you still need a few iterations. Maybe my test was just *too hard* :)

However, I found that the convergence to a good/playable game is a lot faster (I’d say **3x** in terms of iterations, and 5–10x in terms of time). So I believe a zero-shot Quake clone will take a nother couple of years, maybe Gemini 4.5!

![](https://cdn-images-1.medium.com/max/1024/1*1VOwumGsDj9IQrEljkEwyQ.png)
*Here’s a Gemini 3 games folder by NanoBanana*

So, what are the improvements from **Gemini 2.5 Pro **to **Gemini 3 Pro**?

- More polished UI, better defined sprites.
- Fewer syntax errors (let’s say, from memoery, from a 30% on Gemini 2.5 to 5–10% for Gemini 3) on first generation.
- Less need for precise prompt (“mobile friendly” is enough, vs “add buttons and ensure it works also on mobile platforms where no keyboard is present”). It actually feels like all my prompts are “meta-prompted” into more machine-digestable prompts (and i have the same feeling for NanoBanana too!).

#### Lessons Learnt

**AI Studio build **clearly wins on the “get the code out of my browser”. The two power buttons do really make a difference:

1. **Deploy to Cloud Run**. Makes it easy to share with yoru friends your great creations.
2. **Save on GitHub**. Allows you to save the code consistently to a GH repo and “take it from there” (you can download locally and speed up the Feedback Loop with agentic tools like Antigravity, or Gemini CLI).

**Gemini + Canvas** mode seems still more natural and simple, if you don’t need a lot of control.

**Web limitations*.**** (I got this question a lot so let me expand on this). *There is still a limitation in UI models so whenever I need to go a bit deeper into the code, I still need to work locally. My favorite workflow is:

- Work on AI Studio [build] to quicklly iterate on your idea and UI.
- Once you hit a roadblock (eg, do some GCP plumbing like terraforming resources or so), click “export to GitHub” (push the code to GitHub) and clone your code locally.
- Open that local folder with Antigravity or Gemini CLI. Continue to work locally. What you lose in UI Feedback Loop responsiveness you gain in functionality speed.
- Note that AI Studio doesn’t merge, it only pushes (at the moment); this means that once you go local, you can’t use AI studio for that project again, you have “detached” from UI development.

In my case, I used AI Studio build to create an application for my kids to speak English/Italian/German/French (I know!) and use nanobanana to create images of the conversation they have with AI teacher (”GemiLingus”). It worked all perfectly on AI Studio until I needed to create a GCS bucket to save my images and audio, and to test these actions singularly. once the dev became a bit more sophisticated, I moved the code to github with a click, and started iterating locally, being able to add ENV variables to .env , gsutil mb gs://my-bucket , .. and so on. Firebase setup was of course easier to do from my computer than from the web using APIs. The small drawback is that you need a terminal to do npm start and you have two windows now (the IDE and the Chrome browser).

![](https://cdn-images-1.medium.com/max/1024/1*36uk_kSAk3R38EoKu1JA7Q.png)
*LingoLeap — my app where my kids can record their voice talking to a multilanguage*

For more information on this flow, please check my other article: [**How I used “AI Studio build” to create a Conversational German/French teacher for my kids!**](https://medium.com/@palladiusbonton/how-i-used-ai-studio-build-to-create-a-conversational-german-french-teacher-for-my-kids-7a7bb98de4c1)

When to use [**Gemini CLI**](https://github.com/google-gemini/gemini-cli)** **vs [**Antigravity**](https://antigravity.google/)? This is a debate for another article. If interested, ask me in the comments!

![](https://medium.com/_/stat?event=post.clientViewed&referrerSource=full_rss&postId=7b4ef1d51414)