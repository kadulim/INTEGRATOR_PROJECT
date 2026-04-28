document.addEventListener('DOMContentLoaded', () => {
  setTimeout(() => {
    renderChartBars();
    renderDonut();
  }, 100);
});

// ── Volume por Mês ────────────────────────────────────────────────────
function renderChartBars() {
  const months = ['Jan','Fev','Mar','Abr','Mai','Jun','Jul','Ago','Set','Out','Nov','Dez'];

  // Usa dados reais injetados pelo servidor, ou fallback zerado
  const values = (window.DASHBOARD_VOLUMES && window.DASHBOARD_VOLUMES.length === 12)
    ? window.DASHBOARD_VOLUMES
    : new Array(12).fill(0);

  const max = Math.max(...values, 1); // garante que max >= 1 para evitar divisão por zero
  const container = document.getElementById('chart-bars');
  if (!container) return;

  container.innerHTML = months.map((m, i) => {
    const val = values[i];
    const pct = (val / max) * 100;
    // Se o valor for > 0 mas a pct for muito pequena, damos um mínimo para visibilidade
    const displayPct = val > 0 ? Math.max(pct, 5) : 0;

    return `
      <div class="chart-bar-wrap">
        <div class="chart-bar ${i === new Date().getMonth() ? 'active' : ''}"
             style="height: 0%" 
             data-height="${displayPct}%"
             title="${val} projeto(s) em ${m}"></div>
        <span class="chart-label">${m}</span>
      </div>
    `;
  }).join('');

  // Animação de subida das barras
  setTimeout(() => {
    container.querySelectorAll('.chart-bar').forEach(bar => {
      bar.style.height = bar.getAttribute('data-height');
    });
  }, 50);
}

// ── Status dos Projetos (Donut) ───────────────────────────────────────
function renderDonut() {
  // Usa dados reais injetados pelo servidor
  const data = (window.DASHBOARD_STATUS && window.DASHBOARD_STATUS.length > 0)
    ? window.DASHBOARD_STATUS.filter(d => d.val > 0)
    : [{ label: 'Sem dados', val: 1, color: '#6b7280' }];

  const total = data.reduce((acc, d) => acc + d.val, 0);
  const container = document.getElementById('donut-wrap');
  if (!container) return;

  const r = 45, cx = 55, cy = 55, strokeW = 18;
  const circ = 2 * Math.PI * r;
  let offset = 0;

  const segments = data.map(d => {
    const dash = (d.val / total) * circ;
    const seg = `<circle cx="${cx}" cy="${cy}" r="${r}"
      fill="none" stroke="${d.color}" stroke-width="${strokeW}"
      stroke-dasharray="${dash} ${circ}"
      stroke-dashoffset="${-offset}"
      transform="rotate(-90 ${cx} ${cy})"
      style="transition:stroke-dasharray 0.3s ease"/>`;
    offset += dash;
    return seg;
  });

  container.innerHTML = `
    <svg class="donut-svg" width="110" height="110" viewBox="0 0 110 110">
      ${segments.join('')}
      <text x="55" y="51" text-anchor="middle" font-family="DM Sans,sans-serif" font-size="18" font-weight="700" fill="var(--text-primary)">${total}</text>
      <text x="55" y="65" text-anchor="middle" font-family="DM Sans,sans-serif" font-size="9" fill="var(--text-muted)">projetos</text>
    </svg>
    <div class="donut-legend">
      ${data.map(d => `
        <div class="donut-legend-item">
          <div class="donut-dot" style="background:${d.color}"></div>
          <span style="font-size:12.5px;color:var(--text-secondary);">${d.label}</span>
          <span class="donut-val">${d.val}</span>
        </div>
      `).join('')}
    </div>
  `;
}
