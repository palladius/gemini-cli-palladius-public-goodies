---
title: "How I used “AI Studio build” to create a Conversational German/French teacher for my kids!"
author: Riccardo Carlesso
pubDate: Thu, 30 Oct 2025 12:47:01 GMT
link: https://medium.com/@palladiusbonton/how-i-used-ai-studio-build-to-create-a-conversational-german-french-teacher-for-my-kids-7a7bb98de4c1?source=rss-b5293b96912f------2
tags: gemini-cli, gemini, vibecodinglist, google-ai-studio, voice-assistant
---

# How I used “AI Studio build” to create a Conversational German/French teacher for my kids!

*Originally published at [Medium](https://medium.com/@palladiusbonton/how-i-used-ai-studio-build-to-create-a-conversational-german-french-teacher-for-my-kids-7a7bb98de4c1?source=rss-b5293b96912f------2) by Riccardo Carlesso on Thu, 30 Oct 2025 12:47:01 GMT.*

A few days ago, I bumped into this LinkedIn update from [Logan Kilpatrick](https://www.linkedin.com/in/logankilpatrick/):

![](https://cdn-images-1.medium.com/max/1024/1*VfIkjsZoXq9Y2rQKpoIq7w.jpeg)
*[https://ai.studio/build](https://ai.studio/build)has landed!*

I am a huge fan of [**AI Studio**](https://ai.studio/), as it empowers me to prototype stuff and, as a coder, copy paste bash/python code to then tweak to my liking in my swiss-army knife Gemini script. I’ve also loved [**Firebase Studio**](https://firebase.studio/), as the sleekest vibe coding tool I’ve ever seen!

*.. but this is something else entirely!*

#### 👣 Dipping my toes into AI Studio Build

- I entered [https://ai.studio/build](https://ai.studio/build) and I see **16 cards** to choose from (!). Check just a few here:

![](https://cdn-images-1.medium.com/max/608/1*XLwO33-Kt_eePKQYSrlAkA.png)

- I click “**Nano Banana powered app**” and ask to create a simple editing tool:

![](https://cdn-images-1.medium.com/max/898/1*74cyTCHi69BOQRMuJxeOdw.png)
*All tabs you click give Gemini an applet with prompts and sample code to choose from*

- I click the “**build” **button.

One minute later, a Node.js application is created with a familiar canvas on the side. If you used Firebase Studio, it’s a very similar experience. The app is created, and run for me on the browser.

![](https://cdn-images-1.medium.com/max/1024/1*qzSz2O_e3I4w6zVN3y380Q.png)
*I’ve uploaded a[Rubycon](https://rubycon.it/)logo, and asked to “Add a Banana on bottom left”*

![](https://cdn-images-1.medium.com/max/1024/1*VpmQ8D_21cRLTU4pnAmckA.png)
*Banana added!*

So the editor works!

**Note: **Last week I’ve vibecoded another one ([permalink](https://ai.studio/apps/drive/1STkpI07Sn5UqPcjVlR5IiLuWzLLMaheH)) and I got to this point in 30m of work (the one above was created now to match prompt to images just for this article, since I’ve lost the original prompt):

![](https://cdn-images-1.medium.com/max/1024/0*SypoO1cW20DgN1vV)
*My other experiment from a week ago.*

You can also easily **deploy** it! Look:

![](https://cdn-images-1.medium.com/max/315/1*1cB5Hdt8tyitFlbRqIZT4A.png)
*The rocket icon does the trick*

1. Click the Deploy icon
2. Chose project id
3. .. and in 20 seconds you’re on Cloud Run! [https://vibecoded-gemini-image-editor-272932496670.us-west1.run.app/](https://vibecoded-gemini-image-editor-272932496670.us-west1.run.app/)
4. .. and ready to show off to your friends!

**Note**: remember to protect your app, or anyone from the internet will be able to leverage your Gemini API Key to generate countless banana images!

#### Ok, let’s do something useful now..

**A bit of context.** I had a crazy week: my son is 7, he has a French exam on Monday, German on Thursday (today), and English tomorrow. Yes, he’s ~quadrilingual. This is not about bragging, is about explaining the linguistic confusion a 7-year-old can encounter. His Italian and English are really good, but his German is average and French is *very* basic. I teach him French, but my German is not good and it’s very frustrating since I can’t check his vocabulary.

#### 👅 Enter LingoLeap!

I noticed that AI Studio build also supports “**conversational voice app**s”. WOOOT? I can have Gemini talk to my kids without writing a line of code?This is amazing!

![](https://cdn-images-1.medium.com/max/949/1*J4VFhqEahcb5UJFh5TY96w.png)
*This is how the magic starts!*

After a bit of vibecoding, I was able to have:

1. I want to have Gemini speak Italian, English, French and German to my kids, with configurable values like difficulty, topic, and student name

![](https://cdn-images-1.medium.com/max/354/1*7BQVGr8iE0i5wWItBaepRg.png)

2. Session audio recorded locally

![](https://cdn-images-1.medium.com/max/1024/1*rGKWaaOeuVAGeADQfQA7_Q.png)

3. Image per session generated, based on history (note the flags on the image):

![](https://cdn-images-1.medium.com/max/1024/1*O-SuBZ9fBOw4KZ7oH2rDBA.png)

4. *Ça va sans dire*, a **text transcription**:

![](https://cdn-images-1.medium.com/max/693/1*sQbfDBhIxoTYZMuEDfNsgQ.png)

5. A **leaderboard**, since gamification is a thing (have I mentioned I have TWO boys? They’re very competitive!)

![](https://cdn-images-1.medium.com/max/680/1*YObXA1cnBgkS9nkZsfqJLg.png)
*If you join my game, please use Guest!*

#### [Expert only] Productionize to Cloud Run and save to Firebase

“It works in localhost” is a great way to start. But how do we deploy it?

- The easy way is to click on the deploy icon, and you have a perfect end-to-end no-code vibecoding experience.
- If you want more control, you can actually commit to Github, download locally, and edit locally. Note that once you do that you are “detached” from AI Studio build, and you are NOT going back: the GitHub feature is single direction.

In my case, I wanted to have more control, so I “detached” from AI Studio and started working on my baby locally, with quick feedback loops, extensive testing, and I was able to add:

- Persist images and audio to **Google Cloud Storage**.
- Persist conversations to **Firestore**.

#### Conclusions

**Prons**

- I love that I can share the app with my friends! Prompt, code, frontend all included! Eg, my quick-and-dirty [Gemini Image Editor](https://ai.studio/apps/drive/1STkpI07Sn5UqPcjVlR5IiLuWzLLMaheH).
- **Exporting** to **GitHub **is a GREAT feature!
- **Taylored code**. Clearly, selecting those “cards” empowers your app with the right model, the right code, to make it work. I saw it with my own eyes!
- **Sky is the limit**. You can mix around *Images*, *Video*, [*Maps* grounding](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/grounding/grounding-with-google-maps), .. I’ve created a Canvas app which edits/creates a markdown beside my local Google Map, and allows me to interactively write tables of results which get updated as I chat with restaurants open tonight near me, based on today’s taste, and custom metadata.

**Cons**

A few things IMHO are still perfectible.

1. The **GitHub export** feature is **limited**. If you edit the code LOCALLY, web app won’t be able to sync with it, it will stubbornly push it’s own code. I’ve tried to sync from web after making local changes, and it just pushes Web changes discarding theirs in the git merge.
2. **Code editor **is opinionated and quite **limited**. For instance, I can’t edit the .env.local nor add a justfile : only TypeScript is allowed!
3. **Loses memory at reload. **While **checkpointing **is available, you’ll lose chat history (and checkpoints) after reload. I mean, you can save to GitHub on every iteration, but you still can’t rollback on the UI if not from the current session.

#### My verdict

**AI Studio** latest “**build**” feature is breath taking. You can go from zero to hero in 5–30 minutes and create a working POC. However, if you want to go from good to perfect, you can’t stay on browser, and you want to leverage a local environment, like **Gemini CLI** + Visual Studio + git.

Remember: the product came out less than a week ago, so this is early stages to judge. I’m super excited for what’s next!

***Note****: Code is at *[*https://github.com/palladius/lingoleap-ai-tutor*](https://github.com/palladius/lingoleap-ai-tutor)* (private ATM). AI Studio Shared app is *[*here*](https://ai.studio/apps/drive/1vmrs8gLSsG_QAVPvWs-UfjlcBm5dA4ud)* though. *The app is **deployed **[here](https://lingoleap-x42ijqglgq-ew.a.run.app/chats) (Please use it sparingly -> I haven’t made it multi-login yet, so chats are public).

![](https://medium.com/_/stat?event=post.clientViewed&referrerSource=full_rss&postId=7a7bb98de4c1)