// Dark mode toggle
document.addEventListener('DOMContentLoaded', function() {
    const darkModeToggle = document.getElementById('darkModeToggle');
    const darkModeStylesheet = document.getElementById('dark-mode-stylesheet');

    if (darkModeToggle) {
        darkModeToggle.addEventListener('click', function() {
            const isDark = document.body.getAttribute('data-bs-theme') === 'dark';

            if (isDark) {
                document.body.setAttribute('data-bs-theme', 'light');
                darkModeToggle.innerHTML = '<i class="fas fa-moon"></i> الوضع الليلي';
                localStorage.setItem('theme', 'light');
            } else {
                document.body.setAttribute('data-bs-theme', 'dark');
                darkModeToggle.innerHTML = '<i class="fas fa-sun"></i> الوضع النهاري';
                localStorage.setItem('theme', 'dark');
            }
        });

        // Load saved theme
        const savedTheme = localStorage.getItem('theme');
        if (savedTheme === 'dark') {
            document.body.setAttribute('data-bs-theme', 'dark');
            darkModeToggle.innerHTML = '<i class="fas fa-sun"></i> الوضع النهاري';
        }
    }
});

// Auto-hide alerts after 5 seconds
setTimeout(function() {
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(function(alert) {
        alert.style.transition = 'opacity 0.5s';
        alert.style.opacity = '0';
        setTimeout(function() {
            alert.remove();
        }, 500);
    });
}, 5000);