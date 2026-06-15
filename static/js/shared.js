/* ============================================================
   CoByte — JavaScript Compartilhado
   ============================================================ */

// ── Helpers ────────────────────────────────────────────────
function statusBadge(status) {
  const map = {
    'Em andamento': 'badge-em-andamento',
    'Concluído':    'badge-concluido',
    'Pausado':      'badge-pausado',
    'Cancelado':    'badge-cancelado',
  };
  return `<span class="badge ${map[status] || 'badge-gray'}">${status}</span>`;
}

function priorityBadge(p) {
  const map = { 'Alta': 'badge-red', 'Média': 'badge-yellow', 'Baixa': 'badge-gray' };
  return `<span class="badge ${map[p] || 'badge-gray'}">${p}</span>`;
}

function memberStatusBadge(s) {
  return s === 'Disponível'
    ? `<span class="badge badge-green">${s}</span>`
    : `<span class="badge badge-blue">${s}</span>`;
}

function progressFillClass(pct) {
  if (pct >= 80) return 'green';
  if (pct >= 50) return 'blue';
  if (pct >= 25) return 'purple';
  return '';
}

function formatDate(str) {
  if (!str) return '—';
  const d = new Date(str + 'T00:00:00');
  return d.toLocaleDateString('pt-BR', { day:'2-digit', month:'short', year:'numeric' });
}

function formatCurrency(n) {
  return new Intl.NumberFormat('pt-BR', { style:'currency', currency:'BRL' }).format(n);
}

// ── Modal Helpers ──────────────────────────────────────────
function openModal(id) {
  const el = document.getElementById(id);
  if (el) el.classList.add('open');
}
function closeModal(id) {
  const el = document.getElementById(id);
  if (el) el.classList.remove('open');
}

// ── Toast ──────────────────────────────────────────────────
function toast(msg, type = 'success') {
  const el = document.createElement('div');
  el.style.cssText = `
    position:fixed; bottom:24px; right:24px; z-index:9999;
    background:${type==='error'?'#e94560':'#22c55e'}; color:#fff;
    padding:12px 20px; border-radius:10px; font-size:13.5px; font-weight:600;
    box-shadow:0 6px 20px rgba(0,0,0,0.18); animation:fadeUp 0.3s ease;
    display:flex; align-items:center; gap:8px;
  `;
  el.textContent = msg;
  document.body.appendChild(el);
  setTimeout(() => el.remove(), 3000);
}

// ── SVG Icons ──────────────────────────────────────────────
const svg = (d, extra='') => `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" ${extra}>${d}</svg>`;

function iconHome()      { return svg('<path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/>'); }
function iconFolder()    { return svg('<path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>'); }
function iconUsers()     { return svg('<path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>'); }
function iconSettings()  { return svg('<circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/>'); }
function iconLogout()    { return svg('<path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/>', 'width="16" height="16"'); }
function iconBell()      { return svg('<path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/>'); }
function iconPlus()      { return svg('<line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>'); }
function iconSearch()    { return svg('<circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>'); }
function iconX()         { return svg('<line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>'); }
function iconEdit()      { return svg('<path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>'); }
function iconTrash()     { return svg('<polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/><path d="M10 11v6"/><path d="M14 11v6"/><path d="M9 6V4a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2"/>'); }
function iconCheck()     { return svg('<polyline points="20 6 9 17 4 12"/>'); }
function iconArrow()     { return svg('<line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/>'); }
function iconChart()     { return svg('<line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/>'); }
function iconClock()     { return svg('<circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>'); }
function iconMail()      { return svg('<path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/>'); }
function iconBriefcase() { return svg('<rect x="2" y="7" width="20" height="14" rx="2" ry="2"/><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/>'); }
function iconStar()      { return svg('<polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>'); }
function iconFilter()    { return svg('<polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"/>'); }
function iconUser()      { return svg('<path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>'); }
function iconEye()       { return svg('<path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/>'); }
function iconLock()      { return svg('<rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/>'); }
function iconSave()      { return svg('<path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/><polyline points="17 21 17 13 7 13 7 21"/><polyline points="7 3 7 8 15 8"/>'); }
// ── Theme Management ───────────────────────────────────────
function setAppTheme(theme) {
  if (theme === 'light') {
    document.body.classList.add('light-mode');
    localStorage.setItem('cobyte-theme', 'light');
  } else {
    document.body.classList.remove('light-mode');
    localStorage.setItem('cobyte-theme', 'dark');
  }
}

function loadAppTheme() {
  const saved = localStorage.getItem('cobyte-theme');
  if (saved === 'light') {
    document.body.classList.add('light-mode');
  } else if (!saved) {
    localStorage.setItem('cobyte-theme', 'dark');
  }
}

// Inicializa no carregamento
document.addEventListener('DOMContentLoaded', () => {
  loadAppTheme();
  initSidebarToggle();
  setTimeout(() => {
    document.documentElement.classList.remove('sidebar-preload-collapsed');
  }, 50);
});

// ── Sidebar Collapse Toggle ────────────────────────────────
function initSidebarToggle() {
  const sidebar = document.querySelector('.sidebar, .func-sidebar');
  if (!sidebar) return;

  // Create toggle button
  const toggleBtn = document.createElement('button');
  toggleBtn.className = 'sidebar-toggle';
  toggleBtn.setAttribute('title', 'Minimizar menu');
  toggleBtn.setAttribute('aria-label', 'Minimizar menu lateral');
  toggleBtn.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="15 18 9 12 15 6"/></svg>`;
  sidebar.appendChild(toggleBtn);

  // Add data-tooltip to nav items for collapsed tooltips
  sidebar.querySelectorAll('.nav-item').forEach(item => {
    const label = item.querySelector('span');
    if (label) {
      item.setAttribute('data-tooltip', label.textContent.trim());
    }
  });

  // Restore saved state
  const isCollapsed = localStorage.getItem('cobyte-sidebar-collapsed') === 'true';
  if (isCollapsed) {
    sidebar.classList.add('sidebar-collapsed');
    toggleBtn.setAttribute('title', 'Expandir menu');
  }

  // Toggle handler
  toggleBtn.addEventListener('click', () => {
    const willCollapse = !sidebar.classList.contains('sidebar-collapsed');
    sidebar.classList.toggle('sidebar-collapsed');
    
    if (willCollapse) {
      localStorage.setItem('cobyte-sidebar-collapsed', 'true');
      toggleBtn.setAttribute('title', 'Expandir menu');
    } else {
      localStorage.setItem('cobyte-sidebar-collapsed', 'false');
      toggleBtn.setAttribute('title', 'Minimizar menu');
    }

    // Also adjust any sibling main content that uses inline styles
    const funcMain = document.querySelector('[style*="margin-left: var(--sidebar-w)"]');
    if (funcMain) {
      funcMain.style.marginLeft = willCollapse ? 'var(--sidebar-collapsed-w)' : 'var(--sidebar-w)';
    }
  });
}
