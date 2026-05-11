// ── Login Page ────────────────────────────────────────────

document.addEventListener('DOMContentLoaded', () => {
  const loginForm = document.querySelector('form');
  if (loginForm) {
    loginForm.addEventListener('submit', (e) => {
      const btn = document.getElementById('submit-btn');
      if (btn) {
        btn.classList.add('loading');
        btn.textContent = 'Entrando…';
      }
      // Deixa o form submeter nativamente para o Flask
    });
  }
});

function quickLogin(email) {
  document.getElementById('identificador').value = email;
  document.getElementById('password').value = '123456';
  const errEl = document.getElementById('error-msg');
  if (errEl) errEl.style.display = 'none';
  
  // Auto submit the form
  const loginForm = document.querySelector('form');
  if (loginForm) {
    loginForm.submit();
  }
}

function togglePassword() {
  const inp = document.getElementById('password');
  const icon = document.getElementById('eye-icon');
  if (inp.type === 'password') {
    inp.type = 'text';
    icon.innerHTML = '<path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/><line x1="1" y1="1" x2="23" y2="23"/>';
  } else {
    inp.type = 'password';
    icon.innerHTML = '<path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/>';
  }
}
