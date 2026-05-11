function cfAnalyze() {
  const input = document.getElementById('cf-repo-input');
  const btn = document.getElementById('cf-analyze-btn');
  const error = document.getElementById('cf-error');
  const results = document.getElementById('cf-results');
  const loading = document.getElementById('cf-loading');
  const content = document.getElementById('cf-content');

  error.style.display = 'none';
  let repo = input.value.trim();
  if (!repo) {
    cfShowError('Digite a URL de um repositório GitHub.');
    input.focus();
    return;
  }

  const match = repo.match(/github\.com\/([^/]+\/[^/]+?)(?:\/|$)/);
  if (match) repo = match[1];
  repo = repo.replace(/\/$/, '');
  if (!/^[\w.-]+\/[\w.-]+$/.test(repo)) {
    cfShowError('Formato inválido. Use: owner/repo ou https://github.com/owner/repo');
    return;
  }

  btn.disabled = true;
  btn.textContent = 'Analisando...';
  results.style.display = 'block';
  loading.style.display = 'flex';
  content.style.display = 'none';

  fetch(CODEFLOW_API_URL + '/api/analyze', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ repo }),
  })
    .then(r => r.json())
    .then(data => {
      loading.style.display = 'none';
      content.style.display = 'block';
      if (data.error) {
        cfShowError(data.error);
        results.style.display = 'none';
        return;
      }
      cfRenderResults(data);
    })
    .catch(err => {
      loading.style.display = 'none';
      cfShowError('Erro ao conectar com a API CodeFlow. Certifique-se de que o serviço está rodando em ' + CODEFLOW_API_URL);
      results.style.display = 'none';
    })
    .finally(() => {
      btn.disabled = false;
      btn.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="16" height="16"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg> Analisar';
    });
}

function cfShowError(msg) {
  const el = document.getElementById('cf-error');
  el.textContent = msg;
  el.style.display = 'block';
}

function cfRenderResults(data) {
  const health = data.health || {};
  const stats = data.stats || {};

  document.getElementById('cf-grade').textContent = health.grade || '-';
  const score = health.score || 0;
  document.getElementById('cf-ring-fill').setAttribute('stroke-dasharray', score + ', 100');
  const ringColor = score >= 80 ? '#22c55e' : score >= 50 ? '#f59e0b' : '#ef4444';
  document.getElementById('cf-ring-fill').setAttribute('stroke', ringColor);
  document.getElementById('cf-health-grade').textContent = health.level || '-';
  document.getElementById('cf-health-score').textContent = score + '/100';

  document.getElementById('cf-stat-files').textContent = stats.files ?? '-';
  document.getElementById('cf-stat-functions').textContent = stats.functions ?? '-';
  document.getElementById('cf-stat-loc').textContent = stats.loc ? stats.loc.toLocaleString() : '-';
  const langKeys = Object.keys(stats.languages || {});
  document.getElementById('cf-stat-languages').textContent = langKeys.length || '-';

  cfRenderLanguages(stats.languages || {});
  cfRenderPatterns(data.patterns || []);
  cfRenderSecurity(data.security_issues || []);
  cfRenderCircular(data.circular_dependencies || []);
  cfRenderDead(data.dead_functions || []);
  cfRenderFiles(data.files || []);
}

function cfRenderLanguages(languages) {
  const el = document.getElementById('cf-languages');
  const keys = Object.keys(languages);
  if (!keys.length) { el.innerHTML = '<div class="cf-empty">Nenhum dado disponível</div>'; return; }

  const totalLoc = Object.values(languages).reduce((s, l) => s + (l.loc || 0), 0);
  const langColors = {
    javascript: '#f7df1e', typescript: '#3178c6', python: '#3572a5',
    html: '#e34f26', css: '#563d7c', java: '#b07219', go: '#00add8',
    ruby: '#701516', php: '#4f5d95', rust: '#dea584', c: '#555555',
    'c++': '#f34b7d', 'c#': '#178600', swift: '#ffac45', kotlin: '#f18e33',
    scala: '#c22d40', elixir: '#6e4a7e', haskell: '#5e5086', lua: '#000080',
    r: '#198ce7', dart: '#00b4ab', shell: '#89e051', vue: '#42b883',
    svelte: '#ff3e00',
  };

  let html = '<div class="cf-lang-bar">';
  for (const [lang, info] of Object.entries(languages)) {
    const pct = totalLoc ? ((info.loc || 0) / totalLoc * 100) : 0;
    html += `<div class="cf-lang-segment" style="width:${pct}%;background:${langColors[lang] || '#6366f1'}" title="${lang}: ${pct.toFixed(1)}%"></div>`;
  }
  html += '</div><div class="cf-lang-list">';
  for (const [lang, info] of Object.entries(languages)) {
    const pct = totalLoc ? ((info.loc || 0) / totalLoc * 100) : 0;
    html += `<div class="cf-lang-item">
      <span class="cf-lang-dot" style="background:${langColors[lang] || '#6366f1'}"></span>
      <span class="cf-lang-name">${lang}</span>
      <span class="cf-lang-meta">${info.files || 0} arquivos, ${(info.loc || 0).toLocaleString()} linhas (${pct.toFixed(1)}%)</span>
    </div>`;
  }
  html += '</div>';
  el.innerHTML = html;
}

