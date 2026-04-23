
// ===================== DATA =====================
const USERS = [
  { id:'1', name:'Admin Principal', email:'admin@cobyte.com', role:'admin' },
  { id:'2', name:'João Santos', email:'joao@cobyte.com', role:'employee' },
  { id:'3', name:'Cliente TechCorp', email:'contato@techcorp.com', role:'client', clientProjectId:'1' },
  { id:'4', name:'Cliente DeliveryPlus', email:'contato@deliveryplus.com', role:'client', clientProjectId:'2' },
];

const PROJECTS = [
  { id:'1', name:'Sistema de E-commerce', description:'Plataforma completa de vendas online com integração de pagamento', status:'Em andamento', team:5, documents:12, requirements:24, diagrams:6, lastUpdate:'Há 2 horas', progress:65, startDate:'15/01/2026', deadline:'30/06/2026' },
  { id:'2', name:'App Mobile Delivery', description:'Aplicativo de delivery com rastreamento em tempo real', status:'Em andamento', team:4, documents:8, requirements:18, diagrams:4, lastUpdate:'Há 5 horas', progress:45, startDate:'01/02/2026', deadline:'15/07/2026' },
  { id:'3', name:'Portal Corporativo', description:'Sistema interno de gestão de recursos humanos', status:'Planejamento', team:3, documents:4, requirements:12, diagrams:2, lastUpdate:'Há 1 dia', progress:20, startDate:'10/03/2026', deadline:'30/09/2026' },
  { id:'4', name:'API de Integração', description:'API REST para integração com sistemas legados', status:'Em andamento', team:2, documents:6, requirements:15, diagrams:3, lastUpdate:'Há 3 horas', progress:80, startDate:'05/01/2026', deadline:'30/05/2026' },
  { id:'5', name:'Dashboard Analytics', description:'Painel de visualização de dados e métricas', status:'Em andamento', team:3, documents:5, requirements:10, diagrams:4, lastUpdate:'Há 6 horas', progress:55, startDate:'15/02/2026', deadline:'15/08/2026' },
  { id:'6', name:'Sistema de Gestão Escolar', description:'Plataforma para gerenciamento de instituições de ensino', status:'Concluído', team:6, documents:20, requirements:35, diagrams:8, lastUpdate:'Há 2 dias', progress:100, startDate:'01/08/2025', deadline:'01/02/2026' },
];

const TEAM_DATA = {
  '1': [
    { id:1, name:'Maria Silva', role:'Gerente de Projeto', avatar:'MS', email:'maria.silva@exemplo.com' },
    { id:2, name:'João Santos', role:'Desenvolvedor Full Stack', avatar:'JS', email:'joao.santos@exemplo.com' },
    { id:3, name:'Ana Costa', role:'UX/UI Designer', avatar:'AC', email:'ana.costa@exemplo.com' },
    { id:4, name:'Pedro Almeida', role:'Analista de Requisitos', avatar:'PA', email:'pedro.almeida@exemplo.com' },
    { id:5, name:'Cliente TechCorp', role:'Cliente', avatar:'TC', email:'contato@techcorp.com' },
  ],
  '2': [
    { id:1, name:'Maria Silva', role:'Gerente de Projeto', avatar:'MS', email:'maria.silva@exemplo.com' },
    { id:2, name:'João Santos', role:'Desenvolvedor', avatar:'JS', email:'joao.santos@exemplo.com' },
    { id:3, name:'Rafael Lima', role:'Desenvolvedor Mobile', avatar:'RL', email:'rafael.lima@exemplo.com' },
  ],
};

const DOCS_DATA = {
  '1': [
    { id:1, name:'Documento de Requisitos v2.0', type:'Requisitos', lastEdit:'Há 2 horas', author:'Pedro Almeida', version:'2.0', status:'Em Revisão' },
    { id:2, name:'Especificação Técnica', type:'Especificação', lastEdit:'Há 5 horas', author:'João Santos', version:'1.5', status:'Aprovado' },
    { id:3, name:'Manual do Usuário', type:'Manual', lastEdit:'Há 1 dia', author:'Ana Costa', version:'1.0', status:'Rascunho' },
    { id:4, name:'Arquitetura do Sistema', type:'Arquitetura', lastEdit:'Há 3 horas', author:'João Santos', version:'1.2', status:'Aprovado' },
  ],
  '2': [
    { id:1, name:'Especificação do App', type:'Especificação', lastEdit:'Há 1 hora', author:'Maria Silva', version:'1.0', status:'Em Revisão' },
    { id:2, name:'Guia de Estilo', type:'Manual', lastEdit:'Há 4 horas', author:'Ana Costa', version:'1.1', status:'Aprovado' },
  ],
};

const REQS_DATA = {
  '1': [
    { id:1, code:'RF-001', title:'Login de Usuário', description:'O sistema deve permitir que usuários façam login com email e senha', type:'Funcional', priority:'Alta', status:'Aprovado', clientApproval:'approved' },
    { id:2, code:'RF-002', title:'Cadastro de Produtos', description:'Administradores devem poder cadastrar novos produtos', type:'Funcional', priority:'Alta', status:'Aprovado', clientApproval:'approved' },
    { id:3, code:'RF-003', title:'Carrinho de Compras', description:'Usuários devem poder adicionar produtos ao carrinho', type:'Funcional', priority:'Alta', status:'Em Revisão', clientApproval:'pending' },
    { id:4, code:'RNF-001', title:'Tempo de Resposta', description:'O sistema deve responder requisições em menos de 2 segundos', type:'Não Funcional', priority:'Média', status:'Pendente', clientApproval:'pending' },
    { id:5, code:'RNF-002', title:'Segurança de Dados', description:'Todas as senhas devem ser criptografadas', type:'Não Funcional', priority:'Alta', status:'Aprovado', clientApproval:'approved' },
  ],
  '2': [
    { id:1, code:'RF-001', title:'Rastreamento em Tempo Real', description:'O app deve mostrar localização do entregador em tempo real', type:'Funcional', priority:'Alta', status:'Aprovado', clientApproval:'approved' },
    { id:2, code:'RF-002', title:'Notificações Push', description:'Enviar notificações sobre status do pedido', type:'Funcional', priority:'Alta', status:'Aprovado', clientApproval:'pending' },
  ],
};

