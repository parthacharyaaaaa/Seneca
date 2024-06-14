document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('dropdownMenuButton').addEventListener('click', function() {
        var filterMenu = document.getElementById('filterMenu');
        filterMenu.classList.toggle('active');
    });

    // Close the dropdown menu if clicked outside
    document.addEventListener('click', function(e) {
        var filterMenu = document.getElementById('filterMenu');
        if (!e.target.closest('.filter-dropdown')) {
            filterMenu.classList.remove('active');
        }
    });
});