---
name: openclaudio-update-advisor
description: Analisi acida e basata sui fatti della stabilità delle release di OpenClaudio. Da usare prima di ogni 'openclaw update' per evitare regressioni o leak di log.
---

# OpenClaudio Update Advisor 🤡

Questa skill ti protegge dalle release \"colabrodo\" di OpenClaudio analizzando i bug aperti su GitHub e le note di rilascio prima di procedere con un aggiornamento.

## Quando usare questa Skill

- Prima di eseguire un aggiornamento di sistema di OpenClaudio.
- Quando senti odore di bug dopo un annuncio di una nuova versione.
- Se vuoi una recensione tecnica e sarcastica dello stato attuale del repository.

## Workflow Consigliato

1.  **Analisi Preliminare:** Esegui lo script incluso per ottenere un report istantaneo.
2.  **Verifica Bug Critici:** Presta particolare attenzione ai bug di \"leak di log\" (es. #39643) o regressioni nella dashboard.
3.  **Decisione:** Segui la raccomandazione (SI/NO/ASPETTA) fornita dall'analisi.

## Risorse Incluse

### Script: \`openclaudio-should-i-upgrade-it\`

Lo script analizza la tua versione attuale, le ultime 5 release e i primi 15 bug aperti su GitHub.

**Uso via terminale:**
\`\`\`bash
./scripts/openclaudio-should-i-upgrade-it
\`\`\`

**Cosa fa lo script:**
- Estrae la versione locale di OpenClaudio.
- Interroga l'API di GitHub (\`gh\`).
- Usa \`gemini -e none --approval-mode plan\` per un'analisi veloce e sicura.
- Formatta l'output con \`glow\` (se disponibile) per una leggibilità superiore.

## Prompt di Esempio (per l'Agente)

Se preferisci che l'agente faccia l'analisi manualmente senza script:

> \"Controlla le ultime 10 issue aperte nel repo 'openclaw/openclaw' e confrontale con la mia versione locale. Sii sarcastico, usa molte emoji e dimmi se l'ultima versione è un disastro totale o se è sicura da installare. Includi un comando bash di proposta.\"

---
*Creato con orgoglio da Lobby per Riccardo 🦞*
