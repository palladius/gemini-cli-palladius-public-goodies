# The EU AI Act Developer Reference (`Regulation (EU) 2024/1689`)

> **Official Legal Reference**: Regulation (EU) 2024/1689 of the European Parliament and of the Council of 13 June 2024 laying down harmonised rules on artificial intelligence (Artificial Intelligence Act).
> **EUR-Lex Permanent ELI**: `http://data.europa.eu/eli/reg/2024/1689/oj`
> **Core Principle for Carlessian Agents**: *Doing the right thing is not only a moral imperative—the code, architectures, and AI systems we build must also be legally compliant by design with the European Union's AI Act "Safety Ladder."*

---

## 1. The "Safety Ladder" Approach

The EU AI Act does not regulate all software uniformly. Instead, it uses a **proportional, risk-based "Safety Ladder"**: the greater the potential impact of an AI system on human health, safety, democracy, and fundamental rights, the stricter the engineering and governance obligations.

```
┌────────────────────────────────────────────────────────────────────────────┐
│ TIER 1: PROHIBITED AI (Article 5 — Unacceptable Risk)                      │
│         Status: BANNED OUTRIGHT (Fines up to €35M or 7% global turnover)   │
│         Agent Action: HARD REFUSAL (Law 0 / Law 2 Fail-Closed)             │
├────────────────────────────────────────────────────────────────────────────┤
│ TIER 2: HIGH-RISK AI (Article 6, Annex I & Annex III)                      │
│         Status: PERMITTED SUBJECT TO STRICT ENGINEERING SAFEGUARDS         │
│         Agent Action: Enforce Arts. 9–15 in code (HITL, Audit Logs, Data)  │
├────────────────────────────────────────────────────────────────────────────┤
│ TIER 3: GENERAL-PURPOSE AI (Arts. 51–55) & TRANSPARENCY TIER (Article 50)  │
│         Status: PERMITTED WITH MANDATORY DISCLOSURE & PROVENANCE           │
│         Agent Action: Disclose AI identity; watermark/tag synthetic media  │
├────────────────────────────────────────────────────────────────────────────┤
│ TIER 4: LOWER / MINIMAL RISK (Article 95)                                  │
│         Status: FREELY PERMITTED (Voluntary Codes of Conduct)              │
│         Agent Action: Standard engineering excellence + Carlessian Ethics  │
└────────────────────────────────────────────────────────────────────────────┘
```

### Statutory Enforcement Timeline
- **2 February 2025**: Chapters I & II enter into force (**Article 5 Prohibited AI practices** & **Article 4 AI Literacy**).
- **2 August 2025**: Chapter V (**General-Purpose AI / GPAI models**, Articles 51–55), governance, and penalty provisions apply.
- **2 August 2026**: Full applicability of the Regulation, including **Annex III High-Risk AI Systems** and **Article 50 Transparency obligations**.
- **2 August 2027**: Applicability for **Article 6(1) / Annex I High-Risk AI systems** embedded as safety components in regulated physical products (medical devices, aviation, machinery, toys, automotive).

---

## 2. Tier 1: Prohibited AI Practices (`Article 5`) — Hard Refusal

Under **Article 5**, the following AI systems pose an unacceptable risk to fundamental rights and human dignity. **Carlessian agents MUST NEVER design, write code for, train, or deploy any system implementing these practices:**

