(function() {
    // Join all HTML into a single string (one element per line)
    const joinedHTML = window.collectedTabsHTML.join('\n');

    console.log(`Joining ${window.collectedTabsHTML.length} elements...`);

    // Create a blob and download it
    const blob = new Blob([joinedHTML], { type: 'text/html' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'collected-tabs.html';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);

    console.log('✓ File downloaded as "collected-tabs.html"');

    // Also expose the joined version
    window.joinedTabsHTML = joinedHTML;

    return joinedHTML;
})();