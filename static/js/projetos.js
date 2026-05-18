function onSearch(val) {
  const query = val.toLowerCase();
  const cards = document.querySelectorAll('.proj-card');
  const rows = document.querySelectorAll('.data-table tbody tr');

  // Filtrar Cards
  cards.forEach(card => {
    const name = card.querySelector('.pc-name').textContent.toLowerCase();
    const client = card.querySelector('.pc-client').textContent.toLowerCase();
    const matches = name.includes(query) || client.includes(query);
    card.style.display = matches ? 'flex' : 'none';
  });

  // Filtrar Tabela
  rows.forEach(row => {
    const text = row.textContent.toLowerCase();
    row.style.display = text.includes(query) ? '' : 'none';
  });
}

function onFilter(status) {
  const cards = document.querySelectorAll('.proj-card');
  const rows = document.querySelectorAll('.data-table tbody tr');

  cards.forEach(card => {
    const cardStatus = card.getAttribute('data-status');
    const matches = status === 'Todos' || cardStatus === status;
    card.style.display = matches ? 'flex' : 'none';
  });

  rows.forEach(row => {
    const rowStatus = row.getAttribute('data-status');
    if (rowStatus) {
      const matches = status === 'Todos' || rowStatus === status;
      row.style.display = matches ? '' : 'none';
    }
  });
}

function openProject(id) {
  // Por enquanto apenas redireciona ou abre um detalhe fictício
  window.location.href = `/admin/projeto-detalhe?id=${id}`;
}
