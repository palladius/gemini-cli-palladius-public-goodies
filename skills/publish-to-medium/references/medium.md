# 🟢 Medium Cross-Posting Playbook (`references/medium.md`)

Empirically verified operational guide for staging technical articles into **Medium** (`https://medium.com`) as **unpublished drafts**.

> [!CAUTION]
> **DRAFT-ONLY HITL GATE**: Never click **"Publish"**, **"Publish now"**, **"Submit"**, or **"Schedule"**. Every automated helper must enforce a hard regex denylist against publish actions and stop at **`Saved`** (`/p/<story_id>/edit`).

---

## 1. Browser Architecture: Why Real Authenticated Chrome (`DevToolsActivePort`) Wins

Live testing revealed three compounding traps with isolated Puppeteer / MCP browser instances:

1. **Google OAuth Rejection**: Browsers launched with `--enable-automation` are blocked at `accounts.google.com/v3/signin/rejected` (*"This browser or app may not be secure"*).
2. **Cloudflare Turnstile**: Unauthenticated automation profiles trigger Cloudflare Turnstile challenges on `medium.com` (which agents must never attempt to solve or bypass).
3. **Chrome 136+ `DevToolsActivePort` Protocol**: Enabling remote debugging at `chrome://inspect/#remote-debugging` writes `<port>\n/devtools/browser/<uuid>` to `DevToolsActivePort` (`~/.config/google-chrome/DevToolsActivePort` on Linux, `~/Library/Application Support/Google/Chrome/DevToolsActivePort` on macOS). Chrome 136+ speaks **WebSocket-only** on that endpoint (HTTP `/json/list` returns `EOF`) and prompts *"Allow remote debugging?"* once per WebSocket connection.

**Winning Pattern (`$SKILL_DIR/scripts/cdp_medium_draft.py`)**:
- Ask the user once to toggle **Discover network targets / Allow remote debugging** at `chrome://inspect/#remote-debugging` and keep **one `https://medium.com` tab** open in their authenticated Chrome window.
- Connect over **one single persistent WebSocket session** (`Target.getTargets` → `Target.attachToTarget` with `flatten: true`), executing copy, paste, editor audit, settings canonical update, screenshots, and optional `[TEST - DELETE ME]` cleanup in a single connection so the user clicks **Allow** only once.
- Note: While connected, Chrome displays its gray info bar (*"Chrome is being controlled by automated test software [Turn off in settings]"*). This is Chrome's own local debugging indicator, **not** a Medium block.

---

## 2. Method B (Native Blink Copy+Paste) vs. Method A (`/p/import`) — Live Empirical Comparison

| Dimension | **Method B: Native Blink Copy + Paste (`paste-html` — RECOMMENDED)** | **Method A: URL Importer (`import-url` on `/p/import`)** |
| :--- | :--- | :--- |
| **How it works** | Opens local `file:///.../out/medium/index.html`, selects `#medium-story-title` + `#medium-story-body` via DOM `Range`, dispatches native CDP `Copy`, navigates to `https://medium.com/new-story`, and dispatches native CDP `Paste`. | Navigates to `https://medium.com/p/import`, types public URL into central `div.js-importUrl`, clicks `Import` → `See your story`. |
| **Remote Images (`200 OK`)** | **Auto-uploaded by Medium** directly onto `cdn-images-1.medium.com` (`1376px` full resolution with `data-image-id`)! | Auto-imported from live page if Medium's scraper can reach all assets. |
| **Broken / Un-synced `404` Images** | `cdp_medium_draft.py` pre-filters HTTP `404` `<img>` tags into visible `[TODO: Upload missing image]` callouts so Medium never halts with `"Uh oh! Something went wrong uploading the image"`. | Silently drops or breaks un-deployed images. |
| **Local Draft Edits** | Reflects local compiled HTML edits (`build.py` fixes, table-to-list conversions, `&nbsp;` code blocks) **immediately**, even before redeploying your blog! | Only sees what is already deployed on the public URL (subject to Embedly caching). |
| **Canonical Link** | Set via `/p/<story_id>/settings` → `Advanced Settings` → `Customize Canonical Link`. | Auto-populated to imported URL (always verify in `/p/<story_id>/settings`). |

---

