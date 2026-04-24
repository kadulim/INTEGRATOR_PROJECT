document.addEventListener('DOMContentLoaded', () => {
  // Animar gráficos
  setTimeout(() => {
    renderChartBars();
    renderDonut();
  }, 100);
});

function renderChartBars() {
  const months = ['Jan','Fev','Mar','Abr','Mai','Jun','Jul','Ago','Set','Out','Nov','Dez'];
  const values = [2, 1, 3, 2, 4, 3, 5, 2, 4, 6, 3, 2];
  const max    = Math.max(...values);
  const container = document.getElementById('chart-bars');
  if (!container) return;

  container.innerHTML = months.map((m, i) => `
    <div class="chart-bar-wrap">
      <div class="chart-bar ${i === new Date().getMonth() ? 'active' : ''}"
           style="height:${(values[i]/max)*100}%"
           title="${values[i]} projeto(s)"></div>
      <span class="chart-label">${m}</span>
    </div>
  `).join('');
}

function renderDonut() {
  // Dados fictícios visuais (apenas animação)
  const data = [
    { label: 'Em andamento', val: 3,   color: '#3b82f6' },
    { label: 'Concluído',    val: 1, color: '#22c55e' },
    { label: 'Planejamento', val: 1, color: '#8b5cf6' },
    { label: 'Pausado',      val: 1,  color: '#f59e0b' },
  ].filter(d => d.val > 0);
  
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
      style="transition:stroke-dasharray 0.8s ease"/>`;
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
