/**
 * Antigravity Inline PDF Viewer Sidecar
 * Automatically intercepts .pdf files opened in Antigravity's Aux Pane (via file_extensions: [".pdf"]).
 */
import { execFileSync, spawn } from 'node:child_process';
import { existsSync, readFileSync, statSync } from 'node:fs';
import { homedir, userInfo } from 'node:os';
import { basename, dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { SidecarApp, Response } from 'sidecar_sdk';

const app = new SidecarApp();
const CURRENT_DIR = dirname(fileURLToPath(import.meta.url));

function findXdgOpenAs() {
  const candidates = [
    process.env.XDG_OPEN_AS_BIN,
    process.env.GIC ? join(process.env.GIC, 'bin', 'xdg-open-as') : '',
    join(homedir(), 'git', 'gic', 'bin', 'xdg-open-as'),
    join(homedir(), 'bin', 'xdg-open-as'),
    join(homedir(), '.local', 'bin', 'xdg-open-as'),
    join(CURRENT_DIR, 'xdg-open-as'),
  ].filter(Boolean);
  for (const c of candidates) {
    if (existsSync(c)) return c;
  }
  return 'xdg-open-as';
}

function detectChromeIdentities() {
  const home = homedir();
  const statePaths = [
    join(home, '.config', 'google-chrome', 'Local State'),
    join(home, '.config', 'chromium', 'Local State'),
    join(home, 'Library', 'Application Support', 'Google', 'Chrome', 'Local State'),
  ];
  const username = (userInfo().username || '').toLowerCase();
  const profiles = [];

  for (const p of statePaths) {
    if (!existsSync(p)) continue;
    try {
      const state = JSON.parse(readFileSync(p, 'utf-8'));
      const cache = state?.profile?.info_cache || {};
      for (const [dir, info] of Object.entries(cache)) {
        const email = info?.user_name || info?.email || '';
        if (!email) continue;
        const hostedDomain =
          info?.hosted_domain && info.hosted_domain !== 'NO_HOSTED_DOMAIN'
            ? info.hosted_domain
            : '';
        profiles.push({
          dir,
          email,
          name: info?.name || dir,
          hostedDomain,
          isPrimaryWork: Boolean(hostedDomain && email.toLowerCase().startsWith(username + '@')),
          isDefault: dir === 'Default',
        });
      }
      break;
    } catch {
      // ignore parse errors
    }
  }

  profiles.sort((a, b) => {
    if (a.isPrimaryWork !== b.isPrimaryWork) return a.isPrimaryWork ? -1 : 1;
    if (a.isDefault !== b.isDefault) return a.isDefault ? -1 : 1;
    return a.email.localeCompare(b.email);
  });

  const defaultIdentity =
    process.env.PDF_VIEWER_PRINT_IDENTITY ||
    profiles[0]?.email ||
    '';

  return { defaultIdentity, profiles };
}

function normalizeFilePath(rawPath) {
  if (!rawPath || typeof rawPath !== 'string') return null;
  let p = rawPath.trim();
  if (p.startsWith('file://')) {
    try {
      p = fileURLToPath(p);
    } catch {
      p = decodeURIComponent(p.replace(/^file:\/\//, ''));
    }
  }
  p = resolve(p);
  if (!existsSync(p)) return null;
  return p;
}

function findPopplerBin(binName) {
  const candidates = [
    `/opt/homebrew/bin/${binName}`,
    `/usr/local/bin/${binName}`,
    `/usr/bin/${binName}`,
  ];
  for (const c of candidates) {
    if (existsSync(c)) return c;
  }
  return binName;
}

const PDFINFO_BIN = findPopplerBin('pdfinfo');
const PDFTOTEXT_BIN = findPopplerBin('pdftotext');
const PDFTOPPM_BIN = findPopplerBin('pdftoppm');

function getPdfInfo(filePath) {
  const stat = statSync(filePath);
  let pages = 1;
  let title = '';
  let pageSize = '';
  try {
    const out = execFileSync(PDFINFO_BIN, [filePath], {
      encoding: 'utf-8',
      timeout: 5000,
    });
    for (const line of out.split('\n')) {
      const m = /^([^:]+):\s*(.*)$/.exec(line);
      if (!m) continue;
      const key = m[1].trim().toLowerCase();
      const val = m[2].trim();
      if (key === 'pages') pages = Math.max(1, parseInt(val, 10) || 1);
      if (key === 'title') title = val;
      if (key === 'page size') pageSize = val;
    }
  } catch (err) {
    console.warn('[pdf-viewer] pdfinfo fallback:', err.message);
  }
  let text = '';
  try {
    text = execFileSync(PDFTOTEXT_BIN, [filePath, '-'], {
      encoding: 'utf-8',
      timeout: 8000,
      maxBuffer: 10 * 1024 * 1024,
    }).trim();
  } catch (err) {
    console.warn('[pdf-viewer] pdftotext fallback:', err.message);
  }
  const { defaultIdentity, profiles } = detectChromeIdentities();
  return {
    file: filePath,
    filename: basename(filePath),
    sizeBytes: stat.size,
    pages,
    title,
    pageSize,
    text,
    defaultIdentity,
    profiles,
  };
}

function renderPagePng(filePath, pageNum, dpi = 160) {
  const safePage = Math.max(1, Math.min(500, parseInt(String(pageNum), 10) || 1));
  const safeDpi = Math.max(72, Math.min(300, parseInt(String(dpi), 10) || 160));
  return execFileSync(
    PDFTOPPM_BIN,
    ['-png', '-r', String(safeDpi), '-f', String(safePage), '-l', String(safePage), '-singlefile', filePath],
    { timeout: 15000, maxBuffer: 50 * 1024 * 1024 }
  );
}

const VIEW_HTML = `<!DOCTYPE html>
<html lang="it">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>PDF Viewer 📄</title>
<style>
  :root {
    --bg: var(--background, #141416);
    --fg: var(--foreground, #ececf1);
    --card: var(--card, #1e1f23);
    --border: var(--border, #2e3038);
    --muted: var(--muted-foreground, #9ca3af);
    --accent: var(--primary, #60a5fa);
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    background: var(--bg);
    color: var(--fg);
    font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    height: 100vh;
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }
  header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 8px;
    padding: 8px 12px;
    background: var(--card);
    border-bottom: 1px solid var(--border);
    flex-shrink: 0;
    flex-wrap: wrap;
    z-index: 20;
  }
  .file-meta {
    display: flex;
    align-items: center;
    gap: 8px;
    min-width: 0;
    flex: 1;
  }
  .file-title {
    font-size: 13px;
    font-weight: 600;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  .badge {
    font-size: 11px;
    color: var(--muted);
    background: rgba(128,128,128,0.15);
    padding: 2px 7px;
    border-radius: 999px;
    white-space: nowrap;
  }
  .toolbar {
    display: flex;
    align-items: center;
    gap: 4px;
    flex-wrap: wrap;
  }
  .page-nav-pill {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    background: rgba(128,128,128,0.12);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 2px 4px;
    margin-right: 4px;
  }
  .page-nav-pill button {
    border: none;
    background: transparent;
    padding: 3px 7px;
    font-weight: 700;
  }
  .page-nav-pill button:hover:not(:disabled) {
    background: rgba(128,128,128,0.28);
  }
  .page-nav-pill button:disabled {
    opacity: 0.35;
    cursor: default;
  }
  #page-counter {
    font-size: 12px;
    font-weight: 600;
    min-width: 64px;
    text-align: center;
    font-variant-numeric: tabular-nums;
  }
  button {
    background: rgba(128,128,128,0.14);
    color: var(--fg);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 4px 8px;
    font-size: 12px;
    cursor: pointer;
    transition: all 0.12s ease;
    display: inline-flex;
    align-items: center;
    gap: 4px;
    white-space: nowrap;
  }
  button:hover:not(:disabled) {
    background: rgba(128,128,128,0.26);
    border-color: var(--accent);
  }
  button.primary-print {
    background: rgba(59, 130, 246, 0.18);
    border-color: rgba(96, 165, 250, 0.45);
  }
  button.primary-print:hover {
    background: rgba(59, 130, 246, 0.32);
    border-color: var(--accent);
  }
  button.active {
    background: var(--accent);
    color: #000;
    border-color: var(--accent);
    font-weight: 600;
  }
  #zoom-label {
    font-size: 11px;
    min-width: 44px;
    text-align: center;
    color: var(--muted);
    font-variant-numeric: tabular-nums;
  }
  .viewport-wrapper {
    position: relative;
    flex: 1;
    display: flex;
    overflow: hidden;
  }
  main {
    flex: 1;
    overflow: auto;
    padding: 16px 64px;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 20px;
    scroll-behavior: smooth;
  }
  /* Mega bottoncioni laterali Avanti / Indietro */
  .mega-nav-btn {
    position: absolute;
    top: 50%;
    transform: translateY(-50%);
    width: 46px;
    height: 92px;
    border-radius: 14px;
    background: rgba(25, 26, 32, 0.78);
    backdrop-filter: blur(8px);
    color: #fff;
    border: 1px solid rgba(255,255,255,0.18);
    font-size: 22px;
    font-weight: 700;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 2px;
    cursor: pointer;
    z-index: 15;
    box-shadow: 0 6px 20px rgba(0,0,0,0.45);
    transition: all 0.15s ease;
    user-select: none;
  }
  .mega-nav-btn span.sub {
    font-size: 9px;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    opacity: 0.75;
  }
  .mega-nav-btn:hover:not(:disabled) {
    background: var(--accent);
    color: #000;
    border-color: var(--accent);
    transform: translateY(-50%) scale(1.06);
  }
  .mega-nav-btn:disabled {
    opacity: 0.22;
    cursor: default;
  }
  .mega-prev { left: 10px; }
  .mega-next { right: 10px; }

  .page-card {
    background: #fff;
    border-radius: 6px;
    box-shadow: 0 8px 24px rgba(0,0,0,0.35);
    overflow: hidden;
    position: relative;
    transition: width 0.12s ease;
    max-width: 100%;
    flex-shrink: 0;
  }
  .page-card img {
    display: block;
    width: 100%;
    height: auto;
  }
  .page-number {
    position: absolute;
    bottom: 8px;
    right: 10px;
    background: rgba(0,0,0,0.68);
    color: #fff;
    font-size: 11px;
    padding: 2px 8px;
    border-radius: 999px;
    pointer-events: none;
  }
  #text-view {
    display: none;
    width: 100%;
    max-width: 820px;
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 16px;
    white-space: pre-wrap;
    font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
    font-size: 12.5px;
    line-height: 1.55;
    user-select: text;
  }
  .status-box {
    margin: auto;
    text-align: center;
    color: var(--muted);
    font-size: 13px;
    max-width: 420px;
    line-height: 1.5;
  }
  footer {
    flex-shrink: 0;
    padding: 5px 12px;
    background: var(--card);
    border-top: 1px solid var(--border);
    text-align: center;
    font-size: 11.5px;
    font-style: italic;
    color: var(--muted);
    z-index: 20;
  }
  footer a {
    color: var(--accent);
    text-decoration: none;
    font-weight: 500;
  }
  footer a:hover {
    text-decoration: underline;
  }
</style>
</head>
<body>
  <header>
    <div class="file-meta">
      <span>📄</span>
      <span class="file-title" id="filename">Caricamento PDF...</span>
      <span class="badge" id="page-badge">–</span>
    </div>
    <div class="toolbar">
      <div class="page-nav-pill" title="Usa anche le frecce ⬅️ / ➡️ della tastiera">
        <button id="top-prev" onclick="stepPage(-1)" title="Pagina precedente (⬅️)">◀</button>
        <span id="page-counter">1 / 1</span>
        <button id="top-next" onclick="stepPage(1)" title="Pagina successiva (➡️)">▶</button>
      </div>
      <button id="btn-single-mode" onclick="toggleSinglePageMode()" title="Alterna Pagina Singola vs Scroll Continuo">📖 Singola</button>
      <button onclick="changeZoom(-15)" title="Zoom Out">➖</button>
      <span id="zoom-label">100%</span>
      <button onclick="changeZoom(15)" title="Zoom In">➕</button>
      <button onclick="resetZoom()" title="Adatta larghezza">↔️ Fit</button>
      <button id="btn-text" onclick="toggleTextView()" title="Mostra/copia testo estratto">📝 Testo</button>
      <button onclick="openInChromeForPrint()" id="btn-print" class="primary-print" title="Apri in Chrome con il profilo abilitato alla stampa">🖨️ Apri in Chrome per Stampa</button>
      <button onclick="sendToChat()" id="btn-chat" title="Invia testo del PDF in chat">💬 In Chat</button>
    </div>
  </header>

  <div class="viewport-wrapper">
    <button id="mega-prev" class="mega-nav-btn mega-prev" onclick="stepPage(-1)" title="Pagina Precedente (Freccia Sinistra ⬅️)">
      <span>◀</span>
      <span class="sub">Prev</span>
    </button>

    <main id="viewport">
      <div class="status-box" id="status">Caricamento anteprima PDF...</div>
      <div id="pages-container" style="display:flex;flex-direction:column;align-items:center;gap:20px;width:100%;"></div>
      <pre id="text-view"></pre>
    </main>

    <button id="mega-next" class="mega-nav-btn mega-next" onclick="stepPage(1)" title="Pagina Successiva (Freccia Destra ➡️)">
      <span>▶</span>
      <span class="sub">Next</span>
    </button>
  </div>

  <footer>
    Made by 💛 <a href="https://www.linkedin.com/in/riccardocarlesso/" target="_blank" rel="noopener noreferrer">Riccardo</a> with <a href="https://antigravity.google/" target="_blank" rel="noopener noreferrer">Antigravity</a>
  </footer>

<script>
  const params = new URLSearchParams(window.location.search);
  let currentFile = params.get('file') || '';
  let zoomPct = 100;
  let pdfMeta = null;
  let showingText = false;
  let singlePageMode = false;
  let currentPage = 1;
  let totalPages = 1;
  let programmaticScroll = false;

  function formatBytes(b) {
    if (!b) return '';
    if (b < 1024) return b + ' B';
    if (b < 1024 * 1024) return (b / 1024).toFixed(1) + ' KB';
    return (b / (1024 * 1024)).toFixed(2) + ' MB';
  }

  function updateNavButtons() {
    document.getElementById('page-counter').textContent = currentPage + ' / ' + totalPages;
    const atStart = currentPage <= 1;
    const atEnd = currentPage >= totalPages;
    document.getElementById('top-prev').disabled = atStart;
    document.getElementById('top-next').disabled = atEnd;
    document.getElementById('mega-prev').disabled = atStart;
    document.getElementById('mega-next').disabled = atEnd;

    const cards = document.querySelectorAll('.page-card');
    cards.forEach((card, idx) => {
      const p = idx + 1;
      if (singlePageMode) {
        card.style.display = p === currentPage ? 'block' : 'none';
      } else {
        card.style.display = 'block';
      }
    });
  }

  function goToPage(targetPage) {
    if (totalPages < 1) return;
    currentPage = Math.max(1, Math.min(totalPages, targetPage));
    updateNavButtons();
    if (singlePageMode) {
      document.getElementById('viewport').scrollTop = 0;
    } else {
      const card = document.getElementById('page-card-' + currentPage);
      if (card) {
        programmaticScroll = true;
        card.scrollIntoView({ behavior: 'smooth', block: 'start' });
        setTimeout(() => { programmaticScroll = false; }, 450);
      }
    }
  }

  function stepPage(delta) {
    if (showingText) toggleTextView();
    goToPage(currentPage + delta);
  }

  function toggleSinglePageMode() {
    singlePageMode = !singlePageMode;
    document.getElementById('btn-single-mode').classList.toggle('active', singlePageMode);
    updateNavButtons();
    if (!singlePageMode) {
      const card = document.getElementById('page-card-' + currentPage);
      if (card) card.scrollIntoView({ behavior: 'instant', block: 'start' });
    }
  }

  function applyZoom() {
    document.getElementById('zoom-label').textContent = zoomPct + '%';
    const cards = document.querySelectorAll('.page-card');
    cards.forEach(card => {
      card.style.width = zoomPct + '%';
      card.style.maxWidth = zoomPct > 100 ? 'none' : '900px';
    });
  }

  function changeZoom(delta) {
    zoomPct = Math.max(40, Math.min(250, zoomPct + delta));
    applyZoom();
  }

  function resetZoom() {
    zoomPct = 100;
    applyZoom();
  }

  function toggleTextView() {
    showingText = !showingText;
    document.getElementById('btn-text').classList.toggle('active', showingText);
    document.getElementById('pages-container').style.display = showingText ? 'none' : 'flex';
    document.getElementById('text-view').style.display = showingText ? 'block' : 'none';
  }

  async function openInChromeForPrint() {
    if (!currentFile) return;
    const btn = document.getElementById('btn-print');
    const orig = btn.textContent;
    try {
      btn.textContent = '⏳ Apertura Chrome...';
      const q = new URLSearchParams(window.location.search);
      q.set('file', currentFile);
      const res = await fetch('/api/open-chrome-print?' + q.toString());
      const data = await res.json();
      if (data.ok) {
        btn.textContent = '✅ Aperto (' + (data.identity || 'Chrome') + ')!';
      } else {
        btn.textContent = '⚠️ ' + (data.error || 'Errore');
      }
    } catch (e) {
      console.error(e);
      btn.textContent = '⚠️ Errore';
    }
    setTimeout(() => { btn.textContent = orig; }, 2200);
  }

  async function sendToChat() {
    if (!pdfMeta) return;
    const btn = document.getElementById('btn-chat');
    const orig = btn.textContent;
    try {
      btn.textContent = '⏳...';
      const snippet = (pdfMeta.text || '').slice(0, 2000);
      const msg = \`📄 **\${pdfMeta.filename}** (\${pdfMeta.pages} pag.):\\n\\n\\\`\\\`\\\`\\n\${snippet || 'PDF caricato'}\\n\\\`\\\`\\\`\`;
      if (window.antigravity && window.antigravity.sendMessage) {
        const convId = params.get('conversationId') || window.antigravity.config?.conversationId;
        if (convId) {
          await window.antigravity.sendMessage(convId, msg);
          btn.textContent = '✅ Inviato!';
          setTimeout(() => { btn.textContent = orig; }, 2000);
          return;
        }
      }
      await navigator.clipboard.writeText(pdfMeta.text || pdfMeta.file);
      btn.textContent = '📋 Copiato!';
    } catch (e) {
      console.error(e);
      btn.textContent = '⚠️ Errore';
    }
    setTimeout(() => { btn.textContent = orig; }, 2000);
  }

  // Track visible page on manual scroll
  document.getElementById('viewport').addEventListener('scroll', () => {
    if (singlePageMode || showingText || programmaticScroll) return;
    const viewport = document.getElementById('viewport');
    const center = viewport.getBoundingClientRect().top + viewport.clientHeight * 0.35;
    const cards = document.querySelectorAll('.page-card');
    let bestPage = currentPage;
    for (let i = 0; i < cards.length; i++) {
      const r = cards[i].getBoundingClientRect();
      if (r.top <= center && r.bottom >= center) {
        bestPage = i + 1;
        break;
      }
    }
    if (bestPage !== currentPage) {
      currentPage = bestPage;
      updateNavButtons();
    }
  });

  // Keyboard navigation (Left/Right arrows, PageUp/PageDown)
  window.addEventListener('keydown', (e) => {
    if (e.target && (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA')) return;
    if (e.key === 'ArrowLeft' || e.key === 'PageUp') {
      e.preventDefault();
      stepPage(-1);
    } else if (e.key === 'ArrowRight' || e.key === 'PageDown') {
      e.preventDefault();
      stepPage(1);
    }
  });

  async function loadPdf(filePath) {
    const statusEl = document.getElementById('status');
    const pagesContainer = document.getElementById('pages-container');
    const textView = document.getElementById('text-view');

    if (!filePath) {
      statusEl.innerHTML = '📄 <b>PDF Viewer attivo!</b><br><br>Clicca su qualsiasi file <code>.pdf</code> in Antigravity per visualizzarlo qui.';
      document.getElementById('filename').textContent = 'PDF Viewer 📄';
      return;
    }

    try {
      statusEl.style.display = 'block';
      statusEl.textContent = 'Rendering PDF ad alta definizione...';
      pagesContainer.innerHTML = '';

      const q = new URLSearchParams(window.location.search);
      q.set('file', filePath);

      const res = await fetch('/api/info?' + q.toString());
      const data = await res.json();
      if (data.error) {
        statusEl.textContent = '⚠️ ' + data.error;
        return;
      }

      pdfMeta = data;
      currentPage = 1;
      totalPages = Math.max(1, data.pages || 1);

      document.getElementById('filename').textContent = data.filename;
      document.getElementById('filename').title = data.file;
      document.getElementById('page-badge').textContent =
        totalPages + (totalPages === 1 ? ' pagina' : ' pagine') + ' • ' + formatBytes(data.sizeBytes);
      if (data.defaultIdentity) {
        document.getElementById('btn-print').title =
          'xdg-open-as ' + data.defaultIdentity + ' "' + data.file + '"';
      }
      textView.textContent = data.text || '(Nessun testo selezionabile trovato nel PDF)';

      statusEl.style.display = 'none';

      for (let p = 1; p <= totalPages; p++) {
        const card = document.createElement('div');
        card.className = 'page-card';
        card.id = 'page-card-' + p;
        card.style.width = zoomPct + '%';
        card.style.maxWidth = '900px';

        const img = document.createElement('img');
        const imgQ = new URLSearchParams(window.location.search);
        imgQ.set('file', filePath);
        imgQ.set('page', String(p));
        imgQ.set('dpi', '160');
        img.loading = p <= 2 ? 'eager' : 'lazy';
        img.alt = 'Pagina ' + p;
        img.src = '/api/page?' + imgQ.toString();

        const badge = document.createElement('div');
        badge.className = 'page-number';
        badge.textContent = 'Pag. ' + p + ' / ' + totalPages;

        card.appendChild(img);
        card.appendChild(badge);
        pagesContainer.appendChild(card);
      }

      updateNavButtons();
    } catch (err) {
      statusEl.style.display = 'block';
      statusEl.textContent = '⚠️ Errore caricamento PDF: ' + err.message;
    }
  }

  loadPdf(currentFile);
</script>
</body>
</html>`;

app.page('/', () => VIEW_HTML);
app.page('/view.html', () => VIEW_HTML);

app.api('/api/info', (data) => {
  const raw = data.file || data.path;
  const filePath = normalizeFilePath(raw);
  if (!filePath) {
    return { error: `File PDF non trovato: ${raw || '(nessun file specificato)'}` };
  }
  return getPdfInfo(filePath);
}, 'GET');

app.api('/api/open-chrome-print', (data) => {
  const raw = data.file || data.path;
  const filePath = normalizeFilePath(raw);
  if (!filePath) {
    return { ok: false, error: `File PDF non trovato: ${raw || ''}` };
  }
  const { defaultIdentity, profiles } = detectChromeIdentities();
  const identity = data.identity || defaultIdentity;
  const xdgOpenAs = findXdgOpenAs();

  try {
    if (identity && existsSync(xdgOpenAs)) {
      execFileSync(xdgOpenAs, [identity, filePath], {
        timeout: 5000,
        env: { ...process.env, DISPLAY: process.env.DISPLAY || ':0' },
      });
      return { ok: true, identity, file: filePath };
    }
    const matched =
      profiles.find((p) => p.email.toLowerCase() === String(identity).toLowerCase()) ||
      profiles[0];
    const chromeArgs = matched?.dir
      ? [`--profile-directory=${matched.dir}`, filePath]
      : [filePath];
    const cmd = process.platform === 'darwin' ? 'open' : 'google-chrome';
    const spawnArgs =
      process.platform === 'darwin'
        ? ['-na', 'Google Chrome', '--args', ...chromeArgs]
        : chromeArgs;
    const child = spawn(cmd, spawnArgs, {
      detached: true,
      stdio: 'ignore',
      env: { ...process.env, DISPLAY: process.env.DISPLAY || ':0' },
    });
    child.unref();
    return { ok: true, identity: identity || matched?.email || 'google-chrome', file: filePath };
  } catch (err) {
    return { ok: false, error: err.message };
  }
}, 'GET');

app.api('/api/page', (data) => {
  const filePath = normalizeFilePath(data.file || data.path);
  if (!filePath) {
    return new Response('File not found', { status: 404, contentType: 'text/plain' });
  }
  const pngBuffer = renderPagePng(filePath, data.page || 1, data.dpi || 160);
  return new Response(pngBuffer, {
    status: 200,
    contentType: 'image/png',
    headers: { 'Cache-Control': 'private, max-age=60' },
  });
}, 'GET');

app.api('/raw.pdf', (data) => {
  const filePath = normalizeFilePath(data.file || data.path);
  if (!filePath) {
    return new Response('File not found', { status: 404, contentType: 'text/plain' });
  }
  const pdfBuffer = readFileSync(filePath);
  return new Response(pdfBuffer, {
    status: 200,
    contentType: 'application/pdf',
    headers: {
      'Content-Disposition': `inline; filename="${basename(filePath)}"`,
    },
  });
}, 'GET');

app.run();
