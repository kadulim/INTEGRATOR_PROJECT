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
  const cards = document.querySelectorAll('.member-card');

  cards.forEach(card => {
    const cardStatus = card.getAttribute('data-status');
    const matches = val === 'Todos' || cardStatus === val;
    card.style.display = matches ? 'flex' : 'none';
  });
}