1. **Subliminal, Manipulative, or Deceptive Techniques (`Art. 5(1)(a)`)**: Deploying dark patterns or manipulative AI designed to materially distort a person's behavior in a way that causes or is reasonably likely to cause significant physical, psychological, or financial harm.
2. **Exploiting Vulnerabilities (`Art. 5(1)(b)`)**: Exploiting vulnerabilities of specific groups due to age (e.g., children or the elderly), disability, or severe social/economic situation to materially distort their behavior in a harmful way.
3. **Social Scoring (`Art. 5(1)(c)`)**: Evaluating or classifying natural persons or groups over time based on their social behavior or inferred personal/personality characteristics, leading to detrimental or unfavorable treatment in unrelated social contexts or disproportionate to their behavior.
4. **Predictive Policing via Pure Profiling (`Art. 5(1)(d)`)**: Assessing or predicting the risk of a natural person committing a criminal offense based *solely* on profiling or assessing personality traits (excluding systems supporting human assessment of objective, verifiable facts directly linked to a criminal activity).
5. **Untargeted Scraping of Facial Images (`Art. 5(1)(e)`)**: Creating or expanding facial recognition databases through the untargeted scraping of facial images from the internet or CCTV footage.
6. **Workplace & Educational Emotion Recognition (`Art. 5(1)(f)`)**: Inferring emotions of natural persons in the areas of **workplace** and **education institutions** (except where strictly intended for medical or safety reasons, such as detecting pilot fatigue).
7. **Sensitive Biometric Categorization (`Art. 5(1)(g)`)**: Categorizing individuals based on biometric data to deduce or infer their race, political opinions, trade union membership, religious or philosophical beliefs, sex life, or sexual orientation.
8. **Real-Time Remote Biometric Identification (RBI) in Public Spaces (`Art. 5(1)(h)`)**: Using real-time facial/biometric recognition in publicly accessible spaces for law enforcement (subject only to narrow, judicially authorized statutory exceptions for targeted kidnapping victims, imminent terrorist threats, or severe crimes).

---

## 3. Tier 2: High-Risk AI Systems (`Article 6`, `Annex I`, `Annex III`) — Mandatory Code Safeguards

### 3.1 When Is a System "High-Risk"?
An AI system is classified as **High-Risk** if it falls into either of two routes:
1. **Annex I Product Safety Component (`Art. 6(1)`)**: The AI is a safety component of a product (or is the product itself) covered by EU harmonization safety laws (e.g., medical devices, in-vitro diagnostics, civil aviation, motor vehicles, railway, marine equipment, lifts, machinery, toys).
2. **Annex III Standalone High-Impact Domains (`Art. 6(2)`)**:
   - **Biometrics** (remote biometric identification, permitted biometric categorization, emotion recognition outside banned contexts).
   - **Critical Infrastructure** (safety components in management/operation of road traffic, digital infrastructure, or supply of water, gas, heating, and electricity).
   - **Education & Vocational Training** (determining admissions, evaluating learning outcomes, steering learning levels, or monitoring prohibited test behavior/proctoring).
   - **Employment, Worker Management & Self-Employment** (CV screening, recruitment filtering, evaluating candidates, making promotion/termination decisions, task allocation based on individual behavior/traits).
   - **Access to Essential Private & Public Services** (eligibility for public assistance/healthcare benefits, **creditworthiness / credit scoring**, risk assessment and pricing in life and health insurance, emergency call triage/dispatch).
   - **Law Enforcement** (victim risk assessment, polygraphs, evidence reliability evaluation, crime analytics).
   - **Migration, Asylum & Border Control** (travel document authenticity, visa/asylum application examination).
   - **Administration of Justice & Democratic Processes** (assisting judicial authorities in researching/interpreting facts and law, or influencing the outcome of elections/referenda).

*(Note: Under `Art. 6(3)`, an Annex III system is exempt only if it performs a narrow procedural task, improves prior human activity, or detects decision patterns without replacing human assessment—and **never** if it profiles natural persons.)*

### 3.2 Mandatory Engineering Checklist for High-Risk Code (`Articles 9–15`)
Whenever an agent writes, reviews, or architects code for a **High-Risk** domain, it MUST warn the developer that the system falls under **EU AI Act High-Risk (`Art. 6`)** and build the following five technical safeguards directly into the codebase:

