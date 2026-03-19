// Juraj Orwell — Blog main script
// Loads posts from posts.json and renders them on the index page

const POSTS_PER_PAGE = 10;
let allPosts = [];
let displayedCount = 0;

async function loadPosts() {
    try {
        const response = await fetch('posts.json');
        if (!response.ok) throw new Error('Nepodarilo sa načítať články.');
        allPosts = await response.json();
        // Sort by date, newest first
        allPosts.sort((a, b) => new Date(b.date) - new Date(a.date));
        displayPosts();
    } catch (err) {
        const container = document.getElementById('posts');
        if (container) {
            container.innerHTML = '<p style="color: #888; text-align: center; padding: 2rem 0;">Zatiaľ neboli publikované žiadne články.</p>';
        }
    }
}

function displayPosts() {
    const container = document.getElementById('posts');
    if (!container) return;

    const end = Math.min(displayedCount + POSTS_PER_PAGE, allPosts.length);

    for (let i = displayedCount; i < end; i++) {
        const post = allPosts[i];
        const card = document.createElement('div');
        card.className = 'post-card';

        const tagsHTML = (post.tags || [])
            .map(tag => `<span class="tag">${tag}</span>`)
            .join('');

        card.innerHTML = `
            <div class="post-card-meta">${formatDate(post.date)}</div>
            <h2><a href="posts/${post.slug}.html">${post.title}</a></h2>
            <p class="post-card-excerpt">${post.excerpt}</p>
            <div class="post-card-tags">${tagsHTML}</div>
        `;
        container.appendChild(card);
    }

    displayedCount = end;

    // Show/hide load more button
    const loadMoreBtn = document.getElementById('load-more');
    if (loadMoreBtn) {
        loadMoreBtn.style.display = displayedCount < allPosts.length ? 'block' : 'none';
    }
}

function loadMore() {
    displayPosts();
}

function formatDate(dateStr) {
    const months = [
        'januára', 'februára', 'marca', 'apríla', 'mája', 'júna',
        'júla', 'augusta', 'septembra', 'októbra', 'novembra', 'decembra'
    ];
    const d = new Date(dateStr);
    return `${d.getDate()}. ${months[d.getMonth()]} ${d.getFullYear()}`;
}

// Initialize
document.addEventListener('DOMContentLoaded', loadPosts);
