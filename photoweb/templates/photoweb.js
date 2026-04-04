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

/**
 * Handle image zoom/toggle on click
 */
document.addEventListener('DOMContentLoaded', function() {
    const pic = document.getElementById('pic');
    if (pic && pic.parentElement) {
        pic.addEventListener('click', function() {
            pic.parentElement.classList.toggle('full');
        });
    }
});

/**
 * Handle touch swipe navigation
 */
let touchStartX = 0;
let touchStartY = 0;
const swipeThreshold = 50;

document.addEventListener('touchstart', function(event) {
    touchStartX = event.changedTouches[0].screenX;
    touchStartY = event.changedTouches[0].screenY;
}, {passive: true});

document.addEventListener('touchend', function(event) {
    const touchEndX = event.changedTouches[0].screenX;
    const touchEndY = event.changedTouches[0].screenY;
    const diffX = touchEndX - touchStartX;
    const diffY = touchEndY - touchStartY;

    // Only trigger if horizontal movement is dominant and exceeds threshold
    if (Math.abs(diffX) > Math.abs(diffY) && Math.abs(diffX) > swipeThreshold) {
        if (diffX < 0) {
            const next = document.getElementById('next');
            if (next) next.href ? window.location.href = next.href : next.click();
        } else {
            const prev = document.getElementById('prev');
            if (prev) prev.href ? window.location.href = prev.href : prev.click();
        }
    }
}, {passive: true});