const DIAGRAMS_DATA = {
  '1': [
    { id:1, title:'Diagrama de Classes – Sistema Principal', type:'UML', author:'João Santos', lastEdit:'Há 3 horas', bg:'linear-gradient(135deg,#6366f1,#8b5cf6)' },
    { id:2, title:'Fluxo de Processo de Compra', type:'Fluxograma', author:'Ana Costa', lastEdit:'Há 1 dia', bg:'linear-gradient(135deg,#3b82f6,#06b6d4)' },
    { id:3, title:'Modelo de Dados – E-commerce', type:'Entidade-Relacionamento', author:'Pedro Almeida', lastEdit:'Há 2 dias', bg:'linear-gradient(135deg,#10b981,#059669)' },
    { id:4, title:'Sequência de Autenticação', type:'Sequência', author:'João Santos', lastEdit:'Há 8 horas', bg:'linear-gradient(135deg,#f59e0b,#ef4444)' },
  ],
  '2': [
    { id:1, title:'Arquitetura Mobile', type:'Arquitetura', author:'João Santos', lastEdit:'Há 2 horas', bg:'linear-gradient(135deg,#a855f7,#ec4899)' },
    { id:2, title:'Fluxo de Pedido', type:'Fluxograma', author:'Maria Silva', lastEdit:'Há 5 horas', bg:'linear-gradient(135deg,#3b82f6,#06b6d4)' },
  ],
};

const COMMENTS_DATA = {
  '1': [
    { id:1, author:'Cliente TechCorp', text:'Gostaria de revisar os requisitos de pagamento antes da próxima reunião.', date:'10/04/2026 14:30', isClient:true },
    { id:2, author:'Maria Silva', text:'Claro! Vou preparar um documento detalhado para você revisar.', date:'10/04/2026 15:15', isClient:false },
    { id:3, author:'Cliente TechCorp', text:'Perfeito! Também gostaria de discutir a integração com o sistema de estoque.', date:'11/04/2026 09:00', isClient:true },
  ],
  '2': [
    { id:1, author:'Cliente DeliveryPlus', text:'O rastreamento em tempo real está funcionando muito bem nos testes!', date:'09/04/2026 10:20', isClient:true },
    { id:2, author:'Maria Silva', text:'Que ótimo! Vamos continuar os testes de carga na próxima semana.', date:'09/04/2026 11:30', isClient:false },
  ],
};

const TEAM_MEMBERS = [
  { id:1, name:'Maria Silva', email:'maria.silva@exemplo.com', role:'Gerente de Projeto', projects:3, lastActive:'Agora', avatar:'MS', color:'#16a34a' },
  { id:2, name:'João Santos', email:'joao.santos@exemplo.com', role:'Desenvolvedor', projects:4, lastActive:'Há 2 horas', avatar:'JS', color:'#2563eb' },
  { id:3, name:'Ana Costa', email:'ana.costa@exemplo.com', role:'Desenvolvedor', projects:2, lastActive:'Há 5 horas', avatar:'AC', color:'#2563eb' },
  { id:4, name:'Pedro Almeida', email:'pedro.almeida@exemplo.com', role:'Analista', projects:3, lastActive:'Há 1 hora', avatar:'PA', color:'#ca8a04' },
  { id:5, name:'Carla Souza', email:'carla.souza@exemplo.com', role:'Administrador', projects:6, lastActive:'Há 30 min', avatar:'CS', color:'#dc2626' },
  { id:6, name:'Cliente – TechCorp', email:'contato@techcorp.com', role:'Cliente', projects:2, lastActive:'Há 3 horas', avatar:'TC', color:'#9333ea' },
  { id:7, name:'Rafael Lima', email:'rafael.lima@exemplo.com', role:'Desenvolvedor', projects:3, lastActive:'Há 4 horas', avatar:'RL', color:'#2563eb' },
  { id:8, name:'Julia Ferreira', email:'julia.ferreira@exemplo.com', role:'Desenvolvedor', projects:2, lastActive:'Há 6 horas', avatar:'JF', color:'#2563eb' },
];

const ACTIVITIES = [
  { id:1, user:'Maria Silva', action:'editou requisitos funcionais', project:'Sistema de E-commerce', time:'5 min atrás', type:'edit' },
  { id:2, user:'João Santos', action:'criou novo diagrama UML', project:'App Mobile Delivery', time:'15 min atrás', type:'create' },
  { id:3, user:'Ana Costa', action:'aprovou documentação', project:'Portal Corporativo', time:'1 hora atrás', type:'approve' },
  { id:4, user:'Pedro Almeida', action:'adicionou requisito não funcional', project:'Sistema de E-commerce', time:'2 horas atrás', type:'create' },
  { id:5, user:'Cliente – TechCorp', action:'comentou em documento', project:'API de Integração', time:'3 horas atrás', type:'edit' },
  { id:6, user:'Carlos Mendes', action:'atualizou diagrama de classes', project:'Sistema de E-commerce', time:'4 horas atrás', type:'edit' },
  { id:7, user:'Fernanda Lima', action:'criou novo requisito funcional', project:'App Mobile Delivery', time:'5 horas atrás', type:'create' },
  { id:8, user:'Cliente – StartupXYZ', action:'aprovou requisitos v1.5', project:'Portal Corporativo', time:'6 horas atrás', type:'approve' },
  { id:9, user:'Roberto Dias', action:'adicionou casos de uso', project:'API de Integração', time:'7 horas atrás', type:'create' },
  { id:10, user:'Juliana Rocha', action:'editou especificação técnica', project:'Sistema de E-commerce', time:'8 horas atrás', type:'edit' },
];

const PENDING_ITEMS = [
  { id:1, title:'Aprovar requisitos funcionais v2.0', project:'Sistema de E-commerce', priority:'Alta', dueDate:'Hoje' },
  { id:2, title:'Revisar diagrama de arquitetura', project:'App Mobile Delivery', priority:'Média', dueDate:'Amanhã' },
  { id:3, title:'Validar documentação com cliente', project:'Portal Corporativo', priority:'Alta', dueDate:'Hoje' },
  { id:4, title:'Atualizar casos de uso', project:'API de Integração', priority:'Baixa', dueDate:'Segunda-feira' },
];

// ===================== STATE =====================
let currentUser = null;
let currentProjectId = null;
let editingReqId = null;
let detailRequirements = {};
let detailComments = {};
let clientRequirements = [];
let clientComments = [];

// ===================== AUTH =====================
function selectUserType(type, btn) {
  document.querySelectorAll('.user-type-btn').forEach(b => b.classList.remove('selected'));
  btn.classList.add('selected');
}

function getSelectedUserType() {
  const sel = document.querySelector('.user-type-btn.selected');
  return sel ? sel.dataset.type : 'admin';
}

function doLogin() {
  const email = document.getElementById('login-email').value.trim();
  const pass  = document.getElementById('login-pass').value;
  const type  = getSelectedUserType();
  const err   = document.getElementById('login-error');

  if (!email || !pass) { showError(err, 'Preencha email e senha.'); return; }

  const user = USERS.find(u => u.email === email && u.role === type);
  if (!user) { showError(err, 'Credenciais inválidas ou tipo de usuário incorreto'); return; }

  err.classList.add('hidden');
  currentUser = user;
  localStorage.setItem('cobyte_user', JSON.stringify(user));

  if (user.role === 'client') {
    enterClientArea(user);
  } else {
    enterDashboard(user);
  }
}

function showError(el, msg) {
  el.textContent = msg;
  el.classList.remove('hidden');
}

