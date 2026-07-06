---
title: "How I coded 5 kid games with Gemini 2.5 on a Saturday afternoon"
author: Riccardo Carlesso
pubDate: Mon, 07 Apr 2025 07:21:24 GMT
link: https://medium.com/@palladiusbonton/wip-code-3d-kid-games-with-gemini-2-5-d580d6b9802b?source=rss-b5293b96912f------2
tags: gemini-2-5, firebasehosting, google-cloud, prompt-engineering, javascript
---

# How I coded 5 kid games with Gemini 2.5 on a Saturday afternoon

*Originally published at [Medium](https://medium.com/@palladiusbonton/wip-code-3d-kid-games-with-gemini-2-5-d580d6b9802b?source=rss-b5293b96912f------2) by Riccardo Carlesso on Mon, 07 Apr 2025 07:21:24 GMT.*

The 25 March seems like just any other day, until Google Deepmind dropped this bomb: [**Gemini 2.5 is out**](https://blog.google/technology/google-deepmind/gemini-model-thinking-updates-march-2025/)! 
“*Our most intelligent AI model*” so far? Sure, it always is…

**So what’s the big deal?** I’ve seen the internet go crazy already, but if you haven’t seen it yet, let me show you. You can code games with a 3-line prompt:<a href="https://medium.com/media/f886135c5009b15753c5a7deff1ae18a/href">https://medium.com/media/f886135c5009b15753c5a7deff1ae18a/href</a>

***Note.**** If this article interests you, try this *[***step-by-step codelab***](https://codelabs.developers.google.com/codelabs/gemini-games-firebase#0)* i’ve just authored!*

I decided to try it out and create increasingly complex prompts.

In this article:

- I will paste my **prompts** for you to copy and try your own!
- I’ll also share my **code**.
- Finally, I’ll share my sacred **Feedback loop** and some tips (prompt -> code -> deploy -> prompt refinement -> …)

If you find them useful, let me know. If you have better ideas, *please please please* let me know! I want to learn from you!

**Note**: I can write good ruby and decent python — **I can’t write any Javascript.** This is important: I can do cut and paste and edit an existing Hash, that’s it :)

![](https://cdn-images-1.medium.com/max/1024/1*OOx8b7lt7EywFIIx1eneDw.png)
*Gemini 2.5 is coding for kids — courtesy of Imagen model*

1. [Dungeon Runner](https://incandescent-inferno-1052.web.app/) An endless runner featuring family members. Sounds…*unique*.
2. [Smurfs & Dragons](https://smurfs-and-dragons.web.app/) (Math Shooter). Math practice with a Smurf/Dragon theme! Now that’s what I call Edutainment!
3. [3D Googley Lego Tetris](https://gugley-3d-tetris.web.app/) Tetris with Google-coloured Lego in 3D. A spectacular creation, apparently.
4. [2D Lego-ish Tetris](https://legoey-2d-carlessian-tetris.web.app/) The 2D version, for those of us who find 3D *too* stimulating.
5. [Multilingual Anagrams](https://zurigram.web.app). Anagram game in multiple languages! Kate *must* see this!

If you’re impatient, **code and prompts** are illustrated [**here**](https://github.com/palladius/genai-googlecloud-scripts/blob/main/24-gemini25-games/README.md). All games are in [**this webpage**](https://g25-games.web.app/) (for my kids tablet)

And now.. *Game on, Wayne!*

#### 1. A simple family game: Dungeon Runner

As a first experiment, I wanted to copy the existing prompt which creates an endless runner game with p5.js. As a non-js developer, of course I don’t know what `p5.js` is, so I just copy the prompt :)

App: [https://incandescent-inferno-1052.web.app/](https://incandescent-inferno-1052.web.app/) (later I’ll get smarter and choose better names).
Code: [01-dungeon-runner](https://github.com/palladius/genai-googlecloud-scripts/tree/main/24-gemini25-games/01-dungeon-runner)

This is a Mario Bros clone where you choose one element of my family (Ale, Seby, Kate, Papino or our nanny Silvana), each with their totem “animal”:

![](https://cdn-images-1.medium.com/max/808/1*xbuX33tk9UnodHgF5vjCEQ.png)

The game is a pretty silly POC, and my kids got bored of it immediately, when I decided you could shoot at a wall rather than jumping it (Seby was frustrated as he couldn’t jump on time).

#### 2. Smurfs&Dragons — a math shooter

I wanted my kids to learn math having fun. Are you familiar with those vertical shooet’em’all where you choose between some red/blue flags which augment/punish your army which fights soldiers, skeletons and stuff? Well, I wanted to do the same adding what Alessandro and Seby love most (dragons and smurfs, respectively). Finally I wanted the math to be not trivial: is it better to get a “+10 or X 2” when you have 8? Not easy for a 7-year old.

![](https://cdn-images-1.medium.com/max/831/1*jFgZgA_gRYoap7aZ-qaY0g.png)
*We have 25 soldiers, should we choose x3 or +25 before we fight a 15HP dragon?*

Here’s my Prompt. Took me 20 min to think it through, and two executions.

```

My kids, aged 5 and 7, are learning Maths, and I'd like them to enjoy it.

The internet is full of clones of the same game which looks like this:

* eternal vertical scrolling app where your character (think of a shoot'em up app) can only move left-right on the bottom of vertical screen (in doubt, take my phone size which is a Pixel 8 "2400 × 1080 pixel").
* the controls are just left and right.
* In front of you you have an army of, initially, 1 soldier. That army can't grow to more than say 200 (MAX_SOLDIERS). The more soldiers you have the more firepower you have (this could be linear or, probably better, logarithmic in the number of soldier)
* Things will come towards you randomly, usually proposing some cunning choice between Addition and multiplication. Additions and Multiplication should be BLUE (good), and subtractions and divisions would be RED (negative).
* Getting to <1 soldier ends the game, and visualizes your score (you choose an algorithm to decide score, based on killings, or time, or both).
* Game score is visualized on top right in green at all time.
* Every challenge (as two random things, left and right) will come at a given interval (say 5 seconds, initially as `CHALLENGE_INTERVAL`). Decrease the interval slowly over time (say -0.1s every 10 seconds) to make the game harder with time.
* Every CHALLENGE will come in two forms:
* a Left/Right Math choice
* a number of soldiers to fight. If you have 30 soldiers and the soldiers come
* Note on the "random choice between left and right" part:
* If player is presented with a blue/red choice, such as [+10, -10], the choice is kind of obvious. So keep these at a minimum.
* The best choice is something like [+10, *2] or [+30, *4] where the player needs to actively think.
* Shooting at a red decreases its negativity. For instance, shooting at "-20" would make it a -19 and so on until it gets to max +10 (minus half of what it was). Shooting should be signified by a constant arrows to the front of you - you need to hit in the ballpark of the enemy for the damage to be absorbed, or the arrows will go to the end of the schema and will fail.
* Please create Five schema objects of increasing difficulty. As YAML files they'd look like this, but you're welcome to use a native JS object - keep it as succinct as possible because I'll have to maintain it often.

```yaml
# schema01.yaml # turn 01
challenges: # User starts at 1 soldier.
- choice: ['+10', '-10'] # Chooses between 11 and -9. If -9, its game over.
- enemies: 5 soldiers # you cant dodge them, you will go to 6.
- choice: ['+10', '*3'] # Now your math skills are at test: better left (16) or right (18)?
- enemies: 12 smurfs # Now you're down to 4 or 6, depending on what you chose.
- choice: [+5, -10] # You can get +5 or shoot at -10 and it gets more and more...
- enemies: 1 dragon # Dragons have 20 HP, and count as 20 enemies.
# ... < you choose. Length should be around 20. >
```

* My soldiers need to be visible on the bottom! I want to see my current army as N good soldiers (say green uniforms).
* **Graphics**. Please make some effort to design some simplistic non-animated figures. Some with dragons, smurfs (blue gnomes) and enemy soldiers (same as me but with red uniforms).
* On the control side, make sure my army is visible on the X axis. My position will determine if I choose left or right when the left/right challenge hits me. Maybe leave a 20% in the middle for me to try avoid both choices (40% left, 20% nothing, 40% right).

Make me a captivating, multi-turn math shooter game. Key instructions are on screen and dissolve after 5 seconds. p5js scene, no HTML. I like medieval style and colorful background. My kids like dragons and smurfs, so please use them as theme, together with simple/boring soldiers with pikes and helmets.
```

Game here: [https://smurfs-and-dragons.web.app/](https://smurfs-and-dragons.web.app/)
Code and prompt history is here: [02-smurfs-and-dragons](https://github.com/palladius/genai-googlecloud-scripts/tree/main/24-gemini25-games/02-smurfs-and-dragons).

#### 3. 3d Googley Lego Tetris

***Note****: this is the first time my initial prompt was too much for Gemini2.5 So I removed a few constraints to make it easier. Ultimately I’ve also tried the 2D (see app #4) but the 3D is so much better now :) this is probably the most spectacular code I have NOT written so far :)*

![](https://cdn-images-1.medium.com/max/616/1*sfaYbPfBiScuwAlkWkfYqA.png)
*The 3d view is pretty spectacular. Thanks Gemini!*

Prompt:

```
Design a 3D tetris clone where you can dump Lego pieces with the 4 colors of Google (red blue green yellow).
Technology: p5js scene, no HTML. Futuristic, colorful style.
Available pieces will be 1x1, 1x2, 1x4, 1x8, 2x1, 2x2, 2x4, 2x8, short (size 1) or tall (size 3).
The board will memorize what you put down in a chessboard which is 16x16 and say 100 units tall.
* Whenever a slice of the surface (16x16x1) is fully occupied by pieces, the pieces will disappear (tetris side). This will increase the score.
* **Controls**. You can use your mouse to go in four directions, and you can turn your piece to rotate 90 degrees (by clicking on the mouse), and force the piece to go down fast.
    * On computer, the controls will be: left/right/up/down, space bar (drop) and enter (rotate)
    * On mobile, a drag left/right/top/bottom will move the brick, and a tap will rotate it. A double tap will drop it down.
* The game will start slow and it will slowly increase over time.
* player loses when the tallest size is occupied.
* **Graphics**:
    * Graphically the legos need to have little circles, do not just render parallelepipeds, make some graphical effort here.
    * The big container 16x16x100 will need to be half transparent to allow user to see through, and some sort of grids will need to be visible to help the player make their choices.
    * Some sort of gray shadow (or darker brick's color) will help the player understand where the piece is going to land, in the three-dimensions. This can be hard to see, given the space.
* Upon game over, have a dramatic and fun rotation of my creation.
```

Code: [03-googley-lego-tetris-3d](https://github.com/palladius/genai-googlecloud-scripts/tree/main/24-gemini25-games/03-googley-lego-tetris-3d)
App: [https://gugley-3d-tetris.web.app/](https://gugley-3d-tetris.web.app/)

The hardest part here was: #TIL

- Importing “EasyCam”, a JS library for 3d rendering that of course I didn’t know of 5min ago. This library makes all your page drag and droppable to do the 2 lagrangian titlts to render the beautiful 3D in 2d — which is AWESOME, but also makes your 6 controls (Left right up down rotate drop) impossible. In the end I’ve agreed with Gemini that it was easier to have HTML have two canvas, one with Easycam and one with the 6 controls. I loved that Gemini said “let me first try my way last time then if it still doesn’t fix it we do your way”. It’s probably the most intelligent, wise sentence I’ve ever heard an AI say.

#### 4. 2D Lego-ish tetris

Here I took my 3D logic from above, and reduced by one dimension (I realized that rotating doesn’t make sense anymore). Good exercise for the mind, in case you wanted to create a 4D Tesseract :)

App: [https://legoey-2d-carlessian-tetris.web.app/](https://legoey-2d-carlessian-tetris.web.app/)
Code: [04-lego-tetris-2d](https://github.com/palladius/genai-googlecloud-scripts/tree/main/24-gemini25-games/04-lego-tetris-2d)

![](https://cdn-images-1.medium.com/max/502/1*uuXRmpP6Fi1BKBG9iFs50g.png)
*Googley legos on the … wrong side.*

Here’s my prompt:

```

Design a 2D tetris clone where you can dump Lego pieces with the 4 colors of Google (red blue green yellow).

Technology: p5js scene, no HTML. Futuristic, colorful background fantasy / color melange style.

Available pieces will be 1x2, 1x4, 1x8, 1x16, each in short (size 1) or tall (size 3). Probability of 1x8 and 1x16 is lower than others.
They board will memorize what you put down in a chessboard which is BOARD_WIDTH=20-wide and say 80 tall.
* Whenever a row (BOARD_WIDTH x 1) is fully occupied by pieces, the pieces will disappear. This will increase the score A LOT (say like lying 1 piece x 100).
*
* **Controls**. You can use your mouse to go in the two directions, and you can turn your piece to rotate 90 degrees (by clicking on the mouse), and force the piece to go down fast.
    * On computer, the controls will be: left/right, space bar (drop) and enter/up (rotate)
    * On mobile, a drag left/right will move the brick accordingly, and a tap or swipe up will rotate it. A swipe down or double tap will drop it down.
* The game will start slow and it will slowly increase over time, say 1% every 10 sec.
* player loses when the tallest row is occupied. In this case, show the score (and record the top 10 high scores from anonymous players and add YOU in whichever position it is). Keep the score in RAM, doesnt matter if we'll lose it over reloads :)
* **Graphics**:
    * Graphically the legos need to have the little circles above as proper legos, do not just render rectangles, make some graphical effort here. a 1x4 will have for instance 3 bumps which in 2D are pretty easy to signify - use some shading of the original colors to mimic this effect.
    * The big container wil show the tetris "chessboard", and some sort of grids will need to be visible to help the player make their choices.
    * Some sort of gray shadow (or darker brick's color) will help the player understand where the piece is going to land, in the 2-dimensions. This can be hard to see, given the space.
* Upon game over, have a dramatic and fun rotation of my creation.
* Since we have thin (1 in the Z-dimension) and thick bricks (3 in Z-dimension), the game can be messy. Therefore, let's add a fun "3 consecutive thing bricks" rule:
    * If three EQUAL thin pieces land on each other (say 3 thin 1x3 in perfect line one above each other, or 3 1x8 thin bricks in perfect line, and so on), there will be a little explosive graphical effect (or blur, whichever you prefer) and then destroy the whole row of those 3 Z-coordinates.

Again, design a p5js script, with simple/no HTML interaction.
The app needs to work both on browser and on mobile.
```

My personal failure here was to be able to [make Gemini] render legos from the side. I always wanted to randomize the slim pieces vs thick pieces, with 1 thick = 3x thin. But seems like I’m one of the few humans to know “the Fundamental Equation of Lego thickness”. 🥺

#### 5. Multilingual anagrams #Omakase

I was awake at 4am — and decided to go to my computer at 6, finally. At 630 I had a working copy and was shouting to my wife *“Kate, Kate! You must see this!”*

![](https://cdn-images-1.medium.com/max/769/1*LMfQ686jjsoHQD5HY4btWA.png)
*Can you spell card in IT EN DE? This is easy. Note the British flag — Gemini erroneously gave me the American one, but how would I explain my British wife?*

Initial Prompt:

```
I have two kids, aged 5 and 7, who are native speakers of English, Italian, and German;
the big one is also learning French (!). I would like to build a fun game which 
they can play on a mobile. I was thinking of an anagram game where they need to
position the words correctly when they start scrambled. Since they're starting to
read, I think giving them a visual feedback of what they're trying to build could help.
You will have a list of words in the three languages, for each you'll have a structure like this:

```javascript
words = [
{emoji: '🍎', it: 'mela', en: 'apple', de: 'apfel', fr: 'pomme' },
{emoji: '👀', it: 'occhi', en: 'eyes', de: 'eigen', fr: 'yeux' },
]
```
```

You can now swap letters to get “car/auto” in all possible ways. when correct, you jump to the next word. Note Gemini also created a nice dictionary of words with three levels of difficulty!

It took me 10min to get a working demo, and ~3 hours to get it to work with keyboard, mouse and touch on my android.

Code: [05-multilanguage-word-game](https://github.com/palladius/genai-googlecloud-scripts/tree/main/24-gemini25-games/05-multilanguage-word-game)
App URL: [https://zurigram.web.app](https://zurigram.web.app)

### My [SDLC](https://en.wikipedia.org/wiki/Software_development_process) / Feedback Loop

Let me spend a couple of words on how it works for me. I also came up with a new DORA: the Feedback Loop Dev Time (FLDT).

![](https://cdn-images-1.medium.com/max/816/1*g2aCHz8wLrz0XGkTRhIznA.png)

It all starts usually with an insomniac night where I think of what an LLM can do for me.

1. I give a prompt, wait ~10sec for Gemini2.5 to paste the p5js code.
2. I go to [editor.p5js.org](http://editor.p5js.org/) and paste the JS blurb there.
3. Press play and see if it works. this only tests keyboard and mouse. We also need to test it on mobile.
4. As lazy non-mobile user, I don’t test on my computer: I just push it to **Firebase**. Takes 10 seconds :) the hardest part is to force the latest version (as HTML/CSS/JS are heavily cached and nobody taught me how to “uncache” them server-side). Check my justfilecode to see how.
5. If something is not working fine, there are two cases:
6. [early catch] You catch it on [editor.p5js.org](https://editor.p5js.org/): you can paste the text error or a screenshot of the error and you’re good. *FLDT =~ 15 sec*
7. [prod catch] If the error can only be caught on mobile, you need to copy code from Gemini, paste it on editor, it works there. Paste it on local vscode, then push from CLI, try with your phone (after refreshing the cache or it will use the previous version, so also bump version in HTML file by 1 for visual feedback). FLDT =~ *90 sec*

I’m sure you can use some mobile tools to test the mobile phone on your desktop to decrease the production error loop.

#### Lessons learned and tips

I’ve learned that Gemini 2.5 can code a working demo in less than 2 minutes. To make it do what you want it to do (with a healthy feedback loop), it takes me a couple of hours.

A few tips:

- **Gemini prompting history**. If you want to find the code and prompt back/forth you were giving when moving from one computer (say — at home) to another (say — at work), it’s important to be able to find your chats. I found that pinning my chats and renaming them with a fitting emoji / initial helps me a lot. This will allow you to find all your prompts at once:

![](https://cdn-images-1.medium.com/max/646/1*TXZaKaB2dMRzqsS9NzUzVQ.png)

- **Firebase hosting** rocks! There is nothing simpler, and cheaper, to launch a new static app on the web. Plus it’s a free 3rd-level domain as you wish: *<your-desired-appname>.web.app* ! Thanks Guillaume for the tip.
- **Multimodal code vibing** is a thing. How cool it is to attach a screenshot of an error or of a poor UI rendering?

![](https://cdn-images-1.medium.com/max/900/1*t7Sn082FXrJ_LhrGcohnUA.png)
*Here I’ve just pasted the error visually.*

- **Size matters**. With 1M+ tokens (**2M** coming soon!) you can count on Gemini to be able to “store” within the current conversation a pretty complex demo program. Once your demo escapes the size of the LLM, you need to go back to vscode mode. Luckily, we got you covered too! Just install [Gemini Code Assist](https://marketplace.visualstudio.com/items?itemName=Google.geminicodeassist) and you can continue your Vibe Coding on your favorite IDE:

![](https://cdn-images-1.medium.com/max/640/1*MVZLypESkF4EUCmziCC7gg.png)

- **Easy to extend**. My friend Paolo (a non-coder) replicated my idea in a [**new app**](https://teal-georgianne-19.tiiny.site/) from just a couple of screenshots, thanks to Gemini 2.5! With the addition of Dutch and Lithuanian! (yes, where I live we have this thing of “how many languages do your kids speak?” and I definitely lose to Paolo). And what about *you*? Can *you* make a 4D Tesseract Tetris?

![](https://cdn-images-1.medium.com/max/565/1*1Y_D_chD3ooPUJM8-BZqDw.png)
*Pros and Cons of using Gemini 2.5.. :)*

*.. Excellent!*

![](https://medium.com/_/stat?event=post.clientViewed&referrerSource=full_rss&postId=d580d6b9802b)