---
name: spartiti-md
description: "(💛) Formato standard 'Markdown Smart' (ChordPro inline + Emoji semantiche) per spartiti di canzoni con accordi e testo per tastieristi e pianisti."
compatibility: gemini-cli, antigravity, claude
metadata:
  version: "1.0.0"
  author: "Riccardo Carlesso"
  tags: "music, chords, lyrics, piano, markdown, chordpro, spartiti"
---

# 🎹 Spartiti-MD: Il Formato Smart per Accordi e Testo

`spartiti-md` definisce lo standard di riferimento per persistere e convertire testi e accordi di canzoni in **Markdown semantico potenziato**, ottimizzato per chi suona il pianoforte o le tastiere.

> 🚫 **Niente tablature per chitarra** (`e|---B|---G|---`).  
> 🚫 **Niente JSON rumorosi o non leggibili a vista**.  
> 🚫 **Niente righe di accordi sopra il testo con spazi instabili** che si disallineano al primo cambio di font o su mobile/tablet.

---

## 🎯 I 3 Pilastri del Formato

### 1. 🔗 Accordi Inline `[Accordo]` (Stile ChordPro)
L'accordo è inserito tra parentesi quadre **esattamente prima della sillaba** su cui cade il cambio armonico o il tocco pianistico:

```markdown
[DO]Su di noi... ci avresti scom[MIm]messo tu
```
- **Vantaggio #1**: Zero problemi di disallineamento nei font proportionali o su schermi piccoli (tablet per spartiti).
- **Vantaggio #2**: Compatibilità bidirezionale con lo standard universale [ChordPro](https://chordpro.org) e app come OnSong, SongBook, MobileSheets.
- **Vantaggio #3**: Trasposizione immediata (basta una regex per trasporre da DO a RE senza toccare il layout del testo).

### 2. 🏷️ Struttura con Emoji Semantiche
Ogni sezione del brano usa un'intestazione H3 con emoji per una scansione visiva immediata dal leggio:

| Sezione | Header Markdown | Note / Funzione |
| :--- | :--- | :--- |
| **Intro** | `### 🎹 INTRO` | Accordi in battute `\| [DO] \| [MIm] \|` |
| **Strofa / Verse** | `### 🎤 STROFA 1` | Testo con accordi inline |
| **Pre-Ritornello** | `### 🌈 PRE-CHORUS` | Build-up armonico prima del chorus |
| **Ritornello** | `### 💥 RITORNELLO` | Climax del brano, indicare groove/dinamica |
| **Hook / Riff** | `### 🪝 HOOK` | Fraseggio distintivo |
| **Bridge / Special** | `### 🚀 SPECIAL / BRIDGE` | Variazione armonica / stacco |
| **Assolo / Riff tastiera**| `### 🎹 SOLO` | Descrizione armonie o melodie chiave |
| **Finale / Outro** | `### 🔁 OUTRO` | Fade-out o vamp a loop con segnale di stop `🛑` |

### 3. 🎼 Frontmatter & Piano Tips
In cima al file, includere sempre un blocco di metadati YAML/Quote per impostare rapidamente lo strumento:

```markdown
# 🎵 Titolo Canzone — Artista

> **Info brano:**  
> 🎹 **Tonalità Originale:** Do Maggiore (C)  
> ⏱️ **Tempo:** 4/4 (~115 BPM)  
> 💡 **Piano Tips:** Voicing mano sinistra (es. ottave o quinte aperte 1-5), pattern mano destra (arpeggio pop / pad / staccato funky), e modulazioni critiche.
```

---

## 🔄 Regole di Conversione da Web (es. Accordi & Spartiti, Ultimate-Guitar)

Quando converti spartiti da siti web (dove gli accordi sono posizionati su righe separate sopra il testo):

1. **Riconciliazione accordo-sillaba**: analizza la colonna orizzontale in cui compare la lettera dell'accordo nella riga superiore e inseriscilo `[ACCORDO]` esattamente prima della sillaba sottostante.
2. **Notazione accordi**: mantieni la notazione preferita dall'utente (es. italiana `DO, REm, MIb, SOL7` oppure inglese `C, Dm, Eb, G7`), aggiungendo tensioni pianistiche rilevanti se evidenti (`maj7, 9, sus4, dim, m7b5`).
3. **Indicazione dei bassi (Slash Chords)**: per un pianista il basso è fondamentale: preserva sempre i slash chord (es. `[DO/MI]`, `[SOL/SI]`, `[LAm/SOL]`).
4. **Battute per Intro/Outro strumentali**: usa la notazione a battute `| [DO] | [SOL] | [LAm] | [FA] |`.

---

## 📂 Esempio Completo

Vedi l'esempio pronto all'uso in `examples/su-di-noi-pupo.md`.
