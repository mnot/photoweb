/**
 * photoweb dynamic behavior
 * Handles keyboard navigation for detail pages.
 */

document.addEventListener('keydown', function(event) {
    if (event.key === 'ArrowLeft') {
        const prev = document.getElementById('prev');
        if (prev) {
            // navigate to previous
            if (prev.href) {
                window.location.href = prev.href;
            } else {
                prev.click();
            }
        }
    } else if (event.key === 'ArrowRight') {
        const next = document.getElementById('next');
        if (next) {
            // navigate to next
            if (next.href) {
                window.location.href = next.href;
            } else {
                next.click();
            }
        }
    } else if (event.key === 'Escape') {
        const up = document.getElementById('up');
        if (up) {
            // return to index
            if (up.href) {
                window.location.href = up.href;
            } else {
                up.click();
            }
        }
    }
});