function doLogout() {
  currentUser = null;
  localStorage.removeItem('cobyte_user');
  window.location.href = 'login.html';
}

function togglePass(id, btn) {
  const inp = document.getElementById(id);
  inp.type = inp.type === 'password' ? 'text' : 'password';
}

// ===================== ROUTING =====================
function showPage(pageId) {
  document.querySelectorAll('#auth-section .auth-page').forEach(p => p.classList.add('hidden'));
  document.getElementById(pageId).classList.remove('hidden');
}

function enterDashboard(user) {
  if (!document.getElementById('dashboard-section')) {
    window.location.href = 'dashboard.html';
    return;
  }
  document.getElementById('dashboard-section').classList.remove('hidden');
  document.getElementById('topbar-username').textContent = user.name;
  document.getElementById('topbar-role').textContent = user.role === 'admin' ? 'Administrador' : 'Funcionário';
  document.getElementById('topbar-avatar').textContent = user.name.charAt(0);
  navigate('dashboard');
}

function enterClientArea(user) {
  if (!document.getElementById('client-section')) {
    window.location.href = 'client.html';
    return;
  }
  document.getElementById('client-section').classList.remove('hidden');
  document.getElementById('client-name').textContent = user.name;
  document.getElementById('client-avatar').textContent = user.name.charAt(0);

  const pid = user.clientProjectId || '1';
  const proj = PROJECTS.find(p => p.id === pid) || PROJECTS[0];
  document.getElementById('client-proj-name').textContent    = proj.name;
  document.getElementById('client-proj-desc').textContent    = proj.description;
  document.getElementById('client-start').textContent        = proj.startDate;
  document.getElementById('client-deadline').textContent     = proj.deadline;
  document.getElementById('client-progress-bar').style.width = proj.progress + '%';
  document.getElementById('client-progress').textContent     = proj.progress + '%';

  clientRequirements = JSON.parse(JSON.stringify(REQS_DATA[pid] || []));
  clientComments     = JSON.parse(JSON.stringify(COMMENTS_DATA[pid] || []));
  document.getElementById('client-req-count').textContent = clientRequirements.length;

  renderClientRequirements();
  renderClientDocs(pid);
  renderClientDiagrams(pid);
  renderClientComments();
  updateClientPendingBadge();
}

function navigate(page, projectId) {
  document.querySelectorAll('#dashboard-section .page').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));

  if (page === 'dashboard') {
    document.getElementById('page-dashboard').classList.add('active');
    document.getElementById('nav-dashboard').classList.add('active');
    document.getElementById('page-title').textContent = 'Dashboard';
    document.getElementById('main-topbar').style.display = '';
    renderDashboard();
  } else if (page === 'projects') {
    document.getElementById('page-projects').classList.add('active');
    document.getElementById('nav-projects').classList.add('active');
    document.getElementById('page-title').textContent = 'Projetos';
    document.getElementById('main-topbar').style.display = '';
    renderProjects();
  } else if (page === 'project-detail') {
    currentProjectId = projectId;
    document.getElementById('page-project-detail').classList.add('active');
    document.getElementById('nav-projects').classList.add('active');
    document.getElementById('main-topbar').style.display = 'none';
    renderProjectDetail(projectId);
  } else if (page === 'new-project') {
    document.getElementById('page-new-project').classList.add('active');
    document.getElementById('nav-projects').classList.add('active');
    document.getElementById('page-title').textContent = 'Projetos';
    document.getElementById('main-topbar').style.display = '';
  } else if (page === 'teams') {
    document.getElementById('page-teams').classList.add('active');
    document.getElementById('nav-teams').classList.add('active');
    document.getElementById('page-title').textContent = 'Equipes';
    document.getElementById('main-topbar').style.display = '';
    renderTeams();
  } else if (page === 'settings') {
    document.getElementById('page-settings').classList.add('active');
    document.getElementById('nav-settings').classList.add('active');
    document.getElementById('page-title').textContent = 'Configurações';
    document.getElementById('main-topbar').style.display = '';
  }
}

// ===================== HELPERS =====================
const statusBadge = { 'Em andamento':'badge-blue', 'Concluído':'badge-green', 'Planejamento':'badge-yellow' };
const priorityBadge = { 'Alta':'badge-red', 'Média':'badge-yellow', 'Baixa':'badge-green' };
const reqStatusBadge = { 'Aprovado':'badge-green', 'Pendente':'badge-yellow', 'Rejeitado':'badge-red', 'Em Revisão':'badge-blue' };
const typeBadge = { 'Funcional':'badge-indigo', 'Não Funcional':'badge-purple' };
const docStatusBadge = { 'Rascunho':'badge-gray', 'Em Revisão':'badge-yellow', 'Aprovado':'badge-green' };
const docTypeBadge = { 'Requisitos':'badge-indigo', 'Especificação':'badge-purple', 'Manual':'badge-blue', 'Arquitetura':'badge-pink', 'Casos de Uso':'badge-cyan' };
const diagTypeBadge = { 'UML':'badge-indigo', 'Fluxograma':'badge-blue', 'Arquitetura':'badge-purple', 'Entidade-Relacionamento':'badge-green', 'Sequência':'badge-orange' };
const roleBadge = { 'Administrador':'badge-red', 'Desenvolvedor':'badge-blue', 'Cliente':'badge-purple', 'Gerente de Projeto':'badge-green', 'Analista':'badge-yellow' };

// SVG ICONS
const ICON = {
  edit: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>`,
  plus: `<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>`,
  check: `<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg>`,
  clock: `<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>`,
  file: `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>`,
  share: `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><line x1="8.59" y1="13.51" x2="15.42" y2="17.49"/></svg>`,
  download: `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>`,
  net: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><line x1="8.59" y1="13.51" x2="15.42" y2="17.49"/><line x1="15.41" y1="6.51" x2="8.59" y2="10.49"/></svg>`,
  mail: `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/></svg>`,
  more: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="5" r="1"/><circle cx="12" cy="12" r="1"/><circle cx="12" cy="19" r="1"/></svg>`,
  users: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 00-3-3.87"/><path d="M16 3.13a4 4 0 010 7.75"/></svg>`,
};