## 3. Seven Medium Editor & DOM Quirks Verified Live

1. **NEVER Use Synthetic `new ClipboardEvent('paste')` on `/new-story`**:
   - **Symptom**: Dispatching an untrusted JS `new ClipboardEvent('paste', { clipboardData })` strips `src` from `<img>` tags (`imgSrc: null`), creating corrupted Graf image nodes that cause Medium's backend delta-saver to show a red error banner: **`"Something is wrong and we cannot save your story"`** and never assign a `/p/<id>/edit` URL.
   - **Fix**: Always perform **native Blink `Copy` + `Paste`** via CDP `Input.dispatchKeyEvent` (`commands: ["Copy"]` on a rendered `file://` DOM `Range`, followed by `commands: ["Paste"]` on `/new-story`).
2. **Multi-Line `<pre><code>` Splitting on Blank Lines**:
   - **Symptom**: Medium splits `<pre><code>` blocks into separate boxes at every empty line (`\n\n`).
   - **Fix**: Replace blank lines inside `<pre><code>` with `\n&nbsp;\n`. Verified live across 17 Ruby/Bash/Mermaid blocks (up to 20 lines each): zero block splits, and Medium even auto-detects syntax highlighting (e.g., `Auto (Bash)`).
3. **Protect Code Spans Before Inline Markdown Regexes**:
   - Protect fenced ` ``` ` blocks and inline `` `...` `` code spans with placeholders (`@@CODEBLOCK_i@@`, `@@INLINECODE_i@@`) *before* running bold/italic/link regexes so globs (`"*.rb", "*.yml"`) and ANSI escapes (`\e[32m`) are never mangled into `<em>` or `<a href>`.
4. **HTML `<table>` Degenerates into Disconnected `<blockquote>`s**:
   - **Symptom**: Medium's editor has zero `<table>` support (`tablesCount: 0`) and converts every `<th>` and `<td>` cell into separate `<blockquote>` elements (a 6-row × 3-column table becomes 19 disconnected blockquotes!).
   - **Fix**: Convert Markdown tables into semantic `<ul><li><strong>Col1</strong> — Header2: Val2 · Header3: Val3</li></ul>` bullet lists (or pre-rendered PNG cards) when compiling HTML for Medium.
5. **Loose Ordered Lists (`1. ...\n\n2. ...`)**:
   - Ensure blank lines between consecutive numbered items do not close and reopen `<ol>`, otherwise Medium renders every item as `1.`.
6. **DOM Selector Traps on `/p/import` and `/p/<id>/settings`**:
   - **On `/p/import`**: `document.querySelector('input')` matches Medium's top-right navbar `Search` bar (`placeholder="Search"`, `y < 80`)! Exclude header/search inputs; the central import field is `<div class="textInput textInput--large js-importUrl u-textAlignLeft editable" placeholder="http://www.yoursite.org/your-post">` (`y > 100`), and requires firing `input` + `keyup` events after inserting text so the `Import` button enables.
   - **On `/p/<id>/settings`**: Click `button` matching `/^Advanced Settings$/i` specifically (`querySelectorAll('button')`). Using `querySelectorAll('div, button')` hits an outer wrapper `<div>` with identical `.innerText` (`"Advanced Settings"`), which absorbs `.click()` without expanding the accordion!
   - **Editor DOM Auditing**: Scope `querySelectorAll('figure, img, pre')` to `.postArticle-content, section.section--body` — Medium's bottom `"Writing on Medium"` onboarding carousel injects 5 empty `<figure>` elements outside the article body.
7. **Videos (`.mp4`), Animated `.gif`s, and Mermaid**:
   - Reachable `HTTP 200` animated `.gif` URLs (`< 25 MB`) upload cleanly as inline animated images; `HTTP 404` `.gif` URLs trigger `"Uh oh! Something went wrong uploading the image"`.
   - Raw `.mp4` `<video>` tags are stripped — upload videos to YouTube and place the bare `https://www.youtube.com/watch?v=<ID>` URL on its own paragraph line (press `Enter` in the editor to trigger Embedly), or auto-swap `.mp4` to a companion `.gif` (`<= 24 MB`).
   - `mermaid` fences and LaTeX math (`$$...$$`) are rasterized locally to 3x Retina / 300-DPI PNGs via `$SKILL_DIR/scripts/render_blocks.py`.
8. **Enterprise Chrome DLP Prompts on Local File Uploads (`DOM.setFileInputFiles`)**:
   - On managed corporate Chrome workstations, uploading local disk files (`.png`/`.gif`) via `<input type="file">` triggers an enterprise DLP confirmation dialog asking the user to confirm the images are public.
   - **Zero-Popup Best Practice**: Deploy public images, companion `.gif`s, and `rendered/*.png` diagrams to your primary HTTPS blog **first** so Medium ingests 100% of them server-side via native HTML paste without triggering local file-upload DLP dialogs. When staging before blog deploy, inform the user upfront so they can approve the DLP prompt.
9. **Story Settings Complete Metadata (`Topics`, `SEO Title`, `SEO Description`, `Canonical Link`)**:
   - On `/p/<story_id>/settings`, `cdp_medium_draft.py` automatically populates and saves **all four** metadata fields (`Add a topic...` up to 5 keywords from `data-topics`, `SEO Title` from `data-title`, `SEO Description` `<= 155` chars from `data-description`, and 2-step `Customize Canonical Link`: check *This story was originally published elsewhere* → click **`Edit canonical link`** to unlock the read-only URL box → insert canonical URL → click **`Save canonical link`**).
10. **NEVER Call `Page.bringToFront` or Raw `Element.remove()` Inside Medium's Editor**:
    - Calling `Page.bringToFront` raises the Chrome OS window on X11/Wayland/macOS and hijacks the user's live keyboard input into `h3.graf--title`. Always use `Emulation.setFocusEmulationEnabled({enabled: true})` instead, and fire OS desktop notifications (`notify-send` / `osascript`, suppressible with `--no-notify`) at START ("please don't focus that Chrome window until I'm done") and END (*"Don't Panic — SEP field off, now 100% your responsibility"*).
    - Calling raw DOM `p.remove()` on a `<p class="graf">` node desynchronizes Medium's internal Graf paragraph array, truncating subsequent blocks and breaking delta-saves. Clear placeholder paragraphs via native `Range.selectNodeContents(p)` + `Backspace` (`p.graf--empty.is-selected`).
11. **Medium's `1*b31hiO4ynbDLRrXWEFF4aQ.png` Skeleton Trap & `<figcaption>` Reset**:
    - Immediately upon pasting `<img src="https://...">`, Medium mounts a `700x400` white skeleton image hosted on `cdn-images-1.medium.com/max/1250/1*b31hiO4ynbDLRrXWEFF4aQ.png` (`naturalWidth: 700`). Upload pollers **must** exclude `1*b31hiO4ynbDLRrXWEFF4aQ` (or pass `--prefer-local-files` to upload all images directly from `out/medium/` via `DOM.setFileInputFiles`), otherwise navigating away commits solid white `700x400` rectangles!
    - When async image ingestion finishes, Medium re-mounts each `<figure>` and resets `<figcaption>` to `"Type caption for image (optional)"`. Always run post-upload caption hydration (`populate_all_figure_captions`) after all images settle.

---

## 4. End-to-End CLI Recipes (`cdp_medium_draft.py`)

```bash
# 1. Check open medium.com tab in authenticated Chrome
python3 "$SKILL_DIR/scripts/cdp_medium_draft.py" status

# 2. Stage local compiled HTML as a real Medium draft (Method B — Recommended)
python3 "$SKILL_DIR/scripts/cdp_medium_draft.py" paste-html \
  --html path/to/out/medium/index.html \
  --url "https://example.com/posts/my-article/" \
  --title-prefix "" \
  --out-dir /tmp/medium_stage_out

# 3. Run side-by-side A/B sandbox test and auto-delete [TEST - DELETE ME] drafts afterward
python3 "$SKILL_DIR/scripts/cdp_medium_draft.py" ab-experiment \
  --url "https://example.com/posts/my-article/" \
  --html path/to/out/medium/index.html \
  --out-dir /tmp/medium_ab_out \
  --cleanup-after

# 4. Sweep any leftover [TEST - DELETE ME] drafts
python3 "$SKILL_DIR/scripts/cdp_medium_draft.py" cleanup-test-drafts
```
