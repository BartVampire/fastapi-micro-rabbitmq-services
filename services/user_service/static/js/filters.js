
document.addEventListener("DOMContentLoaded", function() {
    var grid = document.querySelector('.grid');
    var iso = new Isotope(grid, {
        itemSelector: '.all',
        layoutMode: 'fitRows'
    });

    var filters = document.querySelectorAll('.filters_menu li');
    filters.forEach(function(filter) {
        filter.addEventListener('click', function() {
            filters.forEach(f => f.classList.remove('active'));
            this.classList.add('active');
            var filterValue = this.getAttribute('data-filter');
            iso.arrange({ filter: filterValue });
        });
    });
});