// ===================== DASHBOARD =====================
function renderDashboard() {
  // Projects
  const pl = document.getElementById('dash-projects-list');
  pl.innerHTML = PROJECTS.slice(0,4).map(p => `
    <div onclick="navigate('project-detail','${p.id}')" class="card card-hover" style="cursor:pointer;padding:16px">
      <div class="flex justify-between" style="margin-bottom:8px">
        <h3 class="font-semibold text-gray-900">${p.name}</h3>
        <span class="badge ${statusBadge[p.status]}">${p.status}</span>
      </div>
      <div class="flex gap-4 text-sm text-gray-600">
        <span class="flex items-center gap-1">${ICON.users} ${p.team} membros</span>
        <span class="flex items-center gap-1">${ICON.file} ${p.documents} docs</span>
        <span class="flex items-center gap-1">${ICON.clock} ${p.lastUpdate}</span>
      </div>
    </div>`).join('');

  // Pending
  const pen = document.getElementById('dash-pending-list');
  pen.innerHTML = PENDING_ITEMS.map(i => `
    <div class="card card-hover" style="padding:12px">
      <div class="flex justify-between gap-2" style="margin-bottom:6px">
        <h4 class="text-sm font-semibold text-gray-900">${i.title}</h4>
        <span class="badge ${priorityBadge[i.priority]}">${i.priority}</span>
      </div>
      <p class="text-xs text-gray-600" style="margin-bottom:4px">${i.project}</p>
      <p class="text-xs text-gray-500 flex items-center gap-1">${ICON.clock} ${i.dueDate}</p>
    </div>`).join('');

  // Activities
  const act = document.getElementById('dash-activities-list');
  const actIcons = { edit: ICON.file, create: ICON.plus, approve: ICON.check };
  act.innerHTML = ACTIVITIES.map(a => `
    <div class="activity-item">
      <div class="activity-icon">${actIcons[a.type]}</div>
      <div>
        <p class="text-sm"><strong>${a.user}</strong> <span class="text-gray-600">${a.action}</span></p>
        <p class="text-xs text-gray-500">${a.project}</p>
        <p class="text-xs text-gray-400" style="margin-top:2px">${a.time}</p>
      </div>
    </div>`).join('');
}

// ===================== PROJECTS =====================
function renderProjects(filter = '') {
  const list = filter
    ? PROJECTS.filter(p => p.name.toLowerCase().includes(filter.toLowerCase()))
    : PROJECTS;

  document.getElementById('projects-grid').innerHTML = list.map(p => `
    <div onclick="navigate('project-detail','${p.id}')" class="card card-hover" style="cursor:pointer">
      <div class="flex justify-between" style="margin-bottom:12px">
        <div>
          <h3 class="text-lg font-bold text-gray-900" style="margin-bottom:4px">${p.name}</h3>
          <p class="text-sm text-gray-600">${p.description}</p>
        </div>
        <button class="btn-icon" style="height:fit-content" onclick="event.stopPropagation()">${ICON.more}</button>
      </div>
      <div class="flex items-center gap-2" style="margin-bottom:14px">
        <span class="badge ${statusBadge[p.status]}">${p.status}</span>
        <span class="flex items-center gap-1 text-xs text-gray-500">${ICON.clock} ${p.lastUpdate}</span>
      </div>
      <div style="margin-bottom:14px">
        <div class="flex justify-between text-sm" style="margin-bottom:6px"><span class="text-gray-600">Progresso</span><span class="font-semibold">${p.progress}%</span></div>
        <div class="progress-bar"><div class="progress-fill" style="width:${p.progress}%"></div></div>
      </div>
      <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:8px;padding-top:14px;border-top:1px solid var(--gray-200)">
        <div class="text-center"><div class="flex justify-center" style="margin-bottom:4px">${ICON.users}</div><p class="text-sm font-semibold">${p.team}</p><p class="text-xs text-gray-500">Membros</p></div>
        <div class="text-center"><div class="flex justify-center" style="margin-bottom:4px">${ICON.file}</div><p class="text-sm font-semibold">${p.documents}</p><p class="text-xs text-gray-500">Docs</p></div>
        <div class="text-center"><div class="flex justify-center" style="margin-bottom:4px">${ICON.check}</div><p class="text-sm font-semibold">${p.requirements}</p><p class="text-xs text-gray-500">Requisitos</p></div>
        <div class="text-center"><div class="flex justify-center" style="margin-bottom:4px">${ICON.net}</div><p class="text-sm font-semibold">${p.diagrams}</p><p class="text-xs text-gray-500">Diagramas</p></div>
      </div>
    </div>`).join('');
}

function filterProjects() {
  renderProjects(document.getElementById('proj-search').value);
}

// ===================== PROJECT DETAIL =====================
function renderProjectDetail(pid) {
  const p    = PROJECTS.find(pr => pr.id === pid);
  const docs = DOCS_DATA[pid]  || [];
  const reqs = JSON.parse(JSON.stringify(REQS_DATA[pid]  || []));
  const diag = DIAGRAMS_DATA[pid] || [];
  const team = TEAM_DATA[pid]  || [];
  const comm = JSON.parse(JSON.stringify(COMMENTS_DATA[pid] || []));

  detailRequirements[pid] = reqs;
  detailComments[pid]     = comm;

  document.getElementById('detail-title').textContent       = p.name;
  document.getElementById('detail-desc').textContent        = p.description;
  document.getElementById('detail-start').textContent       = p.startDate;
  document.getElementById('detail-deadline').textContent    = p.deadline;
  document.getElementById('detail-team').textContent        = team.length + ' membros';
  document.getElementById('detail-progress-txt').textContent= p.progress + '%';
  document.getElementById('detail-progress-bar').style.width= p.progress + '%';
  document.getElementById('detail-docs-count').textContent  = docs.length;
  document.getElementById('detail-req-count').textContent   = reqs.length;
  document.getElementById('detail-diag-count').textContent  = diag.length;
  document.getElementById('detail-team-count').textContent  = team.length;
  document.getElementById('detail-comm-count').textContent  = comm.length;

  // Render tab contents
  renderDetailOverview(pid, docs, reqs, diag, team);
  renderDetailDocs(docs, pid);
  renderDetailReqs(reqs, pid);
  renderDetailDiags(diag);
  renderDetailTeam(team);
  renderDetailComments(comm, pid);

  // Reset tabs
  document.querySelectorAll('#detail-tabs .tab-btn').forEach(b => b.classList.remove('active'));
  document.querySelectorAll('#page-project-detail .tab-content').forEach(t => t.classList.remove('active'));
  document.querySelector('#detail-tabs .tab-btn').classList.add('active');
  document.getElementById('detail-tab-overview').classList.add('active');
}

