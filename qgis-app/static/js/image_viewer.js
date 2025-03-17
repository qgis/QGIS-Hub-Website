// JavaScript for the image viewer
const imageViewer = document.getElementById('imageViewer');
const viewedImage = document.getElementById('viewedImage');
const zoomInButton = document.getElementById('zoomIn');
const zoomOutButton = document.getElementById('zoomOut');
const resetZoomButton = document.getElementById('resetZoom');

let scale = 1;
let posX = 0, posY = 0;
let isDragging = false;
let startX, startY, translateX = 0, translateY = 0;

function openViewer(imageUrl) {
  viewedImage.src = imageUrl;
  imageViewer.classList.add('active');
}

// Close the image viewer when clicking outside the image
imageViewer.addEventListener('click', (e) => {
    if (e.target === imageViewer) {
        imageViewer.classList.remove('active');
        resetZoom();
    }
});

// Zoom in
zoomInButton.addEventListener('click', () => {
    scale += 0.25;
    updateImageTransform();
});

// Zoom out
zoomOutButton.addEventListener('click', () => {
    if (scale > 0.25) {
        scale -= 0.25;
        updateImageTransform();
    }
});

// Reset zoom and pan
resetZoomButton.addEventListener('click', () => {
    resetZoom();
});

// Reset zoom and pan
function resetZoom() {
    scale = 1;
    translateX = 0;
    translateY = 0;
    updateImageTransform();
}

// Update the image's transform property
function updateImageTransform() {
    viewedImage.style.transform = `translate(${translateX}px, ${translateY}px) scale(${scale})`;
}

// Pan functionality
viewedImage.addEventListener('mousedown', (e) => {
    if (scale > 1) {
        isDragging = true;
        startX = e.clientX - translateX;
        startY = e.clientY - translateY;
        viewedImage.style.cursor = 'grabbing';

        // Prevent default drag behavior
        e.preventDefault();
    }
});

viewedImage.addEventListener('mousemove', (e) => {
    if (isDragging) {
        e.preventDefault();
        translateX = e.clientX - startX;
        translateY = e.clientY - startY;
        updateImageTransform();
    }
});

viewedImage.addEventListener('mouseup', () => {
    isDragging = false;
    viewedImage.style.cursor = 'grab';
});

viewedImage.addEventListener('mouseleave', () => {
    isDragging = false;
    viewedImage.style.cursor = 'grab';
});

// Prevent default drag behavior for the image
viewedImage.setAttribute('draggable', false);
viewedImage.addEventListener('dragstart', (e) => {
    e.preventDefault();
});

// Disable right-click context menu
viewedImage.addEventListener('contextmenu', (e) => {
    e.preventDefault();
});

// Optional: Disable right-click for the entire viewer
imageViewer.addEventListener('contextmenu', (e) => {
    e.preventDefault();
});