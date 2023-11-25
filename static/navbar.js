const doc = window.parent.document;

// wait for DOM to load
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM loaded');

    // Get all iframes
    const iframes = doc.querySelectorAll('iframe');

    console.log(iframes);

    // Set allow-top-navigation to all iframes
    iframes.forEach((iframe) => {
        iframe.setAttribute('sandbox', 'allow-top-navigation');
    });

    initNavbar();
});

const initNavbar = () => {
    // Check if the navbar is already loaded
    if (doc.getElementById('navbar-style')) {
        // Delete the style tag
        doc.getElementById('navbar-style').remove();
    }

    const navbarStyleTag = doc.createElement('style');

    fetch('/app/static/navbar.css')
        .then((response) => response.text())
        .then((data) => {
            navbarStyleTag.id = 'navbar-style';
            navbarStyleTag.innerHTML = data;
            doc.head.appendChild(navbarStyleTag);
            const navbar = doc.getElementById('navbar');

            // Remove the style attribute
            navbar.removeAttribute('style');

            // Get a tag elements in #navbar#navbar-items
            const navbarItems = doc.querySelectorAll('.menu-item');

            // Add event listener to each a tag
            navbarItems.forEach((navbarItem) => {
                // Get current page url
                const pathname = window.parent.location.pathname;

                // Check if pathname is equal to href
                if (pathname === navbarItem.getAttribute('href')) {
                    // Add active class
                    navbarItem.classList.add('active');
                } else {
                    // Remove active class
                    navbarItem.classList.remove('active');
                }
            });
        });
}
