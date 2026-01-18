/**
 * Оптимизированная анимация для секции About
 */
document.addEventListener('DOMContentLoaded', () => {
    const aboutSection = document.querySelector('.body-empire-section');
    const content = document.querySelector('.empire-content');
    const grid = document.querySelector('.grid-overlay');

    if (!aboutSection || !content) return;

    // --- 1. ЛОГИКА ВХОДА И ВЫХОДА (Intersection Observer) ---
    const observerOptions = {
        threshold: 0.2, // Анимация сработает, когда 20% блока в зоне видимости
        rootMargin: "0px 0px -10% 0px" // Небольшой отступ снизу
    };

    const scrollObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                // Вход: плавно проявляем
                content.classList.add('is-visible');
                if (grid) grid.style.opacity = "0.05";
            } else {
                // Выход: скрываем обратно (эффект исчезновения при уходе)
                content.classList.remove('is-visible');
                if (grid) grid.style.opacity = "0";
            }
        });
    }, observerOptions);

    scrollObserver.observe(aboutSection);

    // --- 2. ПАРАЛЛАКС СЕТКИ ПРИ ДВИЖЕНИИ МЫШИ ---
    document.addEventListener('mousemove', (e) => {
        if (!grid || !content.classList.contains('is-visible')) return;

        // Рассчитываем положение курсора относительно центра
        const x = (e.clientX - window.innerWidth / 2) * 0.015;
        const y = (e.clientY - window.innerHeight / 2) * 0.015;

        // Плавно двигаем сетку
        grid.style.transform = `translate(${x}px, ${y}px)`;
    });

    // --- 3. СИНХРОНИЗАЦИЯ С ТЕМОЙ (MutationObserver) ---
    const themeObserver = new MutationObserver(() => {
        const isLight = document.body.classList.contains('light-theme');
        console.log(`[About] Syncing theme: ${isLight ? 'Light' : 'Dark'}`);
    });

    themeObserver.observe(document.body, { attributes: true, attributeFilter: ['class'] });
});
