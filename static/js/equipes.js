function onSearch(val) {
  const query = val.toLowerCase();
  const cards = document.querySelectorAll('.member-card');

  cards.forEach(card => {
    const name = card.querySelector('.member-name').textContent.toLowerCase();
    const email = card.querySelector('.member-email').textContent.toLowerCase();
    const role = card.querySelector('.member-role').textContent.toLowerCase();
    
    // Também buscar nas skills
    const skills = Array.from(card.querySelectorAll('.skill-tag')).map(s => s.textContent.toLowerCase()).join(' ');

    const matches = name.includes(query) || email.includes(query) || role.includes(query) || skills.includes(query);
    card.style.display = matches ? 'flex' : 'none';
  });
}

function onFilter(val) {
  // O filtro atual na UI tem 'Disponível' e 'Em projeto'
  // No momento as badges estão fixas como 'Ativo'
  // Mas vamos implementar a lógica básica para o futuro
  const cards = document.querySelectorAll('.member-card');

  cards.forEach(card => {
    if (val === 'Todos') {
      card.style.display = 'flex';
      return;
    }
    
    // Busca pela badge de status
    const status = card.querySelector('.badge').textContent.trim();
    card.style.display = (status === val) ? 'flex' : 'none';
  });
}