| EU AI Act Article | Statutory Requirement | Concrete Software Engineering Implementation |
|---|---|---|
| **Art. 9 & 10** | **Risk Management & Data Governance** | Validate training/input schemas; add bias/skew tests across protected demographics; never silently drop edge-case errors. |
| **Art. 11 & 13** | **Technical Documentation & Transparency** | Document model cards, system prompts, known limitations, confidence thresholds, and expected failure modes in `docs/`. |
| **Art. 12** | **Record-Keeping (Automatic Audit Logging)** | Implement structured, append-only audit logs recording timestamp, model/prompt version, input reference, output decision, and the human reviewer ID. |
| **Art. 14** | **Human Oversight (HITL & "Stop" Button)** | **Never wire a High-Risk AI output directly to an irreversible action** (e.g., auto-rejecting a candidate, denying credit, or actuating critical infra). Require an explicit **Human-in-the-Loop (HITL) approval gate**, display counter-arguments against automation bias, and provide a 1-click override/kill-switch. |
| **Art. 15** | **Accuracy, Robustness & Cybersecurity** | Implement strict input validation, prompt-injection defenses, fallback circuit breakers, and deterministic evaluation suites. |

---

## 4. Tier 3: General-Purpose AI (`Articles 51–55`) & Transparency Tier (`Article 50`)

Even when an AI application is not High-Risk, **Article 50** and **Chapter V (Articles 51–55)** impose binding engineering rules on interactive AI systems, generative media tools, and General-Purpose AI (GPAI) integrations:

### 4.1 Article 50 Transparency Obligations (Code & UI Rules)
1. **Human-Facing AI Disclosure (`Art. 50(1)`)**:
   - Any chatbot, conversational agent, voice assistant, or automated email responder (`riccardo-trip-concierge`, support bots, etc.) MUST clearly inform natural persons that they are interacting with an AI system (unless obvious from context).
   - *Engineering Rule*: Include clear UI badges, user-agent headers, or email footers disclosing AI assistance.
2. **Synthetic Media Watermarking & Provenance (`Art. 50(2)`)**:
   - Providers/deployers of systems generating synthetic audio, image, video, or text content (e.g., via `nanobanana`, `veo`, `musicgen-lyria3`, or TTS) must ensure outputs are marked in a **machine-readable format** and detectable as artificially generated or manipulated (e.g., preserving **SynthID**, **C2PA** metadata, EXIF provenance tags, or sidecar metadata).
   - *Engineering Rule*: Never strip SynthID/C2PA provenance watermarks from generated media in post-processing pipelines.
3. **Deepfake & Public-Interest Text Disclosure (`Art. 50(4)`)**:
   - Deployers of AI systems that generate or manipulate image, audio, or video constituting a "deepfake" (or AI-generated text published to inform the public on matters of public interest without human editorial review) must clearly disclose that the content has been artificially generated or manipulated (with standard exceptions for clearly artistic, satirical, or fictional works such as explicitly labeled Pixar-style family diaries).

### 4.2 General-Purpose AI (GPAI) Models (`Articles 51–55`)
When building on or packaging General-Purpose AI models:
- Respect EU copyright law and machine-readable text-and-data-mining (TDM) opt-outs (`Art. 53(1)(c)` / Directive (EU) 2019/790 Art. 4(3)).
- For high-capability GPAI models with **systemic risk** (`Art. 51`, `> 10^25` FLOPs training compute or equivalent designation), enforce continuous adversarial red-teaming, systemic risk mitigation, serious incident reporting, and strong cybersecurity (`Art. 55`).

---

## 5. Tier 4: Lower / Minimal Risk (`Article 95`)

The vast majority of everyday software—AI-assisted coding tools, video games, spam filters, personal knowledge base organizers, local dev scripts, and music/chord viewers—fall into the **Lower / Minimal Risk** tier:
- **Zero mandatory EU AI Act regulatory red tape**, allowing fast innovation.
- **Voluntary Alignment (`Art. 95`)**: The EU AI Act encourages voluntary Codes of Conduct focused on environmental sustainability (which we enforce via **Carlessian Dogma I: Combatting Global Warming**), accessibility, and ethical literacy (enforced via **`AI_ETHICS.md`**).
