// ── Index / Landing Page ──────────────────────────────────

document.addEventListener('DOMContentLoaded', () => {
  // Redirecionar se já logado
  const user = Auth.current();
  if (user) {
    if (user.role === 'client') {
      window.location.href = 'cliente-dashboard.html';
    } else {
      window.location.href = 'dashboard.html';
    }
    return;
  }

  renderPageCards();
});

function renderPageCards() {
  const pages = [
    {
      href:  'login.html',
      title: 'Login',
      desc:  'Autenticação segura com três perfis: Administrador, Funcionário e Cliente.',
      icon:  iconLock(),
      color: 'var(--accent-soft)',
      iconColor: 'var(--accent)',
      tag:   'Acesso',
    },
    {
      href:  'dashboard.html',
      title: 'Dashboard',
      desc:  'Visão geral de todos os projetos, métricas, gráficos e atividade recente.',
      icon:  iconHome(),
      color: 'var(--blue-soft)',
      iconColor: 'var(--blue)',
      tag:   'Admin / Funcionário',
    },
    {
      href:  'projetos.html',
      title: 'Projetos',
      desc:  'Lista de projetos com visualização em Cards, Kanban e Tabela. Filtros e busca.',
      icon:  iconFolder(),
      color: 'var(--green-soft)',
      iconColor: 'var(--green)',
      tag:   'Admin / Funcionário',
    },
    {
      href:  'equipes.html',
      title: 'Equipes',
      desc:  'Gerenciamento de membros da equipe, habilidades e carga de trabalho.',
      icon:  iconUsers(),
      color: 'var(--purple-soft)',
      iconColor: 'var(--purple)',
      tag:   'Admin / Funcionário',
    },
    {
      href:  'configuracoes.html',
      title: 'Configurações',
      desc:  'Perfil, notificações, segurança, aparência e integrações.',
      icon:  iconSettings(),
      color: 'var(--yellow-soft)',
      iconColor: 'var(--yellow)',
      tag:   'Todos',
    },
    {
      href:  'cliente-dashboard.html',
      title: 'Dashboard do Cliente',
      desc:  'Interface exclusiva para clientes acompanharem seus projetos e deixarem feedback.',
      icon:  iconUser(),
      color: 'var(--accent-soft)',
      iconColor: 'var(--accent)',
      tag:   'Cliente',
    },
    {
      href:  'projeto-detalhe.html',
      title: 'Detalhe do Projeto',
      desc:  'Hub completo do projeto: Visão Geral, Documentação, Requisitos, Diagramas, Equipe e Comentários.',
      icon:  iconChart(),
      color: 'var(--blue-soft)',
      iconColor: 'var(--blue)',
      tag:   'Admin / Funcionário',
    },
  ];

  const grid = document.getElementById('pages-grid');
  grid.innerHTML = pages.map((p, i) => `
    <a href="${p.href}" class="page-card fade-up" style="animation-delay:${0.06*i}s">
      <div class="page-card-icon" style="background:${p.color};color:${p.iconColor};">
        ${p.icon}
      </div>
      <div class="page-card-title">${p.title}</div>
      <div class="page-card-desc">${p.desc}</div>
      <div class="page-card-tag">
        ${iconArrow()}
        ${p.tag}
      </div>
    </a>
  `).join('');
}