function renderDetailOverview(pid, docs, reqs, diag, team) {
  const approved = reqs.filter(r => r.status === 'Aprovado').length;
  const pending  = reqs.filter(r => r.status === 'Pendente').length;
  const review   = reqs.filter(r => r.status === 'Em Revisão').length;

  document.getElementById('detail-tab-overview').innerHTML = `
    <div class="grid grid-4 gap-6" style="margin-bottom:24px">
      <div class="card"><div class="flex items-center gap-3" style="margin-bottom:8px">${ICON.file.replace('18','18')}<span class="text-sm text-gray-600">Documentos</span></div><p class="text-3xl font-bold">${docs.length}</p></div>
      <div class="card"><div class="flex items-center gap-3" style="margin-bottom:8px">${ICON.check}<span class="text-sm text-gray-600">Requisitos</span></div><p class="text-3xl font-bold">${reqs.length}</p></div>
      <div class="card"><div class="flex items-center gap-3" style="margin-bottom:8px">${ICON.net}<span class="text-sm text-gray-600">Diagramas</span></div><p class="text-3xl font-bold">${diag.length}</p></div>
      <div class="card"><div class="flex items-center gap-3" style="margin-bottom:8px">${ICON.users}<span class="text-sm text-gray-600">Membros</span></div><p class="text-3xl font-bold">${team.length}</p></div>
    </div>
    <div class="grid" style="grid-template-columns:2fr 1fr;gap:24px">
      <div class="card">
        <div class="flex justify-between" style="margin-bottom:16px"><h2 class="text-xl font-bold">Documentos Recentes</h2></div>
        <div class="space-y-3">
          ${docs.slice(0,3).map(d => `
            <div class="card card-hover" style="padding:14px;cursor:pointer">
              <div class="flex items-start gap-3" style="margin-bottom:8px">
                ${ICON.file}
                <div><h3 class="font-semibold">${d.name}</h3><p class="text-sm text-gray-600">${d.type}</p></div>
              </div>
              <div class="flex gap-4 text-xs text-gray-500"><span>Por ${d.author}</span><span>•</span><span>${d.lastEdit}</span></div>
            </div>`).join('')}
        </div>
      </div>
      <div class="card">
        <h2 class="text-xl font-bold" style="margin-bottom:16px">Status dos Requisitos</h2>
        <div class="space-y-3">
          <div style="padding:14px;background:var(--gray-50);border-radius:8px"><p class="text-2xl font-bold">${reqs.length}</p><p class="text-sm text-gray-600">Total</p></div>
          <div style="padding:14px;background:var(--green-50);border-radius:8px"><p class="text-2xl font-bold text-green-600">${approved}</p><p class="text-sm text-gray-600">Aprovados</p></div>
          <div style="padding:14px;background:var(--blue-50);border-radius:8px"><p class="text-2xl font-bold text-blue-600">${review}</p><p class="text-sm text-gray-600">Em Revisão</p></div>
          <div style="padding:14px;background:var(--yellow-50);border-radius:8px"><p class="text-2xl font-bold text-yellow-600">${pending}</p><p class="text-sm text-gray-600">Pendentes</p></div>
        </div>
      </div>
    </div>`;
}

function renderDetailDocs(docs, pid) {
  document.getElementById('detail-tab-docs').innerHTML = `
    <div class="flex justify-between gap-4" style="margin-bottom:20px">
      <div class="input-wrapper" style="flex:1;max-width:380px"><svg class="input-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg><input class="form-input has-icon" type="text" placeholder="Buscar documentos..." /></div>
      <button class="btn btn-primary">${ICON.plus} Novo Documento</button>
    </div>
    <div class="grid grid-2 gap-6">
      ${docs.map(d => `
        <div class="card card-hover">
          <div class="flex justify-between" style="margin-bottom:14px">
            <div class="flex items-start gap-3">
              <div style="width:48px;height:48px;border-radius:8px;background:var(--slate-100);display:flex;align-items:center;justify-content:center;flex-shrink:0">${ICON.file}</div>
              <div><h3 class="font-bold text-gray-900">${d.name}</h3><p class="text-sm text-gray-600">${d.type}</p></div>
            </div>
            <div class="flex gap-1">
              <button class="btn-icon">${ICON.share}</button>
              <button class="btn-icon">${ICON.download}</button>
            </div>
          </div>
          <div class="flex gap-2" style="margin-bottom:14px">
            <span class="badge ${docTypeBadge[d.type]||'badge-gray'}">${d.type}</span>
            <span class="badge ${docStatusBadge[d.status]||'badge-gray'}">${d.status}</span>
            <span class="badge badge-gray">v${d.version}</span>
          </div>
          <div class="flex justify-between pt-3" style="border-top:1px solid var(--gray-200)">
            <span class="text-sm text-gray-600 flex items-center gap-1">${ICON.share} ${d.author}</span>
            <span class="text-sm text-gray-600 flex items-center gap-1">${ICON.clock} ${d.lastEdit}</span>
          </div>
        </div>`).join('')}
    </div>`;
}

function renderDetailReqs(reqs, pid) {
  const funcCount = reqs.filter(r => r.type === 'Funcional').length;
  const nfCount   = reqs.filter(r => r.type === 'Não Funcional').length;

  document.getElementById('detail-tab-requirements').innerHTML = `
    <div class="flex justify-between gap-4" style="margin-bottom:16px">
      <div class="input-wrapper" style="flex:1;max-width:380px"><svg class="input-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg><input class="form-input has-icon" type="text" placeholder="Buscar requisitos..." id="req-search-${pid}" oninput="filterDetailReqs('${pid}')" /></div>
      <button class="btn btn-primary" onclick="openReqModal('${pid}',null)">${ICON.plus} Novo Requisito</button>
    </div>
    <div class="subtabs" style="margin-bottom:16px">
      <button class="subtab active-all" onclick="filterDetailReqsByType('${pid}','all',this)">Todos (${reqs.length})</button>
      <button class="subtab" onclick="filterDetailReqsByType('${pid}','Funcional',this)">Funcionais (${funcCount})</button>
      <button class="subtab" onclick="filterDetailReqsByType('${pid}','Não Funcional',this)">Não Funcionais (${nfCount})</button>
    </div>
    <div class="table-wrap"><div class="overflow-x-auto">
      <table id="req-table-${pid}">
        <thead><tr><th>Código</th><th>Requisito</th><th>Tipo</th><th>Prioridade</th><th>Status</th><th>Ações</th></tr></thead>
        <tbody id="req-tbody-${pid}"></tbody>
      </table>
    </div></div>`;

  renderReqRows(pid, reqs, 'all');
}

function renderReqRows(pid, reqs, filter) {
  const filtered = filter === 'all' ? reqs : reqs.filter(r => r.type === filter);
  document.getElementById(`req-tbody-${pid}`).innerHTML = filtered.length ? filtered.map(r => `
    <tr>
      <td><span class="font-mono text-sm font-semibold text-slate-700">${r.code}</span></td>
      <td><p class="font-semibold text-gray-900">${r.title}</p><p class="text-sm text-gray-600" style="margin-top:2px">${r.description}</p></td>
      <td><span class="badge ${typeBadge[r.type]||'badge-gray'}">${r.type}</span></td>
      <td><span class="badge ${priorityBadge[r.priority]}">${r.priority}</span></td>
      <td><span class="badge ${reqStatusBadge[r.status]||'badge-gray'}">${r.status}</span></td>
      <td><button class="btn-icon" onclick="openReqModal('${pid}',${r.id})" title="Editar">${ICON.edit}</button></td>
    </tr>`).join('') : `<tr><td colspan="6" style="text-align:center;color:var(--gray-500);padding:40px">Nenhum requisito nesta categoria</td></tr>`;
}

