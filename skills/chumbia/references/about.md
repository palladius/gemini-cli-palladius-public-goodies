# About `chumbia` — Comparison & Architectural Lineage

> *"Questa skill somiglia a B e C, ma li supera per via di D, E ed F."*

`chumbia` è il protocollo definitivo di fine sessione ("le pulizie DOPO la fatica" + `/learn` piggyback).

Nel panorama degli agent skill framework per AI coding agents (Claude Code, Cursor, Codex, Gemini CLI, Antigravity), esistono strumenti eccellenti che affrontano pezzetti di questo ciclo di vita. In particolare:

1. **`obra/superpowers:finishing-a-development-branch`** (Jesse Vincent):
   - Si concentra sulla chiusura di un branch di feature e sul cleanup del relativo Git worktree.
2. **`obra/superpowers:verification-before-completion`**:
   - Impone il principio *"Evidence over Claims"*: vieta all'agente di dichiarare vittoria senza l'evidenza di comandi e test passati.

---

## ⚖️ Perché `chumbia` li supera (The D, E, F Advantage)

Mentre le skill sopra citate sono **atomiche e circoscritte a Git/Test**, `chumbia` è una **Session-End Suite olistica** che gestisce l'intero fine vita di una conversazione con un agente.

### 🛡️ D. Riconoscimento robusto dell'ambiente Worktree & Sequencer Guardrails
Superpowers ha introdotto il confronto tra `git rev-parse --git-dir` e `--git-common-dir` per rilevare worktree secondari o branch staccati. `chumbia` adotta ed estende questa logica con cicatrici di guerra reali:
- **Protezione da sequencer incastrati:** `git status --porcelain` nasconde gli stati di cherry-pick o rebase incompleti (`.git/sequencer/`, `CHERRY_PICK_HEAD`). Se i commit sono già approdati sull'HEAD, eseguire `git cherry-pick --abort` cancella il lavoro o sposta indietro `main`; `chumbia` impone tassativamente `git cherry-pick --quit`.
- **Riconoscimento di cherry-pick / squash:** Se un worktree non è stato unito con merge ricorsivo standard, `git merge-base --is-ancestor` restituisce `1` (falso allarme). `chumbia` esegue il fallback a `git cherry -v origin/main <branch>` per verificare se le patch sono effettivamente atterrate.
- **Ritorno sicuro alla root primaria:** Usa `$(git -C "$(git rev-parse --git-common-dir)/.." rev-parse --show-toplevel)` per uscire da un worktree secondario prima di tentare checkout, merge o eliminazione del worktree stesso.

### 🧹 E. Bonifica totale del runtime (non solo file Git)
Una sessione con un agente non lascia solo commit Git sporchi:
- **Background Tasks & Watcher Kill:** `chumbia` interroga `manage_task` o i cron di background (es. watcher di polling PR) e ne impone lo spegnimento per evitare leak di risorse.
- **Pulizia disk-cache e `node_modules` effimeri:** Riconosce `just clean` e spazza via surgicalmente directory `node_modules/` rimaste nei soli worktree temporanei, proteggendo il server foreground dell'utente.
- **Breadcrumb Lockfile (`.chumbia.touch`):** Crea un lockfile con timestamp e PID durante l'audit e lo rimuove solo a completamento; in questo modo il companion job settimanale `git-disk-cleanup` individua run abortiti a metà.

### 🧠 F. Distillazione obbligatoria della memoria (`/learn` Piggyback)
Nessuna skill di finalizzazione in Superpowers o altrove si occupa del problema più grande dei modelli linguistici: **l'amnesia post-chiusura chat**.
- `chumbia` vieta il sign-off finale se prima non viene eseguita la **Fase 3 ("Cosa abbiamo imparato oggi?")**.
- Estrae correzioni utente, preferenze e gotcha tecnici, persistendoli subito o fornendo il comando `/learn <frase>` pronto da copiare/incollare prima che la conversazione venga distrutta.

### 🎺 G. Il Contratto Semantico Vocale
In Superpowers l'agente può dire *"All done"* in qualsiasi momento.  
In `chumbia` esiste una regola invalicabile: **se fallisce anche un solo gate di verifica, l'agente ha il divieto assoluto di pronunciare la parola "Chumbia"**. Vedere `💃🕺🎺 CHUMBIA!` nella risposta è la prova crittografica/comportamentale per l'utente che il codice è su `origin/main`, il disco è pulito e la chat può essere chiusa in totale tranquillità.
