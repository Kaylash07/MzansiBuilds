// MzansiBuilds - Main JavaScript

// Restore scroll position after refresh
(function () {
    var savedPos = sessionStorage.getItem('scrollPos');
    if (savedPos !== null) {
        window.scrollTo(0, parseInt(savedPos, 10));
        sessionStorage.removeItem('scrollPos');
    }
    window.addEventListener('beforeunload', function () {
        sessionStorage.setItem('scrollPos', window.scrollY);
    });
})();

document.addEventListener('DOMContentLoaded', function () {
    // Mobile nav toggle
    const navToggle = document.getElementById('navToggle');
    const navLinks = document.getElementById('navLinks');

    if (navToggle && navLinks) {
        navToggle.addEventListener('click', function () {
            navLinks.classList.toggle('open');
        });

        // Close nav when clicking outside
        document.addEventListener('click', function (e) {
            if (!navToggle.contains(e.target) && !navLinks.contains(e.target)) {
                navLinks.classList.remove('open');
            }
        });
    }

    // Auto-dismiss flash messages after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            alert.style.opacity = '0';
            alert.style.transform = 'translateY(-10px)';
            alert.style.transition = '0.3s ease';
            setTimeout(function () {
                alert.remove();
            }, 300);
        }, 5000);
    });

    // Add animation on scroll for project cards
    const observer = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, { threshold: 0.1 });

    document.querySelectorAll('.card').forEach(function (card) {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        card.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
        observer.observe(card);
    });
});