function filterDetailReqsByType(pid, type, btn) {
  document.querySelectorAll(`#detail-tab-requirements .subtab`).forEach(b => {
    b.className = 'subtab';
  });
  const activeClass = type === 'all' ? 'active-all' : type === 'Funcional' ? 'active-func' : 'active-nf';
  btn.classList.add(activeClass);
  renderReqRows(pid, detailRequirements[pid] || [], type);
}

function filterDetailReqs(pid) {
  const q = document.getElementById(`req-search-${pid}`).value.toLowerCase();
  const reqs = (detailRequirements[pid] || []).filter(r =>
    r.title.toLowerCase().includes(q) || r.code.toLowerCase().includes(q));
  document.getElementById(`req-tbody-${pid}`).innerHTML = reqs.length ? reqs.map(r => `
    <tr>
      <td><span class="font-mono text-sm font-semibold text-slate-700">${r.code}</span></td>
      <td><p class="font-semibold">${r.title}</p><p class="text-sm text-gray-600">${r.description}</p></td>
      <td><span class="badge ${typeBadge[r.type]||'badge-gray'}">${r.type}</span></td>
      <td><span class="badge ${priorityBadge[r.priority]}">${r.priority}</span></td>
      <td><span class="badge ${reqStatusBadge[r.status]||'badge-gray'}">${r.status}</span></td>
      <td><button class="btn-icon" onclick="openReqModal('${pid}',${r.id})">${ICON.edit}</button></td>
    </tr>`).join('') : `<tr><td colspan="6" style="text-align:center;color:var(--gray-500);padding:40px">Nenhum resultado</td></tr>`;
}

function renderDetailDiags(diag) {
  document.getElementById('detail-tab-diagrams').innerHTML = `
    <div class="flex justify-between gap-4" style="margin-bottom:20px">
      <div class="input-wrapper" style="flex:1;max-width:380px"><svg class="input-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg><input class="form-input has-icon" type="text" placeholder="Buscar diagramas..." /></div>
      <button class="btn btn-primary">${ICON.plus} Novo Diagrama</button>
    </div>
    <div class="grid grid-3 gap-6">
      ${diag.map(d => `
        <div class="card" style="padding:0;overflow:hidden;cursor:pointer">
          <div class="diagram-thumb" style="background:${d.bg}">${ICON.net.replace('16','48')}</div>
          <div style="padding:16px">
            <h3 class="font-bold text-gray-900" style="margin-bottom:8px">${d.title}</h3>
            <div style="margin-bottom:10px"><span class="badge ${diagTypeBadge[d.type]||'badge-gray'}">${d.type}</span></div>
            <div class="flex justify-between text-xs text-gray-600" style="margin-bottom:10px"><span>${d.author}</span><span class="flex items-center gap-1">${ICON.clock} ${d.lastEdit}</span></div>
            <div class="flex gap-2">
              <button class="btn" style="flex:1;background:var(--slate-100);color:var(--slate-700);padding:8px;font-size:13px">Abrir</button>
              <button class="btn-icon">${ICON.share}</button>
              <button class="btn-icon">${ICON.download}</button>
            </div>
          </div>
        </div>`).join('')}
    </div>`;
}

function renderDetailTeam(team) {
  document.getElementById('detail-tab-team').innerHTML = `
    <div class="flex justify-between gap-4" style="margin-bottom:20px">
      <div class="input-wrapper" style="flex:1;max-width:380px"><svg class="input-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg><input class="form-input has-icon" type="text" placeholder="Buscar membros..." /></div>
      <button class="btn btn-primary">${ICON.plus} Adicionar Membro</button>
    </div>
    <div class="grid" style="grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:20px">
      ${team.map(m => `
        <div class="member-card">
          <div class="flex justify-between" style="margin-bottom:12px">
            <div class="member-avatar" style="background:var(--slate-700)">${m.avatar}</div>
            <button class="btn-icon">${ICON.more}</button>
          </div>
          <h3 class="font-bold text-gray-900" style="margin-bottom:4px">${m.name}</h3>
          <p class="text-sm text-gray-600 flex items-center gap-1" style="margin-bottom:10px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">${ICON.mail} ${m.email}</p>
          <div style="margin-bottom:14px"><span class="badge ${roleBadge[m.role]||'badge-gray'}">${m.role}</span></div>
          <button class="btn btn-outline w-full" style="justify-content:center;font-size:13px">Ver Perfil</button>
        </div>`).join('')}
    </div>`;
}

function renderDetailComments(comm, pid) {
  const container = document.getElementById('detail-tab-comments');
  container.innerHTML = `
    <div style="max-width:800px">
      <div class="alert alert-blue flex items-start gap-3" style="margin-bottom:20px">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#2563eb" stroke-width="2" style="flex-shrink:0"><path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/></svg>
        <div><strong style="color:#1e40af">Comunicação com o Cliente</strong><p style="font-size:13px;color:#1e40af;margin-top:2px">Visualize comentários do cliente e responda diretamente.</p></div>
      </div>
      <h2 class="text-xl font-bold text-gray-900" style="margin-bottom:16px">Histórico de Comentários</h2>
      <div id="detail-comments-list-${pid}" class="space-y-4" style="margin-bottom:20px"></div>
      <div class="card">
        <h3 class="font-semibold text-gray-900" style="margin-bottom:14px">Responder ao Cliente</h3>
        <textarea class="form-textarea" id="detail-comment-input-${pid}" rows="4" placeholder="Escreva sua resposta..."></textarea>
        <div class="flex justify-end" style="margin-top:12px">
          <button class="btn btn-primary" onclick="sendDetailComment('${pid}')">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>
            Enviar Resposta
          </button>
        </div>
      </div>
    </div>`;
  renderCommentList(`detail-comments-list-${pid}`, detailComments[pid] || []);
}

function renderCommentList(containerId, comments) {
  document.getElementById(containerId).innerHTML = comments.length ? comments.map(c => `
    <div class="comment-box ${c.isClient ? 'is-client' : ''}">
      <div class="flex items-start gap-3">
        <div class="comment-avatar" style="background:${c.isClient ? 'var(--indigo-600)' : 'var(--slate-700)'}">${c.author.charAt(0)}</div>
        <div>
          <div class="flex items-center gap-2" style="margin-bottom:4px">
            <span class="font-semibold text-gray-900">${c.author}</span>
            <span class="badge ${c.isClient ? 'badge-indigo' : 'badge-slate'}">${c.isClient ? 'Cliente' : 'Equipe'}</span>
            <span class="text-xs text-gray-500">${c.date}</span>
          </div>
          <p class="text-gray-700 text-sm">${c.text}</p>
        </div>
      </div>
    </div>`).join('') : '<p class="text-gray-500 text-sm">Nenhum comentário ainda.</p>';
}

function sendDetailComment(pid) {
  const inp = document.getElementById(`detail-comment-input-${pid}`);
  const txt = inp.value.trim();
  if (!txt) return;
  const comm = { id: Date.now(), author: currentUser?.name || 'Equipe', text: txt, date: new Date().toLocaleString('pt-BR'), isClient: false };
  detailComments[pid] = detailComments[pid] || [];
  detailComments[pid].push(comm);
  renderCommentList(`detail-comments-list-${pid}`, detailComments[pid]);
  inp.value = '';
  document.getElementById('detail-comm-count').textContent = detailComments[pid].length;
}

