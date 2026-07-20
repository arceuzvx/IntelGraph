document.addEventListener('DOMContentLoaded', () => {
    const platformFilter = document.getElementById('platform-filter');
    const tacticFilter = document.getElementById('tactic-filter');
    const clearFiltersBtn = document.getElementById('clear-filters-btn');
    const searchInput = document.getElementById('search-input');
    const searchBtn = document.getElementById('search-button');
    const resultsContainer = document.getElementById('results-container');
    const statusContainer = document.getElementById('status-container');

    // Auto-focus search
    searchInput.focus();

    // Fetch and populate filters (loaded only once)
    fetchFilters();

    // Event listeners
    searchBtn.addEventListener('click', () => performSearch());
    searchInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            performSearch();
        }
    });

    clearFiltersBtn.addEventListener('click', () => {
        platformFilter.value = '';
        tacticFilter.value = '';
        // Option to trigger search immediately on clear:
        // performSearch();
    });

    // Delegate Read More clicks
    resultsContainer.addEventListener('click', (e) => {
        if (e.target.classList.contains('read-more-btn')) {
            const descEl = e.target.previousElementSibling;
            if (descEl.classList.contains('collapsed')) {
                descEl.classList.remove('collapsed');
                e.target.textContent = 'Show Less';
            } else {
                descEl.classList.add('collapsed');
                e.target.textContent = 'Read More';
            }
        }
    });

    async function fetchFilters() {
        try {
            const res = await fetch('/api/filters');
            if (!res.ok) throw new Error('Failed to fetch filters');
            const data = await res.json();
            
            if (data.platforms) {
                data.platforms.forEach(platform => {
                    const opt = document.createElement('option');
                    opt.value = platform;
                    opt.textContent = platform;
                    platformFilter.appendChild(opt);
                });
            }
            if (data.tactics) {
                data.tactics.forEach(tactic => {
                    const opt = document.createElement('option');
                    opt.value = tactic;
                    opt.textContent = tactic;
                    tacticFilter.appendChild(opt);
                });
            }
        } catch (error) {
            console.error('Error fetching filters:', error);
        }
    }

    async function performSearch(queryOverride = null) {
        const query = queryOverride || searchInput.value.trim();
        if (!query && !queryOverride) return;

        if (queryOverride) {
            searchInput.value = queryOverride;
        }

        const platform = platformFilter.value;
        const tactic = tacticFilter.value;

        resultsContainer.innerHTML = '';
        statusContainer.innerHTML = `
            <div class="spinner"></div>
            <p style="color: var(--text-secondary);">Scanning intelligence database...</p>
        `;
        
        // Disable search button
        searchBtn.disabled = true;
        searchBtn.innerHTML = '<div class="mini-spinner" style="margin: 0; width: 16px; height: 16px; border-color: rgba(255,255,255,0.2); border-top-color: #fff;"></div>';

        const requestBody = {
            query: query,
            limit: 10
        };
        if (platform) requestBody.platform = platform;
        if (tactic) requestBody.tactic = tactic;

        try {
            const res = await fetch('/api/search', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(requestBody)
            });

            if (!res.ok) throw new Error('Search failed');

            const data = await res.json();
            statusContainer.innerHTML = '';

            if (data.results && data.results.length > 0) {
                data.results.forEach((item, index) => {
                    const card = createResultCard(item, index);
                    resultsContainer.appendChild(card);
                    // Fetch related for each card
                    fetchRelated(item.id, card.querySelector('.related-section-content'));
                });
            } else {
                statusContainer.innerHTML = `
                    <div class="no-results">
                        <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
                        <p>No techniques matched your query.</p>
                    </div>
                `;
            }
        } catch (error) {
            statusContainer.innerHTML = `
                <div class="error-card">
                    <strong>Error:</strong> Failed to connect to the intelligence database API. Please try again later.
                </div>
            `;
            console.error(error);
        } finally {
            // Re-enable search button
            searchBtn.disabled = false;
            searchBtn.innerHTML = '<span class="btn-text">Search</span>';
        }
    }

    function createResultCard(item, index) {
        const div = document.createElement('div');
        div.className = 'result-card';
        div.style.animationDelay = `${index * 0.1}s`;

        const scorePct = Math.round(item.score * 100);
        
        // Metadata formatting as requested: "Platforms: Windows • Linux • macOS"
        let platformsHtml = '';
        if (item.platforms && item.platforms.length > 0) {
            platformsHtml = `<div style="font-size: 0.85rem; margin-bottom: 0.25rem;"><strong style="color: var(--text-secondary);">Platforms</strong><br/>${escapeHTML(item.platforms.join(' • '))}</div>`;
        }
        
        let tacticsHtml = '';
        if (item.tactics && item.tactics.length > 0) {
            tacticsHtml = `<div style="font-size: 0.85rem; margin-bottom: 0.75rem;"><strong style="color: var(--text-secondary);">Tactics</strong><br/>${escapeHTML(item.tactics.join(' • '))}</div>`;
        }
        
        let metadataHtml = '';
        if (platformsHtml || tacticsHtml) {
            metadataHtml = `<div class="card-metadata" style="margin-bottom: 1rem;">${platformsHtml}${tacticsHtml}</div>`;
        }

        const fullDesc = escapeHTML(item.description || 'No description available.');
        const isLong = fullDesc.length > 280;
        
        const descHtml = `
            <div class="card-desc-container">
                <p class="card-desc ${isLong ? 'collapsed' : ''}">${fullDesc}</p>
                ${isLong ? '<button class="read-more-btn">Read More</button>' : ''}
            </div>
        `;

        div.innerHTML = `
            <div class="card-header">
                <div class="title-group">
                    <span class="tech-id">${escapeHTML(item.technique_id || 'UNKNOWN')}</span>
                    <h3 class="card-title">${escapeHTML(item.title)}</h3>
                </div>
                <div class="score-badge">
                    <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>
                    ${scorePct}% Match
                </div>
            </div>
            
            ${metadataHtml}
            ${descHtml}
            
            <div class="card-footer" style="justify-content: flex-end;">
                ${item.url ? `<a href="${escapeHTML(item.url)}" target="_blank" rel="noopener noreferrer" class="mitre-btn">
                    View on MITRE
                    <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path><polyline points="15 3 21 3 21 9"></polyline><line x1="10" y1="14" x2="21" y2="3"></line></svg>
                </a>` : ''}
            </div>
            <div class="related-section">
                <h4 class="related-title">Related Techniques</h4>
                <div class="related-section-content">
                    <div class="mini-spinner"></div>
                </div>
            </div>
        `;

        return div;
    }

    async function fetchRelated(pointId, container) {
        try {
            const res = await fetch('/api/related', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ point_id: pointId, limit: 4 })
            });

            if (!res.ok) throw new Error('Failed to fetch related');
            
            const data = await res.json();
            container.innerHTML = '';
            
            if (data.related && data.related.length > 0) {
                const grid = document.createElement('div');
                grid.className = 'related-cards';
                
                data.related.forEach(rel => {
                    const miniScore = Math.round(rel.score * 100);
                    const miniCard = document.createElement('div');
                    miniCard.className = 'mini-card';
                    miniCard.innerHTML = `
                        <div class="mini-card-header">
                            <span class="tech-id" style="font-size: 0.75rem;">${escapeHTML(rel.technique_id || 'UKN')}</span>
                            <span class="score-badge" style="padding: 0.2rem 0.5rem; font-size: 0.75rem;">${miniScore}%</span>
                        </div>
                        <div class="mini-card-title" title="${escapeHTML(rel.title)}">${escapeHTML(rel.title)}</div>
                    `;
                    miniCard.addEventListener('click', () => {
                        window.scrollTo({ top: 0, behavior: 'smooth' });
                        performSearch(rel.title);
                    });
                    grid.appendChild(miniCard);
                });
                
                container.appendChild(grid);
            } else {
                container.innerHTML = '<span style="color: var(--text-secondary); font-size: 0.85rem;">No related techniques found.</span>';
            }
            
        } catch (error) {
            container.innerHTML = '<span style="color: var(--danger); font-size: 0.85rem;">Failed to load related.</span>';
            console.error(error);
        }
    }

    function escapeHTML(str) {
        if (!str) return '';
        const div = document.createElement('div');
        div.textContent = str;
        return div.innerHTML;
    }
});
