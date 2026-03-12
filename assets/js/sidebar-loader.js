/**
 * Sidebar Loader
 * Loads and injects the shared sidebar navigation into pages
 * Works with static GitHub Pages
 */

(function() {
    'use strict';

    // Get current page identifier from URL
    function getCurrentPage() {
        const path = window.location.pathname;
        const filename = path.split('/').pop() || 'index.html';
        const page = filename.replace('.html', '');
        
        // Handle special cases
        if (path.includes('/blog/posts/')) return 'blog';
        if (path.includes('/documents/posts/')) return 'documents';
        
        return page || 'index';
    }

    // Load sidebar HTML and inject it
    function loadSidebar() {
        const sidebarPath = '/assets/includes/sidebar.html';
        const desktopPlaceholder = document.getElementById('sidebar-desktop');
        const mobilePlaceholder = document.getElementById('sidebar-mobile');
        
        if (!desktopPlaceholder && !mobilePlaceholder) {
            console.warn('Sidebar placeholders not found');
            return;
        }

        fetch(sidebarPath)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Failed to load sidebar: ${response.status}`);
                }
                return response.text();
            })
            .then(html => {
                // Create a temporary container to parse the HTML
                const temp = document.createElement('div');
                temp.innerHTML = html;
                
                // Extract desktop sidebar (first div with desktop-sidebar class)
                const desktopSidebar = temp.querySelector('.desktop-sidebar');
                // Extract mobile sidebar (div with lg:hidden class)
                const mobileSidebar = temp.querySelector('.lg\\:hidden');
                
                // Inject desktop sidebar
                if (desktopPlaceholder && desktopSidebar) {
                    desktopPlaceholder.innerHTML = desktopSidebar.innerHTML;
                }
                
                // Inject mobile sidebar
                if (mobilePlaceholder && mobileSidebar) {
                    mobilePlaceholder.innerHTML = mobileSidebar.innerHTML;
                }
                
                // Fix relative paths and highlight active page
                setTimeout(() => {
                    fixSidebarPaths();
                    highlightActivePage();
                }, 50);
            })
            .catch(error => {
                console.error('Error loading sidebar:', error);
                // Fallback: show error message or keep existing sidebar
            });
    }

    // Highlight the active page in the sidebar
    function highlightActivePage() {
        const currentPage = getCurrentPage();
        const sidebarLinks = document.querySelectorAll('.sidebar-link');
        
        sidebarLinks.forEach(link => {
            const linkPage = link.getAttribute('data-page');
            if (linkPage === currentPage) {
                // Update classes to show active state
                link.classList.remove('text-gray-300', 'hover:text-white', 'hover:bg-gray-700');
                link.classList.add('text-blue-300', 'bg-gray-700');
            }
        });
    }

    // Fix relative paths in sidebar links based on current page depth
    function fixSidebarPaths() {
        const sidebarLinks = document.querySelectorAll('.sidebar-link');
        const path = window.location.pathname;
        
        // Calculate depth: count directories (excluding root and filename)
        // e.g., /blog/posts/article.html = depth 2, /index.html = depth 0
        const pathParts = path.split('/').filter(p => p);
        const filename = pathParts[pathParts.length - 1] || '';
        const currentDepth = pathParts.length - (filename.endsWith('.html') ? 1 : 0) - 1;
        
        sidebarLinks.forEach(link => {
            const href = link.getAttribute('href');
            if (href && !href.startsWith('http') && !href.startsWith('/')) {
                // Calculate relative path based on depth
                const prefix = currentDepth > 0 ? '../'.repeat(currentDepth) : '';
                link.setAttribute('href', prefix + href);
            }
        });
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            loadSidebar();
        });
    } else {
        loadSidebar();
    }
})();

