/**
 * photoweb dynamic behavior
 * Handles navigation and immersive photo viewing.
 */

// --- Global Helpers ---

/**
 * Applies calculated dimensions to the image container to prevent layout shift.
 * Uses data attributes injected by the template.
 */
const setDimensions = () => {
    const pic = document.getElementById('pic');
    const layout = document.querySelector('.detail-layout');
    if (!pic || !layout) return;
    const container = pic.parentElement;
    if (container && container.dataset.w && container.dataset.h) {
        const w = container.dataset.w;
        const h = container.dataset.h;
        pic.style.aspectRatio = `${w} / ${h}`;
        pic.style.width = '100%';
        pic.style.height = 'auto';
        container.style.width = `min(95vw, calc(80vh * ${w} / ${h}))`;
    }
};

/**
 * Clears inline dimensions to allow the image to fill the screen in fullscreen mode.
 */
const clearDimensions = () => {
    const pic = document.getElementById('pic');
    if (!pic) return;
    pic.style.cssText = ''; 
    const container = pic.parentElement;
    if (container) container.style.cssText = '';
};

/**
 * Toggles the browser's Fullscreen API (only on mobile for edge-to-edge).
 */
const toggleFullscreenAPI = (enter) => {
    const ua = navigator.userAgent;
    const isMobile = /Android|iPhone|iPad|iPod|Opera Mini|IEMobile|Mobile/i.test(ua);
    const hasTouch = ('ontouchstart' in window) || (navigator.maxTouchPoints > 0);
    
    if (!isMobile || !hasTouch) return;

    try {
        if (enter) {
            const el = document.documentElement;
            if (el.requestFullscreen) el.requestFullscreen();
            else if (el.webkitRequestFullscreen) el.webkitRequestFullscreen();
        } else {
            if (document.exitFullscreen && document.fullscreenElement) {
                document.exitFullscreen();
            } else if (document.webkitExitFullscreen && document.webkitFullscreenElement) {
                document.webkitExitFullscreen();
            }
        }
    } catch (e) {
        console.warn("Fullscreen API not supported or blocked", e);
    }
};

// --- State Handlers ---

const getLayout = () => document.querySelector('.detail-layout');
const isImmersive = () => getLayout()?.classList.contains('is-fullscreen');
const isZoomed = () => getLayout()?.classList.contains('is-zoomed');

const enterImmersive = () => {
    clearDimensions();
    getLayout()?.classList.add('is-fullscreen');
    toggleFullscreenAPI(true);
};

const exitImmersive = () => {
    const layout = getLayout();
    if (!layout) return;
    layout.classList.remove('is-fullscreen');
    layout.classList.remove('is-zoomed');
    toggleFullscreenAPI(false);
    setDimensions();
};

const toggleZoom = () => {
    if (isImmersive()) {
        getLayout()?.classList.toggle('is-zoomed');
    }
};

// --- Initialization ---

document.addEventListener('DOMContentLoaded', function() {
    const pic = document.getElementById('pic');
    const layout = getLayout();
    if (!pic || !layout) return;

    // Lock dimensions immediately on load
    setDimensions();

    // Lock dimensions immediately on load
    setDimensions();

    /**
     * Single Click/Tap Handler
     */
    let clickTimer = null;
    pic.addEventListener('click', function(e) {
        e.stopPropagation();
        if (clickTimer) {
            clearTimeout(clickTimer);
            clickTimer = null;
            return; // Part of a dblclick
        }

        const runClick = () => {
            if (!isImmersive()) {
                enterImmersive();
            } else if (isZoomed()) {
                layout.classList.remove('is-zoomed');
            } else {
                exitImmersive();
            }
        };

        if (e.pointerType === 'touch' || e.pointerType === 'pen') {
            runClick();
        } else {
            clickTimer = setTimeout(() => {
                runClick();
                clickTimer = null;
            }, 250);
        }
    });

    /**
     * Double Click Handler
     */
    pic.addEventListener('dblclick', function(e) {
        e.stopPropagation();
        if (clickTimer) {
            clearTimeout(clickTimer);
            clickTimer = null;
        }
        toggleZoom();
    });

    /**
     * Background Click Handler (Exit Fullscreen)
     */
    layout.addEventListener('click', function(e) {
        if (e.target === layout && isImmersive()) {
            exitImmersive();
        }
    });

    /**
     * Mobile Pinch-to-Zoom
     */
    let initialDist = -1;
    let currentScale = 1;

    pic.addEventListener('touchstart', function(e) {
        if (e.touches.length === 2 && isImmersive()) {
            initialDist = Math.hypot(
                e.touches[0].pageX - e.touches[1].pageX,
                e.touches[0].pageY - e.touches[1].pageY
            );
        }
    }, {passive: false});

    pic.addEventListener('touchmove', function(e) {
        if (e.touches.length === 2 && initialDist > 0 && isImmersive()) {
            e.preventDefault(); // Stop OS viewport zoom
            const dist = Math.hypot(
                e.touches[0].pageX - e.touches[1].pageX,
                e.touches[0].pageY - e.touches[1].pageY
            );
            currentScale = dist / initialDist;
            pic.style.transform = `scale(${currentScale})`;
        }
    }, {passive: false});

    pic.addEventListener('touchend', function() {
        if (initialDist > 0) {
            if (currentScale > 1.2 && !isZoomed()) {
                layout.classList.add('is-zoomed');
            } else if (currentScale < 0.8 && isZoomed()) {
                layout.classList.remove('is-zoomed');
            }
            pic.style.transform = '';
        }
        initialDist = -1;
        currentScale = 1;
    }, {passive: true});
});

// --- Navigation & Accessibility ---

document.addEventListener('keydown', function(event) {
    const immersive = isImmersive() || isZoomed();
    
    if ((event.key === 'ArrowLeft' || event.key === 'ArrowRight') && !immersive) {
        const id = event.key === 'ArrowLeft' ? 'prev' : 'next';
        const el = document.getElementById(id);
        if (el) (el.href ? window.location.href = el.href : el.click());
    } else if (event.key === 'Escape') {
        if (isImmersive()) {
            exitImmersive();
        } else {
            const up = document.getElementById('up');
            if (up) (up.href ? window.location.href = up.href : up.click());
        }
    }
});

/**
 * Swipe Navigation (Non-Immersive Mode)
 */
let touchStartX = 0;
let touchStartY = 0;
const swipeThreshold = 50;

document.addEventListener('touchstart', function(e) {
    if (e.touches.length === 1) {
        touchStartX = e.changedTouches[0].screenX;
        touchStartY = e.changedTouches[0].screenY;
    }
}, {passive: true});

document.addEventListener('touchend', function(e) {
    if (isImmersive()) return;

    const diffX = e.changedTouches[0].screenX - touchStartX;
    const diffY = e.changedTouches[0].screenY - touchStartY;

    if (Math.abs(diffX) > Math.abs(diffY) && Math.abs(diffX) > swipeThreshold) {
        const id = diffX < 0 ? 'next' : 'prev';
        const el = document.getElementById(id);
        if (el) el.href ? window.location.href = el.href : el.click();
    }
}, {passive: true});
