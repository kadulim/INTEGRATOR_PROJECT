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
  const stats = data.stats || {};

  document.getElementById('cf-kpi-row').style.display = 'grid';
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

  cfRenderLanguageDonut(stats.languages || {}, stats.loc || 0);
  cfRenderSecurityDonut(data.security_issues || []);
  cfRenderTopFilesChart(data.files || []);
  document.getElementById('cf-charts-row').style.display = 'grid';
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

// ── Tab Switching ──
function cfSwitchTab(tab) {
  document.querySelectorAll('.cf-tab').forEach(t => t.classList.remove('cf-tab-active'));
  document.querySelectorAll('.cf-tab-content').forEach(c => c.classList.remove('cf-tab-content-active'));
  document.querySelector(`.cf-tab[data-tab="${tab}"]`).classList.add('cf-tab-active');
  document.getElementById(`cf-tab-${tab}`).classList.add('cf-tab-content-active');
  document.getElementById('cf-error').style.display = 'none';
}

// ── File Selection State ──
let cfSelectedFiles = [];
let cfUploadMode = 'files';

function cfSwitchUploadMode(mode) {
  cfUploadMode = mode;
  document.querySelectorAll('.cf-mode-btn').forEach(b => {
    b.classList.toggle('cf-mode-active', b.dataset.mode === mode);
  });
  const input = document.getElementById('cf-file-input');
  if (mode === 'folder') {
    input.removeAttribute('accept');
    input.setAttribute('webkitdirectory', '');
    input.setAttribute('mozdirectory', '');
    input.setAttribute('odirectory', '');
  } else {
    input.setAttribute('accept', '.py,.js,.jsx,.ts,.tsx,.java,.go,.rb,.php,.rs,.c,.cpp,.h,.hpp,.cs,.swift,.kt,.html,.css,.vue,.svelte,.md,.json,.yaml,.yml,.toml,.sh,.bash,.sql,.r,.lua,.dart');
    input.removeAttribute('webkitdirectory');
    input.removeAttribute('mozdirectory');
    input.removeAttribute('odirectory');
  }
  const text = document.querySelector('.cf-upload-text');
  if (mode === 'folder') {
    text.innerHTML = '<strong>Clique para selecionar</strong> ou arraste uma pasta aqui';
  } else {
    text.innerHTML = '<strong>Clique para selecionar</strong> ou arraste arquivos aqui';
  }
}

async function cfTraverseEntry(entry, path = '') {
  if (entry.isFile) {
    return new Promise(resolve => {
      entry.file(file => {
        file._cfRelPath = path ? path + '/' + entry.name : entry.name;
        resolve(file);
      });
    });
  }
  if (entry.isDirectory) {
    const reader = entry.createReader();
    const entries = await new Promise(resolve => {
      reader.readEntries(results => resolve(results));
    });
    const results = await Promise.all(
      entries.map(e => cfTraverseEntry(e, path ? path + '/' + entry.name : entry.name))
    );
    return results.flat();
  }
  return [];
}

function cfFormatSize(bytes) {
  if (bytes < 1024) return bytes + ' B';
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}

function cfUpdateUploadUI() {
  const container = document.getElementById('cf-upload-files');
  const btn = document.getElementById('cf-upload-btn');
  container.innerHTML = cfSelectedFiles.map((f, i) =>
    `<div class="cf-upload-file">
      <span class="cf-upload-file-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg></span>
      <span class="cf-upload-file-name">${f.name}</span>
      ${f._cfRelPath ? `<span class="cf-upload-file-path" title="${f._cfRelPath}">${f._cfRelPath}</span>` : ''}
      <span class="cf-upload-file-size">${cfFormatSize(f.size)}</span>
      <span class="cf-upload-file-remove" onclick="cfRemoveFile(${i})">✕</span>
    </div>`
  ).join('');
  btn.disabled = cfSelectedFiles.length === 0;
}

function cfRemoveFile(index) {
  cfSelectedFiles.splice(index, 1);
  cfUpdateUploadUI();
}

