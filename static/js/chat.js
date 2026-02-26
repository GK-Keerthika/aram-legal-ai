// ARAM — அறம் | Chat Interface v3.0

const chatWindow = document.getElementById('chatWindow');
const userInput  = document.getElementById('userInput');
const sendBtn    = document.getElementById('sendBtn');
const charCount  = document.getElementById('charCount');

// ── Page Navigation ───────────────────────────────────
function showPage(page) {
  // Hide all pages
  document.querySelectorAll('.page').forEach(p => {
    p.classList.remove('active');
  });

  // Remove active from nav links
  document.querySelectorAll('.nav-link').forEach(l => {
    l.classList.remove('active');
  });

  // Show selected page
  document.getElementById(page + 'Page').classList.add('active');
  document.getElementById('nav' + page.charAt(0).toUpperCase() + page.slice(1))
    .classList.add('active');
}

// ── Law Card Toggle ───────────────────────────────────
function toggleLaw(lawId) {
  const card = document.getElementById(lawId);
  card.classList.toggle('open');
}
// ── Language Toggle for About & Laws pages ────────────
function setPageLang(page, lang) {
  // Update button states
  document.getElementById(page + 'EngBtn').classList.toggle('active', lang === 'eng');
  document.getElementById(page + 'TamBtn').classList.toggle('active', lang === 'tam');

  // Show/hide content
  const engContent = document.getElementById(page + 'Eng');
  const tamContent = document.getElementById(page + 'Tam');

  if (lang === 'eng') {
    engContent.style.display = 'block';
    tamContent.style.display = 'none';
    engContent.style.animation = 'pageIn 0.3s ease';
  } else {
    engContent.style.display = 'none';
    tamContent.style.display = 'block';
    tamContent.style.animation = 'pageIn 0.3s ease';
  }
}

// ── Auto-resize textarea ──────────────────────────────
userInput.addEventListener('input', function() {
  this.style.height = 'auto';
  this.style.height = Math.min(this.scrollHeight, 120) + 'px';
  charCount.textContent = `${this.value.length} / 500`;
});

// ── Enter key ─────────────────────────────────────────
userInput.addEventListener('keydown', function(e) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
});

// ── Quick send ────────────────────────────────────────
function sendQuick(text) {
  // Switch to chat page if not already there
  showPage('chat');
  setTimeout(() => {
    userInput.value = text;
    sendMessage();
  }, 100);
}

// ── Format bot response ───────────────────────────────
function formatResponse(text) {
  text = text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');

  // Separators
  text = text.replace(
    /────+/g,
    '<hr style="border:none;border-top:1px solid rgba(201,168,76,0.2);margin:10px 0;">'
  );

  // Section headers with color coding
  const headers = [
    [/📋\s+SITUATION UNDERSTOOD/g, '#c9a84c'],
    [/⚖️\s+APPLICABLE LAW/g, '#8b949e'],
    [/💡\s+WHAT THIS MEANS(?: FOR YOU)?/g, '#58a6ff'],
    [/✅\s+YOUR NEXT STEPS/g, '#3fb950'],
    [/📖\s+LEGAL DETAILS/g, '#d2a8ff'],
    [/🏛️\s+WHERE TO (?:FILE COMPLAINT|COMPLAIN)/g, '#ffa657'],
  ];

  headers.forEach(([pattern, color]) => {
    text = text.replace(
      pattern,
      match => `<strong style="color:${color};font-size:12.5px;letter-spacing:0.5px;">${match}</strong>`
    );
  });

  // Severity indicators
  text = text.replace(
    /🔴\s+(?:HIGH SEVERITY|SEVERITY:\s*HIGH)/g,
    '<span style="color:#f85149;font-weight:600;background:rgba(248,81,73,0.1);padding:2px 8px;border-radius:12px;">🔴 HIGH</span>'
  );
  text = text.replace(
    /🟠\s+(?:MEDIUM SEVERITY|SEVERITY:\s*MEDIUM)/g,
    '<span style="color:#e3b341;font-weight:600;background:rgba(227,179,65,0.1);padding:2px 8px;border-radius:12px;">🟠 MEDIUM</span>'
  );
  text = text.replace(
    /🟡\s+(?:LOW SEVERITY|SEVERITY:\s*LOW)/g,
    '<span style="color:#3fb950;font-weight:600;background:rgba(63,185,80,0.1);padding:2px 8px;border-radius:12px;">🟡 LOW</span>'
  );

  // Disclaimer styling
  text = text.replace(
    /⚖️\s+Disclaimer:.*$/gm,
    match => `<span style="color:#4a5568;font-size:11.5px;font-style:italic;">${match}</span>`
  );

  return text;
}

