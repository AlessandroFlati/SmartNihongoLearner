(async function() {
    const collectedHTML = [];
    const seenElements = new Set();
    let previousCount = 0;
    let unchangedCount = 0;
    const maxUnchangedAttempts = 4;
    let currentScrollPosition = 0;

    console.log('Starting collection process...');

    while (unchangedCount < maxUnchangedAttempts) {
        // Find all matching elements
        const elements = document.querySelectorAll('.tab.item-tab.svelte-1re455k');

        // Collect HTML from visible elements
        elements.forEach(el => {
            // Check if element is visible
            const rect = el.getBoundingClientRect();
            const isVisible = rect.top >= 0 || rect.bottom >= 0;

            if (isVisible && !seenElements.has(el)) {
                seenElements.add(el);
                collectedHTML.push(el.outerHTML);
            }
        });

        console.log(`Collected ${collectedHTML.length} elements so far...`);

        // Check if we found new items
        const currentCount = collectedHTML.length;
        if (currentCount === previousCount) {
            unchangedCount++;
        } else {
            unchangedCount = 0;
        }
        previousCount = currentCount;

        // Scroll down by 500px
        currentScrollPosition += 750;
        window.scrollTo(0, currentScrollPosition);

        // Wait for content to load
        await new Promise(resolve => setTimeout(resolve, 1000));
    }

    console.log(`✓ Collection complete! Found ${collectedHTML.length} elements.`);
    console.log('Access the data with: window.collectedTabsHTML');

    // Expose the collected data globally
    window.collectedTabsHTML = collectedHTML;

    // Also return it for immediate access
    return collectedHTML;
})();