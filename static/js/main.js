/* ScoutBet — main.js */

// ── Auto-dismiss flash messages ──────────────────────
(function () {
    const alerts = document.querySelectorAll('[data-auto-dismiss]');
    alerts.forEach(function (el) {
        const delay = parseInt(el.dataset.autoDismiss || '4000', 10);
        setTimeout(function () {
            el.style.transition = 'opacity 0.4s, transform 0.4s';
            el.style.opacity = '0';
            el.style.transform = 'translateY(-8px)';
            setTimeout(function () { el.remove(); }, 400);
        }, delay);
    });
})();

// ── Sidebar mobile toggle ────────────────────────────
(function () {
    const toggleBtn = document.getElementById('sidebar-toggle');
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebar-overlay');

    if (!toggleBtn || !sidebar) return;

    function openSidebar() {
        sidebar.classList.remove('-translate-x-full');
        overlay && overlay.classList.remove('hidden');
    }

    function closeSidebar() {
        sidebar.classList.add('-translate-x-full');
        overlay && overlay.classList.add('hidden');
    }

    toggleBtn.addEventListener('click', function () {
        const isOpen = !sidebar.classList.contains('-translate-x-full');
        isOpen ? closeSidebar() : openSidebar();
    });

    overlay && overlay.addEventListener('click', closeSidebar);
})();

// ── HTMX: show table loading skeleton on filter ──────
document.addEventListener('htmx:beforeRequest', function (evt) {
    const target = evt.detail.target;
    if (target && target.id === 'fixture-table-body') {
        target.innerHTML = Array(5).fill(
            '<tr class="animate-pulse">' +
            Array(9).fill('<td class="px-4 py-3"><div class="h-4 bg-slate-800 rounded w-3/4"></div></td>').join('') +
            '</tr>'
        ).join('');
    }
});

// ── Tooltip init (data-tooltip attribute) ───────────
(function () {
    const els = document.querySelectorAll('[data-tooltip]');
    els.forEach(function (el) {
        const tip = document.createElement('div');
        tip.className = 'absolute z-50 px-2 py-1 text-xs text-white bg-slate-700 rounded shadow-lg pointer-events-none hidden';
        tip.textContent = el.dataset.tooltip;
        document.body.appendChild(tip);

        el.addEventListener('mouseenter', function (e) {
            const rect = el.getBoundingClientRect();
            tip.style.left = rect.left + window.scrollX + 'px';
            tip.style.top = (rect.top + window.scrollY - 30) + 'px';
            tip.classList.remove('hidden');
        });

        el.addEventListener('mouseleave', function () {
            tip.classList.add('hidden');
        });
    });
})();
