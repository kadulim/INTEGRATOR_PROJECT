// ── CoByte Login — High Fidelity Interaction Engine ──────────────────────

document.addEventListener('DOMContentLoaded', () => {

    // 1. Cinematic Background Interactions
    const orbs = document.querySelectorAll('.pulse-orb');
    
    // Subtle Mouse Parallax for Orbs
    document.addEventListener('mousemove', (e) => {
        const x = (e.clientX / window.innerWidth) - 0.5;
        const y = (e.clientY / window.innerHeight) - 0.5;
        
        orbs.forEach((orb, i) => {
            const factor = (i + 1) * 20;
            orb.style.transform = `translate(${x * factor}px, ${y * factor}px) scale(${1 + (Math.abs(x) * 0.1)})`;
        });
    });

    // 2. Energy Lines Flow Logic
    const energyPaths = document.querySelectorAll('.energy-path');
    energyPaths.forEach((path, i) => {
        const length = path.getTotalLength();
        path.style.strokeDasharray = length;
        path.style.strokeDashoffset = length;
        
        path.animate([
            { strokeDashoffset: length },
            { strokeDashoffset: -length }
        ], {
            duration: 15000 + (i * 5000),
            iterations: Infinity,
            easing: 'linear'
        });
    });

    // 3. Password Visibility Toggle
    window.togglePassword = function() {
        const field = document.getElementById('auth-pw');
        const icon = document.querySelector('.pw-toggle svg');
        if (field.type === 'password') {
            field.type = 'text';
            icon.style.color = 'var(--accent-pink)';
        } else {
            field.type = 'password';
            icon.style.color = 'var(--text-dim)';
        }
    };

    // 4. Advanced Reveal System
    const reveals = document.querySelectorAll('.reveal');
    reveals.forEach((el, index) => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(24px) scale(0.98)';
        el.style.filter = 'blur(10px)';
        el.style.transition = 'all 1s cubic-bezier(0.2, 1, 0.2, 1)';
        
        setTimeout(() => {
            el.style.opacity = '1';
            el.style.transform = 'translateY(0) scale(1)';
            el.style.filter = 'blur(0)';
        }, (index * 100));
    });

    // 5. Magnetic Button Effect
    const submitBtn = document.querySelector('.auth-submit');
    if (submitBtn) {
        submitBtn.addEventListener('mousemove', (e) => {
            const rect = submitBtn.getBoundingClientRect();
            const x = e.clientX - rect.left - rect.width / 2;
            const y = e.clientY - rect.top - rect.height / 2;
            submitBtn.style.transform = `translate(${x * 0.1}px, ${y * 0.2}px) scale(1.02)`;
        });
        submitBtn.addEventListener('mouseleave', () => {
            submitBtn.style.transform = `translate(0, 0) scale(1)`;
        });
    }

    // 6. Theme Toggling Logic
    window.setTheme = function(mode) {
        const body = document.body;
        const lightBtn = document.getElementById('light-theme-btn');
        const darkBtn = document.getElementById('dark-theme-btn');

        if (mode === 'light') {
            body.classList.add('light-mode');
            lightBtn.classList.add('active');
            darkBtn.classList.remove('active');
            localStorage.setItem('cobyte-theme', 'light');
        } else {
            body.classList.remove('light-mode');
            darkBtn.classList.add('active');
            lightBtn.classList.remove('active');
            localStorage.setItem('cobyte-theme', 'dark');
        }
    };

    // Persistence Check
    const savedTheme = localStorage.getItem('cobyte-theme');
    if (savedTheme === 'light') setTheme('light');

});