// ===================== TEAMS =====================
function renderTeams() {
  const roles = ['Administrador','Desenvolvedor','Analista','Cliente'];
  document.getElementById('teams-stats').innerHTML = `
    <div class="card" style="padding:14px"><p class="text-sm text-gray-600" style="margin-bottom:4px">Total</p><p class="text-3xl font-bold">${TEAM_MEMBERS.length}</p></div>
    ${roles.map(r => `<div class="card" style="padding:14px"><p class="text-sm text-gray-600" style="margin-bottom:4px">${r}s</p><p class="text-3xl font-bold" style="color:${roleBadge[r]==='badge-red'?'#dc2626':roleBadge[r]==='badge-blue'?'#2563eb':roleBadge[r]==='badge-yellow'?'#ca8a04':'#9333ea'}">${TEAM_MEMBERS.filter(m=>m.role===r).length}</p></div>`).join('')}`;

  document.getElementById('teams-grid').innerHTML = TEAM_MEMBERS.map(m => `
    <div class="member-card">
      <div class="flex justify-between" style="margin-bottom:14px">
        <div class="member-avatar" style="background:${m.color}">${m.avatar}</div>
        <button class="btn-icon">${ICON.more}</button>
      </div>
      <h3 class="font-bold text-gray-900" style="margin-bottom:4px">${m.name}</h3>
      <p class="text-sm text-gray-600 flex items-center gap-1" style="margin-bottom:10px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">${ICON.mail} ${m.email}</p>
      <div style="margin-bottom:14px"><span class="badge ${roleBadge[m.role]||'badge-gray'}">${m.role}</span></div>
      <div style="padding-top:12px;border-top:1px solid var(--gray-200)" class="space-y-2">
        <div class="flex justify-between text-sm"><span class="text-gray-600">Projetos</span><span class="font-semibold">${m.projects}</span></div>
        <div class="flex justify-between text-sm"><span class="text-gray-600">Último acesso</span><span class="font-semibold">${m.lastActive}</span></div>
      </div>
      <button class="btn btn-outline w-full" style="justify-content:center;font-size:13px;margin-top:12px">Ver Perfil</button>
    </div>`).join('');
}

// ===================== TABS =====================
function switchDetailTab(tabId, btn) {
  document.querySelectorAll('#detail-tabs .tab-btn').forEach(b => b.classList.remove('active'));
  document.querySelectorAll('#page-project-detail .tab-content').forEach(t => t.classList.remove('active'));
  btn.classList.add('active');
  document.getElementById(`detail-tab-${tabId}`).classList.add('active');
}

function switchClientTab(tabId, btn) {
  document.querySelectorAll('.client-header ~ * .tabs .tab-btn').forEach(b => { b.className = 'tab-btn'; });
  document.querySelectorAll('[id^="client-tab-"]').forEach(t => t.classList.remove('active'));
  btn.classList.add('active-indigo');
  document.getElementById(`client-tab-${tabId}`).classList.add('active');
}

// ===================== REQ MODAL =====================
function openReqModal(pid, reqId) {
  editingReqId = reqId;
  currentProjectId = pid;
  document.getElementById('req-modal-title').textContent = reqId ? 'Editar Requisito' : 'Novo Requisito';
  document.getElementById('req-modal-btn-txt').textContent = reqId ? 'Salvar Alterações' : 'Criar Requisito';

  if (reqId) {
    const req = (detailRequirements[pid] || []).find(r => r.id === reqId);
    if (req) {
      document.getElementById('req-code').value         = req.code;
      document.getElementById('req-title-input').value  = req.title;
      document.getElementById('req-desc-input').value   = req.description;
      document.getElementById('req-type-input').value   = req.type;
      document.getElementById('req-priority-input').value = req.priority;
      document.getElementById('req-status-input').value = req.status;
    }
  } else {
    document.getElementById('req-code').value = '';
    document.getElementById('req-title-input').value = '';
    document.getElementById('req-desc-input').value = '';
    document.getElementById('req-type-input').value = 'Funcional';
    document.getElementById('req-priority-input').value = 'Média';
    document.getElementById('req-status-input').value = 'Pendente';
  }
  document.getElementById('req-modal').classList.remove('hidden');
}

function closeReqModal() {
  document.getElementById('req-modal').classList.add('hidden');
}

function saveRequirement() {
  const pid   = currentProjectId;
  const code  = document.getElementById('req-code').value.trim();
  const title = document.getElementById('req-title-input').value.trim();
  const desc  = document.getElementById('req-desc-input').value.trim();
  const type  = document.getElementById('req-type-input').value;
  const pri   = document.getElementById('req-priority-input').value;
  const stat  = document.getElementById('req-status-input').value;
  if (!code || !title || !desc) return;

  if (editingReqId) {
    const req = (detailRequirements[pid] || []).find(r => r.id === editingReqId);
    if (req) { req.code = code; req.title = title; req.description = desc; req.type = type; req.priority = pri; req.status = stat; }
  } else {
    detailRequirements[pid] = detailRequirements[pid] || [];
    detailRequirements[pid].push({ id: Date.now(), code, title, description: desc, type, priority: pri, status: stat });
  }
  closeReqModal();
  renderDetailReqs(detailRequirements[pid], pid);
  document.getElementById('detail-req-count').textContent = detailRequirements[pid].length;
}

// ===================== CLIENT RENDERS =====================
function renderClientRequirements() {
  const list = document.getElementById('client-req-list');
  list.innerHTML = clientRequirements.map(r => {
    const approvalLabel = r.clientApproval === 'approved' ? 'Aprovado por você' : r.clientApproval === 'rejected' ? 'Rejeitado por você' : 'Aguardando sua aprovação';
    const approvalBadge = r.clientApproval === 'approved' ? 'badge-green' : r.clientApproval === 'rejected' ? 'badge-red' : 'badge-yellow';
    return `
      <div class="card" id="client-req-${r.id}">
        <div class="flex items-start justify-between" style="margin-bottom:12px">
          <div>
            <div class="flex items-center gap-2" style="margin-bottom:8px">
              <span class="badge badge-slate font-mono">${r.code}</span>
              <span class="badge ${priorityBadge[r.priority]}">${r.priority}</span>
              <span class="badge ${approvalBadge}">${approvalLabel}</span>
            </div>
            <h3 class="font-bold text-gray-900" style="margin-bottom:4px">${r.title}</h3>
            <p class="text-gray-600 text-sm">${r.description}</p>
          </div>
        </div>
        ${r.clientApproval === 'pending' ? `
          <div class="flex gap-3 pt-3" style="border-top:1px solid var(--gray-200)">
            <button class="btn btn-green" onclick="clientApproveReq(${r.id},'approved')">${ICON.check} Aprovar</button>
            <button class="btn btn-red" onclick="clientApproveReq(${r.id},'rejected')">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>
              Recusar
            </button>
          </div>` : r.clientApproval === 'approved' ? `
          <div class="flex items-center gap-2 pt-3" style="border-top:1px solid var(--gray-200);color:var(--green-600)">
            ${ICON.check} <span class="font-semibold text-sm">Você aprovou este requisito</span>
          </div>` : `
          <div class="flex items-center gap-2 pt-3" style="border-top:1px solid var(--gray-200);color:var(--red-700)">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>
            <span class="font-semibold text-sm">Você rejeitou este requisito</span>
          </div>`}
      </div>`}).join('');

  updateClientApprovedStats();
}

