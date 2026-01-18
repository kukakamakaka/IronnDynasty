/**
 * loader.js
 * Управляет навигационным шариком и открытием сайта.
 */

function initPremiumNav() {
    const blob = document.querySelector('.nav-blob');
    const items = document.querySelectorAll('.nav-item');
    if (!blob || items.length === 0) return;

    const currentPath = window.location.pathname.replace(/\/$/, "") || "/";

    items.forEach(item => {
        item.classList.remove('is-active');
        const itemPath = item.getAttribute('data-path').replace(/\/$/, "") || "/";
        
        // Проверка активности ссылки
        if ((itemPath === "/" && currentPath === "/") || (itemPath !== "/" && currentPath.startsWith(itemPath))) {
            item.classList.add('is-active');
            const x = item.offsetLeft + (item.offsetWidth / 2) - (blob.offsetWidth / 2);
            blob.style.transform = `translateX(${x}px)`;
            blob.style.opacity = '1';
        }
    });
}

function revealSite() {
    const preloader = document.getElementById('preloader');
    if (preloader) {
        // Улетаем вверх согласно твоему CSS (.preloader-hidden) [cite: 2026-01-13]
        preloader.classList.add('preloader-hidden');
        
        // Сразу разрешаем клики сквозь исчезающий блок [cite: 2026-01-13]
        preloader.style.pointerEvents = 'none';

        setTimeout(() => {
            preloader.style.display = 'none';
            // Перезагружаем AOS, чтобы блоки в Hero не слипались [cite: 2026-01-13]
            if (typeof AOS !== 'undefined') AOS.refresh();
        }, 1100);
    }
}

// Запуск при полной готовности страницы
window.addEventListener('load', () => {
    const preloader = document.getElementById('preloader');

    // Инициализация шарика, если функция существует
    if (typeof initPremiumNav === 'function') initPremiumNav();

    if (preloader) {
        // Запускаем улет вверх (класс из твоего CSS) [cite: 2026-01-13]
        preloader.classList.add('preloader-hidden');

        // Ключевое: снимаем "невидимую стену" [cite: 2026-01-13]
        preloader.style.pointerEvents = 'none';

        setTimeout(() => {
            preloader.style.display = 'none';
            // Оживляем AOS анимации на новой странице [cite: 2026-01-10]
            if (typeof AOS !== 'undefined') AOS.refresh();
        }, 1100);
    }
});

window.addEventListener('resize', initPremiumNav);