function cfUpload() {
  if (!cfSelectedFiles.length) return;

  const btn = document.getElementById('cf-upload-btn');
  const error = document.getElementById('cf-error');
  const results = document.getElementById('cf-results');
  const loading = document.getElementById('cf-loading');
  const content = document.getElementById('cf-content');

  error.style.display = 'none';
  btn.disabled = true;
  btn.innerHTML = 'Analisando...';
  results.style.display = 'block';
  loading.style.display = 'flex';
  content.style.display = 'none';

  const formData = new FormData();
  for (const file of cfSelectedFiles) {
    formData.append('files', file, file._cfRelPath || file.name);
  }

  fetch(CODEFLOW_API_URL + '/api/analyze/upload', {
    method: 'POST',
    body: formData,
  })
    .then(async r => {
      let data;
      try { data = await r.json(); } catch { data = null; }
      if (!r.ok) {
        throw new Error(data?.error || `Erro HTTP ${r.status} — ${r.statusText}`);
      }
      return data;
    })
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
      cfShowError(err.message || 'Erro ao conectar com a API CodeFlow.');
      results.style.display = 'none';
    })
    .finally(() => {
      btn.disabled = false;
      btn.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="16" height="16"><polyline points="16 3 21 3 21 8"/><line x1="4" y1="20" x2="21" y2="3"/><polyline points="21 16 21 21 16 21"/><line x1="15" y1="15" x2="21" y2="21"/><line x1="4" y1="4" x2="9" y2="9"/></svg> Analisar Arquivos';
    });
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

const CF_COLORS = [
  '#f72585', '#b5179e', '#4361ee', '#4cc9f0', '#f8961e',
  '#f9c74f', '#90be6d', '#43aa8b', '#577590', '#e63946',
  '#a8dadc', '#1d3557', '#2a9d8f', '#e76f51', '#264653',
];

function cfDonutChart(svgEl, segments, total, centerLabel) {
  const r = 80, cx = 100, cy = 100, sw = 20;
  const circ = 2 * Math.PI * r;
  let offset = 0;

  let html = `<circle cx="${cx}" cy="${cy}" r="${r}" fill="none" stroke="var(--border)" stroke-width="${sw}" opacity="0.15"/>`;

  for (const seg of segments) {
    const val = seg.val || 0;
    const dash = total > 0 ? (val / total) * circ : 0;
    html += `<circle cx="${cx}" cy="${cy}" r="${r}"
      fill="none" stroke="${seg.color}" stroke-width="${sw}"
      stroke-dasharray="${dash} ${circ}"
      stroke-dashoffset="${-offset}"
      transform="rotate(-90 ${cx} ${cy})"
      stroke-linecap="butt"
      style="transition: stroke-dasharray 0.8s cubic-bezier(0.34,1.56,0.64,1)"/>
      <circle cx="${cx}" cy="${cy}" r="${r}"
        fill="none" stroke="rgba(255,255,255,0.03)" stroke-width="${sw + 4}"
        stroke-dasharray="${dash} ${circ}"
        stroke-dashoffset="${-offset}"
        transform="rotate(-90 ${cx} ${cy})"
        opacity="0" pointer-events="none"/>`;
    offset += dash;
  }

  html += `<text x="${cx}" y="${cy - 4}" text-anchor="middle" font-size="28" font-weight="800" fill="var(--text-primary)" dominant-baseline="middle">${total}</text>`;
  html += `<text x="${cx}" y="${cy + 18}" text-anchor="middle" font-size="11" font-weight="600" fill="var(--text-muted)" dominant-basaling="middle">${centerLabel}</text>`;

  svgEl.innerHTML = html;
}

function cfLegendItems(container, items) {
  container.innerHTML = items.map(item =>
    `<div class="cf-legend-item">
      <span class="cf-legend-dot" style="background:${item.color}"></span>
      <span class="cf-legend-name">${item.label}</span>
      <span class="cf-legend-pct">${item.pct}%</span>
      <span class="cf-legend-val">${item.val.toLocaleString()}</span>
    </div>`
  ).join('');
}

