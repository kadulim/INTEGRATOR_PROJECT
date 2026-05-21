document.addEventListener('DOMContentLoaded', () => {
    if (window.lucide) {
        lucide.createIcons();
    }

    setTimeout(() => {
        renderModernChartBars();
        renderModernDonut();
        renderSparklines();
    }, 200);
});

// ── Renderização de Sparklines ──────────────────────────────────────────
function renderSparklines() {
    const ids = ['sparkline-projects', 'sparkline-clients', 'sparkline-staff', 'sparkline-budget'];
    const colors = ['#3b82f6', '#10b981', '#8b5cf6', '#f43f5e'];

    ids.forEach((id, index) => {
        const container = document.getElementById(id);
        if (!container) return;

        const width = 100;
        const height = 35;
        // Dados fixos para combinar com a imagem
        const points = [8, 12, 10, 15, 12, 18, 14, 20];
        const max = Math.max(...points);
        
        const pathData = points.map((p, i) => {
            const x = (i / (points.length - 1)) * width;
            const y = height - (p / max) * height;
            return `${i === 0 ? 'M' : 'L'} ${x} ${y}`;
        }).join(' ');

        container.innerHTML = `
            <svg width="${width}" height="${height}" style="overflow: visible;">
                <path d="${pathData}" fill="none" stroke="${colors[index]}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"></path>
                <path d="${pathData} L ${width} ${height} L 0 ${height} Z" fill="${colors[index]}" style="opacity: 0.1;"></path>
            </svg>
        `;
    });
}

// ── Volume por Mês (Moderno) ─────────────────────────────────────────────
function renderModernChartBars() {
    const months = ['Jan','Fev','Mar','Abr','Mai','Jun','Jul','Ago','Set','Out','Nov','Dez'];
    const values = (window.DASHBOARD_VOLUMES && window.DASHBOARD_VOLUMES.length === 12)
        ? window.DASHBOARD_VOLUMES
        : [0.2, 0.2, 0.2, 0.2, 1.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2];

    const max = 3;
    const container = document.getElementById('chart-bars-modern');
    if (!container) return;

    container.innerHTML = `
        <div class="chart-y-axis">
            <span>3</span>
            <span>2</span>
            <span>1</span>
            <span>0</span>
        </div>
        ${months.map((m, i) => {
            const val = values[i];
            const hPct = (val / max) * 100;
            const isActive = i === 4; // Maio ativo
            return `
                <div class="chart-bar-item">
                    <div class="bar-rect ${isActive ? 'active' : ''}" style="height: 0%;" data-height="${hPct}%"></div>
                    <span class="bar-label">${m}</span>
                </div>
            `;
        }).join('')}
    `;

    setTimeout(() => {
        container.querySelectorAll('.bar-rect').forEach(bar => {
            bar.style.height = bar.getAttribute('data-height');
        });
    }, 100);
}

// ── Status dos Projetos (Donut Moderno) ──────────────────────────────────
function renderModernDonut() {
    const data = (window.DASHBOARD_STATUS && window.DASHBOARD_STATUS.length > 0)
        ? window.DASHBOARD_STATUS.filter(d => d.val > 0 && d.label !== 'Cancelado' && d.label !== 'Cancelados')
        : [
            { label: 'Em andamento', val: 1, color: '#f59e0b' },
            { label: 'Concluídos', val: 0, color: '#10b981' },
            { label: 'Pausado', val: 0, color: '#FF5577' },
            { label: 'Cancelados', val: 0, color: '#ec0000' }
        ];

    const total = data.reduce((acc, d) => acc + d.val, 0);
    const container = document.getElementById('donut-modern');
    const legendContainer = document.querySelector('.donut-legend-modern');
    if (!container || !legendContainer) return;

    const r = 40, cx = 60, cy = 60, strokeW = 14;
    const circ = 2 * Math.PI * r;
    let offset = 0;

    const segments = data.map(d => {
        const dash = (d.val / total) * circ;
        const seg = `<circle cx="${cx}" cy="${cy}" r="${r}"
            fill="none" stroke="${d.color}" stroke-width="${strokeW}"
            stroke-dasharray="${dash} ${circ}"
            stroke-dashoffset="${-offset}"
            transform="rotate(-90 ${cx} ${cy})"
            stroke-linecap="round"
            style="transition: all 0.6s ease-out"></circle>`;
        offset += dash;
        return seg;
    });

    container.innerHTML = `
        <svg width="120" height="120" viewBox="0 0 120 120">
            <circle cx="${cx}" cy="${cy}" r="${r}" fill="none" stroke="var(--border)" stroke-width="${strokeW}" style="opacity: 0.15;"></circle>
            ${segments.join('')}
            <text x="${cx}" y="${cy - 3}" text-anchor="middle" font-size="22" font-weight="800" fill="var(--text-primary)" style="dominant-baseline: middle;">${total}</text>
            <text x="${cx}" y="${cy + 16}" text-anchor="middle" font-size="11" font-weight="600" fill="var(--text-muted)">projetos</text>
        </svg>
    `;

    legendContainer.innerHTML = data.map(d => `
        <div class="legend-item-modern">
            <div class="legend-label-wrap">
                <div style="width: 8px; height: 8px; border-radius: 50%; background: ${d.color};"></div>
                <span>${d.label}</span>
            </div>
            <span class="legend-count">${d.val}</span>
        </div>
    `).join('');
}