function cfRenderPatterns(patterns) {
  const el = document.getElementById('cf-patterns');
  if (!patterns.length) { el.innerHTML = '<div class="cf-empty">Nenhum padrão detectado</div>'; return; }

  let html = '<div class="cf-pattern-grid">';
  for (const p of patterns) {
    const isAnti = p.type === 'anti-pattern' || p.name?.toLowerCase().includes('god object');
    html += `<div class="cf-pattern-item ${isAnti ? 'anti' : ''}">
      <div class="cf-pattern-name">${p.name || p.type || 'Padrão'}</div>
      <div class="cf-pattern-desc">${p.description || ''}</div>
      ${p.files ? `<div class="cf-pattern-files">${p.files.map(f => `<span class="cf-pattern-file">${f}</span>`).join('')}</div>` : ''}
    </div>`;
  }
  html += '</div>';
  el.innerHTML = html;
}

function cfRenderSecurity(issues) {
  const el = document.getElementById('cf-security');
  const countEl = document.getElementById('cf-security-count');
  if (!issues.length) {
    el.innerHTML = '<div class="cf-empty">Nenhum problema de segurança encontrado</div>';
    countEl.style.display = 'none';
    return;
  }

  countEl.style.display = 'inline-flex';
  countEl.textContent = issues.length;
  countEl.className = 'badge badge-red';

  let html = '';
  for (const s of issues) {
    const sev = s.severity || 'medium';
    html += `<div class="cf-security-item ${sev}">
      <div class="cf-security-title">${s.type || s.title || 'Problema'}</div>
      <div class="cf-security-desc">${s.description || s.message || ''}</div>
      ${s.file ? `<div class="cf-security-file">${s.file}${s.line ? ':' + s.line : ''}</div>` : ''}
      ${s.code ? `<pre class="cf-security-code">${s.code}</pre>` : ''}
    </div>`;
  }
  el.innerHTML = html;
}

function cfRenderCircular(circular) {
  const el = document.getElementById('cf-circular');
  const countEl = document.getElementById('cf-circular-count');
  if (!circular.length) {
    el.innerHTML = '<div class="cf-empty">Nenhuma dependência circular encontrada</div>';
    countEl.style.display = 'none';
    return;
  }

  countEl.style.display = 'inline-flex';
  countEl.textContent = circular.length;
  countEl.className = 'badge badge-yellow';

  let html = '';
  for (const c of circular) {
    const chain = c.chain || c.circular_dependency || [];
    html += `<div class="cf-circular-item">
      <div class="cf-circular-chain">${chain.map(f => `<span class="cf-chain-file">${f}</span>`).join('<span class="cf-chain-arrow">→</span>')}</div>
    </div>`;
  }
  el.innerHTML = html;
}

function cfRenderDead(dead) {
  const el = document.getElementById('cf-dead');
  const countEl = document.getElementById('cf-dead-count');
  if (!dead.length) {
    el.innerHTML = '<div class="cf-empty">Nenhuma função morta encontrada</div>';
    countEl.style.display = 'none';
    return;
  }

  countEl.style.display = 'inline-flex';
  countEl.textContent = dead.length;
  countEl.className = 'badge badge-yellow';

  let html = '<div class="cf-dead-list">';
  for (const fn of dead) {
    html += `<div class="cf-dead-item">
      <span class="cf-dead-name">${fn.name}</span>
      <span class="cf-dead-file">${fn.file}:${fn.line || '?'}</span>
    </div>`;
  }
  html += '</div>';
  el.innerHTML = html;
}

function cfRenderFiles(files) {
  const el = document.getElementById('cf-files');
  const countEl = document.getElementById('cf-files-count');
  if (!files.length) {
    el.innerHTML = '<div class="cf-empty">Nenhum arquivo analisado</div>';
    countEl.style.display = 'none';
    return;
  }

  countEl.style.display = 'inline-flex';
  countEl.textContent = files.length;

  const byFolder = {};
  for (const f of files) {
    const folder = f.folder || 'root';
    if (!byFolder[folder]) byFolder[folder] = [];
    byFolder[folder].push(f);
  }

  let html = '<div class="cf-files-content">';
  for (const [folder, items] of Object.entries(byFolder)) {
    html += `<div class="cf-folder-group">
      <div class="cf-folder-name">${folder}/</div>
      <div class="cf-files-grid">
      ${items.map(f => `<div class="cf-file-item">
        <svg class="cf-file-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
        <span class="cf-file-name">${f.name}</span>
        <span class="cf-file-meta">${f.language || 'text'} · ${f.lines || 0} linhas</span>
        ${f.functions?.length ? `<span class="cf-file-fns">${f.functions.length} fn</span>` : ''}
      </div>`).join('')}
      </div>
    </div>`;
  }
  html += '</div>';
  el.innerHTML = html;
}

function cfToggleSection(header) {
  const body = header.nextElementSibling;
  const toggle = header.querySelector('.card-toggle');
  if (body.style.display === 'none') {
    body.style.display = 'block';
    toggle.classList.add('open');
  } else {
    body.style.display = 'none';
    toggle.classList.remove('open');
  }
}

document.addEventListener('DOMContentLoaded', () => {
  document.getElementById('cf-repo-input').addEventListener('keydown', e => {
    if (e.key === 'Enter') cfAnalyze();
  });
});