function cfRenderLanguageDonut(languages, totalLoc) {
  const svgEl = document.getElementById('cf-chart-languages');
  const legendEl = document.getElementById('cf-legend-languages');
  if (!svgEl || !legendEl) return;

  const langColors = {
    javascript: '#f7df1e', typescript: '#3178c6', python: '#3572a5',
    html: '#e34f26', css: '#563d7c', java: '#b07219', go: '#00add8',
    ruby: '#701516', php: '#4f5d95', rust: '#dea584', c: '#555555',
    'c++': '#f34b7d', 'c#': '#178600', swift: '#ffac45', kotlin: '#f18e33',
    scala: '#c22d40', elixir: '#6e4a7e', haskell: '#5e5086', lua: '#000080',
    r: '#198ce7', dart: '#00b4ab', shell: '#89e051', vue: '#42b883',
    svelte: '#ff3e00',
  };

  const keys = Object.keys(languages);
  if (!keys.length) {
    svgEl.innerHTML = '';
    legendEl.innerHTML = '';
    return;
  }

  const sorted = keys
    .map(k => ({ label: k, val: languages[k].loc || 0, color: langColors[k] || '#6366f1' }))
    .sort((a, b) => b.val - a.val);

  const total = sorted.reduce((s, i) => s + i.val, 0);
  cfDonutChart(svgEl, sorted, total, 'linhas');

  const legendItems = sorted.map(item => ({
    ...item,
    pct: total ? ((item.val / total) * 100).toFixed(1) : 0,
  }));
  cfLegendItems(legendEl, legendItems);
}

function cfRenderSecurityDonut(issues) {
  const svgEl = document.getElementById('cf-chart-security');
  const legendEl = document.getElementById('cf-legend-security');
  if (!svgEl || !legendEl) return;

  const sevMap = { high: 0, medium: 0, low: 0 };
  for (const s of issues) {
    const sev = s.severity || 'medium';
    if (sevMap[sev] !== undefined) sevMap[sev]++;
  }

  const sevConfig = [
    { label: 'Alta', val: sevMap.high, color: '#ef4444' },
    { label: 'Média', val: sevMap.medium, color: '#f59e0b' },
    { label: 'Baixa', val: sevMap.low, color: '#3b82f6' },
  ];

  const active = sevConfig.filter(s => s.val > 0);
  const total = issues.length;

  if (!total) {
    svgEl.innerHTML = `<text x="100" y="104" text-anchor="middle" font-size="14" font-weight="600" fill="var(--text-muted)">Nenhum</text>`;
    legendEl.innerHTML = '';
    return;
  }

  cfDonutChart(svgEl, active.length ? active : [sevConfig[0]], total, 'problemas');

  const legendItems = active.length ? active.map(s => ({
    ...s,
    pct: ((s.val / total) * 100).toFixed(0),
  })) : [];
  cfLegendItems(legendEl, legendItems);
}

