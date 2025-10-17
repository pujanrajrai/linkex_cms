// Select elements
const hamMenu = document.querySelector(".ham-menu");
const sidebar = document.querySelector(".sidebar");
const navbar = document.querySelector(".navbar");
const content = document.querySelector(".content");
const menuItems = document.querySelectorAll(".menu-item");
const menuLinks = document.querySelectorAll(".menu-link");

// Toggle sidebar expansion
hamMenu.addEventListener("click", () => {
    sidebar.classList.toggle("active");
    navbar.classList.toggle("active");
    content.classList.toggle("active");
    
    // Close all expanded accordion menus when collapsing sidebar
    menuItems.forEach(item => {
        item.classList.removeclass("active");
    });
});

// Handle menu item interactions
menuLinks.forEach(link => {
    link.addEventListener("click", (e) => {
        const menuItem = link.parentElement;
        const hasDropdown = menuItem.querySelector(".dropdown-content");
        
        if (hasDropdown) {
            // Only prevent default if we're handling an accordion
            if (sidebar.classList.contains("active")) {
                e.preventDefault(); // Prevent navigation for accordion mode
                
                // Close all other active dropdowns
                menuItems.forEach(item => {
                    if (item !== menuItem) {
                        item.classList.remove("active");
                    }
                });
                
                // Toggle the current dropdown
                menuItem.classList.toggle("active");
            }
        }
    });
});

// Close dropdowns when clicking outside
document.addEventListener("click", (e) => {
    // Check if click is outside the sidebar and the menu toggle
    if (!sidebar.contains(e.target) && !hamMenu.contains(e.target)) {
        menuItems.forEach(item => {
            item.classList.remove("active");
        });
    }
});

// Handle touch events for mobile devices
if ('ontouchstart' in window) {
    menuItems.forEach(item => {
        // For collapsed sidebar on touch devices
        item.addEventListener("touchstart", (e) => {
            if (!sidebar.classList.contains("active")) {
                // Only handle touch for collapsed sidebar
                e.stopPropagation();
                
                // Close all other dropdowns
                menuItems.forEach(otherItem => {
                    if (otherItem !== item) {
                        otherItem.classList.remove("touch-hover");
                    }
                });
                
                // Toggle hover class for this item
                item.classList.toggle("touch-hover");
            }
        });
    });
    
    // Close all touch hovers when touching outside
    document.addEventListener("touchstart", (e) => {
        if (!sidebar.contains(e.target)) {
            menuItems.forEach(item => {
                item.classList.remove("touch-hover");
            });
        }
    });
}