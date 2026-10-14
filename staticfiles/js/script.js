document.addEventListener('DOMContentLoaded', function () {
    const nav = document.querySelector('nav');

    if (!nav) return;

    const authPathPattern = /\/(accounts\/)?(login|register)\/?$/;
    const isAuthPage = authPathPattern.test(window.location.pathname);

    if (!isAuthPage) {
        nav.classList.remove('nav-hidden');
        return;
    }

    let lastScrollY = window.scrollY;

    const handleNavbarScroll = () => {
        const currentScrollY = window.scrollY;

        if (currentScrollY > lastScrollY && currentScrollY > 80) {
            nav.classList.add('nav-hidden');
        } else {
            nav.classList.remove('nav-hidden');
        }

        lastScrollY = currentScrollY;
    };

    window.addEventListener('scroll', handleNavbarScroll, { passive: true });
    handleNavbarScroll();
});