function cfRenderTopFilesChart(files) {
  const svgEl = document.getElementById('cf-chart-topfiles');
  if (!svgEl) return;

  const withFns = files.filter(f => f.functions?.length > 0);
  if (!withFns.length) {
    svgEl.innerHTML = `<text x="200" y="84" text-anchor="middle" font-size="13" font-weight="600" fill="var(--text-muted)">Nenhum dado</text>`;
    return;
  }

  const sorted = withFns
    .map(f => ({ name: f.name || f.path, val: f.functions.length }))
    .sort((a, b) => b.val - a.val)
    .slice(0, 8);

  const maxVal = sorted[0].val || 1;
  const barH = 20;
  const gap = 10;
  const padL = 28, padR = 60, padT = 20, padB = 10;
  const chartW = 400;
  const maxBarW = chartW - padL - padR;
  const chartH = sorted.length * (barH + gap) + padT + padB;
  svgEl.setAttribute('viewBox', `0 0 ${chartW} ${chartH}`);

  let defs = '';
  let html = '';

  sorted.forEach((item, i) => {
    const color = CF_COLORS[i % CF_COLORS.length];
    const gradId = `cf-topg-${i}`;
    defs += `<linearGradient id="${gradId}" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="${color}" stop-opacity="0.9"/>
      <stop offset="100%" stop-color="${color}" stop-opacity="0.35"/>
    </linearGradient>`;

    const y = i * (barH + gap) + padT;
    const w = Math.max(4, (item.val / maxVal) * maxBarW);
    const displayName = item.name.length > 30 ? item.name.slice(0, 27) + '...' : item.name;
    const valW = String(item.val).length * 7 + 12;

    html += `<rect class="cf-bar-track" x="${padL}" y="${y}" width="${maxBarW}" height="${barH}" rx="6"/>`;
    html += `<rect class="cf-bar-fill" x="${padL}" y="${y}" width="0" height="${barH}" rx="6" fill="url(#${gradId})" data-w="${w}" style="animation-delay:${i * 0.07}s"/>`;
    html += `<text class="cf-bar-rank" x="${padL - 10}" y="${y + barH / 2 + 1}">${i + 1}</text>`;
    html += `<text class="cf-bar-name" x="${padL + 10}" y="${y + barH / 2 + 1}">${displayName}</text>`;
    html += `<title>${item.name}: ${item.val} funções</title>`;
    html += `<rect class="cf-bar-badge-bg" x="${padL + w + 6}" y="${y + 3}" width="${valW}" height="${barH - 6}" rx="4" fill="${color}"/>`;
    html += `<text class="cf-bar-badge" x="${padL + w + 6 + valW / 2}" y="${y + barH / 2 + 1}">${item.val}</text>`;
  });

  svgEl.innerHTML = `<defs>${defs}</defs>${html}`;

  requestAnimationFrame(() => {
    requestAnimationFrame(() => {
      svgEl.querySelectorAll('.cf-bar-fill').forEach(r => {
        r.setAttribute('width', r.dataset.w);
      });
    });
  });
}

document.addEventListener('DOMContentLoaded', () => {
  document.getElementById('cf-repo-input').addEventListener('keydown', e => {
    if (e.key === 'Enter') cfAnalyze();
  });

  // Upload area handlers
  const uploadArea = document.getElementById('cf-upload-area');
  const fileInput = document.getElementById('cf-file-input');

  uploadArea.addEventListener('click', () => fileInput.click());
  fileInput.addEventListener('change', async e => {
    if (cfUploadMode === 'folder' && e.target.files.length > 0) {
      const filesWithPath = Array.from(e.target.files).map(f => {
        f._cfRelPath = f.webkitRelativePath || f.name;
        return f;
      });
      cfSelectedFiles = cfSelectedFiles.concat(filesWithPath);
    } else {
      cfSelectedFiles = cfSelectedFiles.concat(Array.from(e.target.files));
    }
    cfUpdateUploadUI();
    e.target.value = '';
  });

  uploadArea.addEventListener('dragover', e => {
    e.preventDefault();
    uploadArea.classList.add('drag-over');
  });
  uploadArea.addEventListener('dragleave', () => {
    uploadArea.classList.remove('drag-over');
  });
  uploadArea.addEventListener('drop', async e => {
    e.preventDefault();
    uploadArea.classList.remove('drag-over');
    const items = e.dataTransfer.items;
    if (items && items.length > 0) {
      const allFiles = [];
      for (const item of items) {
        const entry = item.webkitGetAsEntry ? item.webkitGetAsEntry() : null;
        if (entry) {
          const files = await cfTraverseEntry(entry);
          allFiles.push(...files);
        }
      }
      if (allFiles.length > 0) {
        cfSelectedFiles = cfSelectedFiles.concat(allFiles);
      } else {
        cfSelectedFiles = cfSelectedFiles.concat(Array.from(e.dataTransfer.files));
      }
    } else {
      cfSelectedFiles = cfSelectedFiles.concat(Array.from(e.dataTransfer.files));
    }
    cfUpdateUploadUI();
  });
});
