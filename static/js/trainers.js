document.addEventListener('DOMContentLoaded', () => {
    const cards = document.querySelectorAll('.card');
    const header = document.querySelector('.hero-header');
    const footer = document.querySelector('.action-footer');

    // --- 1. АНИМАЦИЯ ПОЯВЛЕНИЯ (Intersection Observer) ---
    const revealObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('active');
                revealObserver.unobserve(entry.target);
            }
        });
    }, { threshold: 0.15 });

    [header, footer, ...cards].forEach(el => {
        if (el) {
            el.classList.add('reveal-ov');
            revealObserver.observe(el);
        }
    });

    // --- 2. 3D НАКЛОН (Только для Desktop > 600px) ---
    if (window.innerWidth > 600) {
        cards.forEach(card => {
            card.addEventListener('mousemove', (e) => {
                const rect = card.getBoundingClientRect();
                const x = e.clientX - rect.left;
                const y = e.clientY - rect.top;
                
                const centerX = rect.width / 2;
                const centerY = rect.height / 2;
                
                const rotateX = (centerY - y) / 15;
                const rotateY = (x - centerX) / 15;

                card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg)`;
            });

            card.addEventListener('mouseleave', () => {
                card.style.transform = `perspective(1000px) rotateX(0deg) rotateY(0deg)`;
            });
        });
    }

    // --- 3. СИНХРОНИЗАЦИЯ ТЕМЫ (MutationObserver) ---
    // Следит за классом light-theme на теге body
    const themeObserver = new MutationObserver(() => {
        const isLight = document.body.classList.contains('light-theme');
        console.log(`[Trainers] Theme mode: ${isLight ? 'Light' : 'Dark'}`);
    });

    themeObserver.observe(document.body, { attributes: true, attributeFilter: ['class'] });
});