// ── Append message ────────────────────────────────────
function appendMessage(text, sender) {
  const wrap = document.createElement('div');
  wrap.className = `msg-wrap ${sender}`;

  const time = new Date().toLocaleTimeString('en-IN', {
    hour: '2-digit', minute: '2-digit'
  });

  const avatarContent = sender === 'bot' ? 'அ' : '👤';

  let content;
  if (sender === 'bot') {
    content = `<pre style="white-space:pre-wrap;font-family:inherit;margin:0;">${formatResponse(text)}</pre>`;
  } else {
    content = `<p style="margin:0;">${text.replace(/</g,'&lt;').replace(/>/g,'&gt;')}</p>`;
  }

  wrap.innerHTML = `
    <div class="msg-row">
      <div class="msg-avatar ${sender}">${avatarContent}</div>
      <div class="msg-bubble">${content}</div>
    </div>
    <div class="msg-meta">${sender === 'bot' ? 'அறம் (ARAM)' : 'You'} · ${time}</div>
  `;

  chatWindow.appendChild(wrap);
  scrollToBottom();
}

// ── Typing indicator ──────────────────────────────────
function showTyping() {
  const el = document.createElement('div');
  el.className = 'typing-wrap';
  el.id = 'typingEl';
  el.innerHTML = `
    <div class="msg-avatar bot">அ</div>
    <div class="typing-bubble">
      <div class="typing-dot"></div>
      <div class="typing-dot"></div>
      <div class="typing-dot"></div>
    </div>
  `;
  chatWindow.appendChild(el);
  scrollToBottom();
}

function removeTyping() {
  const el = document.getElementById('typingEl');
  if (el) el.remove();
}

function scrollToBottom() {
  chatWindow.scrollTop = chatWindow.scrollHeight;
}

// ── Main send ─────────────────────────────────────────
async function sendMessage() {
  const message = userInput.value.trim();
  if (!message) return;

  userInput.value = '';
  userInput.style.height = 'auto';
  charCount.textContent = '0 / 500';
  sendBtn.disabled = true;

  appendMessage(message, 'user');
  showTyping();

  try {
    const res = await fetch('/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message })
    });
    const data = await res.json();
    removeTyping();
    appendMessage(data.response, 'bot');
  } catch (err) {
    removeTyping();
    appendMessage('Sorry, something went wrong. Please try again.', 'bot');
  } finally {
    sendBtn.disabled = false;
    userInput.focus();
  }
}

// ── Init ──────────────────────────────────────────────
window.addEventListener('load', () => {
  userInput.focus();
  // Open first law card by default
  const law1 = document.getElementById('law1');
  if (law1) law1.classList.add('open');
});
// ── Logo Meaning Overlay ──────────────────────────────
function openLogoOverlay() {
  const overlay = document.getElementById('logoOverlay');
  overlay.classList.add('open');
  document.body.style.overflow = 'hidden';
}

function closeLogoOverlay(e) {
  // If called from backdrop click, only close if clicking outside box
  if (e && e.target !== document.getElementById('logoOverlay')) return;
  const overlay = document.getElementById('logoOverlay');
  overlay.classList.remove('open');
  document.body.style.overflow = '';
}

// Close on Escape key
document.addEventListener('keydown', function(e) {
  if (e.key === 'Escape') closeLogoOverlay();
});