function clientApproveReq(reqId, decision) {
  const req = clientRequirements.find(r => r.id === reqId);
  if (req) { req.clientApproval = decision; }
  renderClientRequirements();
  updateClientPendingBadge();
}

function updateClientApprovedStats() {
  const approved = clientRequirements.filter(r => r.clientApproval === 'approved').length;
  const pending  = clientRequirements.filter(r => r.clientApproval === 'pending').length;
  const rejected = clientRequirements.filter(r => r.clientApproval === 'rejected').length;
  document.getElementById('ov-approved').textContent = approved;
  document.getElementById('ov-pending').textContent  = pending;
  document.getElementById('ov-rejected').textContent = rejected;
}

function updateClientPendingBadge() {
  const pending = clientRequirements.filter(r => r.clientApproval === 'pending').length;
  const badge = document.getElementById('client-pending-badge');
  if (pending > 0) { badge.textContent = pending + ' pendentes'; badge.style.display = ''; }
  else { badge.style.display = 'none'; }
}

function renderClientDocs(pid) {
  const docs = DOCS_DATA[pid] || [];
  document.getElementById('client-docs-grid').innerHTML = docs.map(d => `
    <div class="card card-hover">
      <div class="flex items-start gap-3" style="margin-bottom:14px">
        <div style="width:48px;height:48px;border-radius:8px;background:var(--indigo-100);display:flex;align-items:center;justify-content:center;flex-shrink:0">${ICON.file.replace('stroke="currentColor"','stroke="var(--indigo-600)"')}</div>
        <div><h3 class="font-bold text-gray-900">${d.name}</h3><p class="text-sm text-gray-600">${d.type} · v${d.version}</p></div>
      </div>
      <div class="flex justify-between items-center pt-3" style="border-top:1px solid var(--gray-200)">
        <span class="text-sm text-gray-600 flex items-center gap-1">${ICON.clock} ${d.lastEdit}</span>
        <button class="btn btn-indigo" style="font-size:12px;padding:7px 14px">${ICON.download} Baixar</button>
      </div>
    </div>`).join('');
}

function renderClientDiagrams(pid) {
  const diag = DIAGRAMS_DATA[pid] || [];
  document.getElementById('client-diag-grid').innerHTML = diag.map(d => `
    <div class="card" style="padding:0;overflow:hidden">
      <div class="diagram-thumb" style="background:${d.bg}">${ICON.net.replace('16','40')}</div>
      <div style="padding:14px">
        <h3 class="font-bold text-gray-900" style="margin-bottom:6px">${d.title}</h3>
        <p class="text-sm text-gray-600" style="margin-bottom:8px">${d.type}</p>
        <div class="flex justify-between text-xs text-gray-600">
          <span class="flex items-center gap-1">${ICON.clock} ${d.lastEdit}</span>
        </div>
      </div>
    </div>`).join('');
}

function renderClientComments() {
  renderCommentList('client-comments-list', clientComments);
  document.getElementById('client-comments-count').textContent = clientComments.length;
}

function sendClientComment() {
  const inp = document.getElementById('client-comment-input');
  const txt = inp.value.trim();
  if (!txt) return;
  clientComments.push({ id: Date.now(), author: currentUser?.name || 'Cliente', text: txt, date: new Date().toLocaleString('pt-BR'), isClient: true });
  renderClientComments();
  inp.value = '';
}

// ===================== AUTO-LOGIN (from localStorage) =====================
function init() {
  const stored = localStorage.getItem('cobyte_user');
  const page = window.location.pathname.split('/').pop();

  // Pages that require authentication
  const authRequired = ['dashboard.html', 'client.html'];
  // Auth-only pages (redirect away if already logged in)
  const authOnly = ['login.html', 'register.html', ''];

  if (stored) {
    try {
      const user = JSON.parse(stored);
      currentUser = user;

      if (authOnly.includes(page)) {
        // Already logged in — go to correct page
        if (user.role === 'client') { window.location.href = 'client.html'; return; }
        else { window.location.href = 'dashboard.html'; return; }
      }

      if (page === 'dashboard.html') {
        if (user.role === 'client') { window.location.href = 'client.html'; return; }
        // Init dashboard UI
        document.getElementById('dashboard-section').classList.remove('hidden');
        document.getElementById('topbar-username').textContent = user.name;
        document.getElementById('topbar-role').textContent = user.role === 'admin' ? 'Administrador' : 'Funcionário';
        document.getElementById('topbar-avatar').textContent = user.name.charAt(0);
        navigate('dashboard');
        return;
      }

      if (page === 'client.html') {
        if (user.role !== 'client') { window.location.href = 'dashboard.html'; return; }
        // Init client UI (call inline)
        const el = document.getElementById('client-section');
        if (el) {
          el.classList.remove('hidden');
          document.getElementById('client-name').textContent = user.name;
          document.getElementById('client-avatar').textContent = user.name.charAt(0);
          const pid = user.clientProjectId || '1';
          const proj = PROJECTS.find(p => p.id === pid) || PROJECTS[0];
          document.getElementById('client-proj-name').textContent    = proj.name;
          document.getElementById('client-proj-desc').textContent    = proj.description;
          document.getElementById('client-start').textContent        = proj.startDate;
          document.getElementById('client-deadline').textContent     = proj.deadline;
          document.getElementById('client-progress-bar').style.width = proj.progress + '%';
          document.getElementById('client-progress').textContent     = proj.progress + '%';
          clientRequirements = JSON.parse(JSON.stringify(REQS_DATA[pid] || []));
          clientComments     = JSON.parse(JSON.stringify(COMMENTS_DATA[pid] || []));
          document.getElementById('client-req-count').textContent = clientRequirements.length;
          renderClientRequirements();
          renderClientDocs(pid);
          renderClientDiagrams(pid);
          renderClientComments();
          updateClientPendingBadge();
        }
        return;
      }

    } catch(e) { localStorage.removeItem('cobyte_user'); }
  }

  // Not logged in
  if (authRequired.includes(page)) {
    window.location.href = 'login.html';
    return;
  }

  // Show login form (on login.html)
  const authSection = document.getElementById('auth-section');
  if (authSection) authSection.classList.remove('hidden');
}

init();


