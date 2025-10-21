document.querySelector('.search-box').addEventListener('input', (e) => {
    // Filter campaigns based on search input
    const searchTerm = e.target.value.toLowerCase();
    document.querySelectorAll('.campaign-card').forEach(card => {
        const title = card.querySelector('.campaign-title').textContent.toLowerCase();
        card.style.display = title.includes(searchTerm) ? '' : 'none';
});
});
document.querySelector('.filter-dropdown').addEventListener('change', (e) => {
    const selectedCategory = e.target.value.toLowerCase();
    document.querySelectorAll('.campaign-card').forEach(card => {
        const category = card.getAttribute('data-category').toLowerCase();
        card.style.display = (selectedCategory === 'all' || category === selectedCategory) ? '' :
}); 
});

<!-- In all forms -->
{% csrf_token %}