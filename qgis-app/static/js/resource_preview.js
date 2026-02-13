/**
 * Resource Preview Modal
 * Handles full-screen preview of maps and screenshots with navigation
 */

(function() {
  'use strict';

  // State
  let resources = [];
  let currentIndex = 0;
  let scale = 1;
  let isDragging = false;
  let startX, startY, translateX = 0, translateY = 0;

  /**
   * Initialize the resource preview from DOM elements
   */
  function initializeResourcesFromDOM() {
    resources = [];
    const seenIds = new Set();
    
    const resourceElements = document.querySelectorAll('[data-resource-id]');
    resourceElements.forEach(function(element) {
      const resourceId = element.getAttribute('data-resource-id');
      
      if (seenIds.has(resourceId)) {
        return;
      }
      seenIds.add(resourceId);
      
      const imageUrl = element.getAttribute('data-resource-image-url');
      
      if (!imageUrl || imageUrl === 'null' || imageUrl === '') {
        console.warn('Skipping resource with invalid image URL:', resourceId);
        return;
      }
      
      const resourceData = {
        id: resourceId,
        name: element.getAttribute('data-resource-name') || 'Untitled',
        creator: element.getAttribute('data-resource-creator') || 'Unknown',
        uploadDate: element.getAttribute('data-resource-upload-date') || '',
        downloadCount: element.getAttribute('data-resource-download-count') || '0',
        description: element.getAttribute('data-resource-description') || '',
        imageUrl: imageUrl,
        downloadUrl: element.getAttribute('data-resource-download-url') || '#',
        detailUrl: element.getAttribute('data-resource-detail-url') || '#',
        isPublishable: element.getAttribute('data-resource-publishable') === 'true',
        resourceType: element.getAttribute('data-resource-type') || 'Resource'
      };
      resources.push(resourceData);
    });
    
  }

  /**
   * Open the preview modal with a specific resource
   */
  function openPreview(resourceId) {
    const modal = document.getElementById('resourcePreviewModal');
    if (!modal) {
      console.error('Preview modal not found in DOM');
      return;
    }

    initializeResourcesFromDOM();
    
    currentIndex = resources.findIndex(function(r) {
      return r.id === resourceId;
    });
    
    if (currentIndex === -1) {
      console.error('Resource not found:', resourceId);
      return;
    }

    showResource(currentIndex);
    modal.classList.add('is-active');
    document.documentElement.classList.add('is-clipped');
    
  }

  /**
   * Display a resource in the preview modal
   */
  function showResource(index) {
    if (index < 0 || index >= resources.length) return;

    currentIndex = index;
    const resource = resources[currentIndex];


    const previewImage = document.getElementById('previewImage');
    const previewName = document.getElementById('previewName');
    const previewCreator = document.getElementById('previewCreator');
    const previewUploadDate = document.getElementById('previewUploadDate');
    const previewDownloadCount = document.getElementById('previewDownloadCount');
    const previewDescription = document.getElementById('previewDescription');
    const previewDownloadBtn = document.getElementById('previewDownloadBtn');
    const previewViewDetailBtn = document.getElementById('previewViewDetailBtn');
    const previewDownloadBtnMobile = document.getElementById('previewDownloadBtnMobile');
    const previewViewDetailBtnMobile = document.getElementById('previewViewDetailBtnMobile');
    const previewHeaderTitle = document.getElementById('previewHeaderTitle');
    const publishableInfo = document.getElementById('previewPublishableInfo');
    const publishableText = document.getElementById('previewPublishableText');
    const prevBtn = document.getElementById('prevResourceBtn');
    const nextBtn = document.getElementById('nextResourceBtn');

    if (resource.imageUrl && resource.imageUrl !== 'null') {
      previewImage.src = resource.imageUrl;
      previewImage.alt = resource.name;
    } else {
      console.error('Invalid image URL for resource:', resource);
      previewImage.src = '';
      previewImage.alt = 'No image available';
    }

    previewName.textContent = resource.name;
    if (previewHeaderTitle) {
      previewHeaderTitle.textContent = resource.name;
    }
    previewCreator.textContent = resource.creator;
    previewUploadDate.textContent = resource.uploadDate;
    previewDownloadCount.textContent = resource.downloadCount;
    previewDescription.innerHTML = resource.description;

    previewDownloadBtn.onclick = function() {
      window.location.href = resource.downloadUrl;
    };
    previewViewDetailBtn.href = resource.detailUrl;
    
    previewDownloadBtnMobile.onclick = function() {
      window.location.href = resource.downloadUrl;
    };
    previewViewDetailBtnMobile.href = resource.detailUrl;

    if (resource.isPublishable) {
      publishableInfo.classList.remove('is-hidden');
      const qgisUrl = resource.resourceType === 'Map' 
        ? 'https://qgis.org/project/overview/maps/'
        : 'https://qgis.org/en/site/about/screenshots.html';
      publishableText.innerHTML = 'Also available on <a href="' + qgisUrl + '" target="_blank" rel="noopener noreferrer">QGIS.org</a>';
    } else {
      publishableInfo.classList.add('is-hidden');
    }

    const hasPrev = currentIndex > 0;
    const hasNext = currentIndex < resources.length - 1;

    if (prevBtn) {
      prevBtn.disabled = !hasPrev;
      prevBtn.classList.toggle('is-disabled', !hasPrev);
      prevBtn.setAttribute('aria-disabled', String(!hasPrev));
    }

    if (nextBtn) {
      nextBtn.disabled = !hasNext;
      nextBtn.classList.toggle('is-disabled', !hasNext);
      nextBtn.setAttribute('aria-disabled', String(!hasNext));
    }

    resetZoom();
  }

  /**
   * Close the preview modal
   */
  function closePreview() {
    const modal = document.getElementById('resourcePreviewModal');
    if (modal) {
      modal.classList.remove('is-active');
      document.documentElement.classList.remove('is-clipped');
      resetZoom();
    }
  }

  /**
   * Navigate to previous resource
   */
  function showPrevious() {
    if (currentIndex > 0) {
      showResource(currentIndex - 1);
    }
  }

  /**
   * Navigate to next resource
   */
  function showNext() {
    if (currentIndex < resources.length - 1) {
      showResource(currentIndex + 1);
    }
  }

  /**
   * Zoom functionality
   */
  function updateImageTransform() {
    const previewImage = document.getElementById('previewImage');
    if (previewImage) {
      previewImage.style.transform = 'translate(' + translateX + 'px, ' + translateY + 'px) scale(' + scale + ')';
    }
  }

  function zoomIn() {
    scale += 0.25;
    if (scale > 3) scale = 3;
    updateImageTransform();
  }

  function zoomOut() {
    scale -= 0.25;
    if (scale < 0.25) scale = 0.25;
    updateImageTransform();
  }

  function resetZoom() {
    scale = 1;
    translateX = 0;
    translateY = 0;
    updateImageTransform();
  }

  /**
   * Setup event listeners when modal is available
   */
  function setupModalListeners() {
    const modal = document.getElementById('resourcePreviewModal');
    if (!modal) return;

    const previewImage = document.getElementById('previewImage');
    const imageContainer = modal.querySelector('.resource-preview-image-container');
    const closeModalBtn = document.getElementById('closePreviewModal');
    const closeModalTopBtn = document.getElementById('closePreviewModalTop');
    const modalBackground = modal.querySelector('.modal-background');
    const prevBtn = document.getElementById('prevResourceBtn');
    const nextBtn = document.getElementById('nextResourceBtn');
    const zoomInBtn = document.getElementById('previewZoomIn');
    const zoomOutBtn = document.getElementById('previewZoomOut');
    const zoomResetBtn = document.getElementById('previewZoomReset');

    if (previewImage) {
      previewImage.addEventListener('mousedown', function(e) {
        if (scale > 1) {
          isDragging = true;
          startX = e.clientX - translateX;
          startY = e.clientY - translateY;
          previewImage.style.cursor = 'grabbing';
          e.preventDefault();
        }
      });

      previewImage.addEventListener('mousemove', function(e) {
        if (isDragging) {
          e.preventDefault();
          translateX = e.clientX - startX;
          translateY = e.clientY - startY;
          updateImageTransform();
        }
      });

      previewImage.addEventListener('mouseup', function() {
        isDragging = false;
        previewImage.style.cursor = 'grab';
      });

      previewImage.addEventListener('mouseleave', function() {
        isDragging = false;
        previewImage.style.cursor = 'grab';
      });

      previewImage.setAttribute('draggable', false);
      previewImage.addEventListener('dragstart', function(e) {
        e.preventDefault();
      });

      previewImage.addEventListener('contextmenu', function(e) {
        e.preventDefault();
      });
    }

    if (closeModalBtn) closeModalBtn.addEventListener('click', closePreview);
    if (closeModalTopBtn) closeModalTopBtn.addEventListener('click', closePreview);
    if (modalBackground) modalBackground.addEventListener('click', closePreview);

    if (prevBtn) prevBtn.addEventListener('click', showPrevious);
    if (nextBtn) nextBtn.addEventListener('click', showNext);

    if (zoomInBtn) zoomInBtn.addEventListener('click', zoomIn);
    if (zoomOutBtn) zoomOutBtn.addEventListener('click', zoomOut);
    if (zoomResetBtn) zoomResetBtn.addEventListener('click', resetZoom);

    if (imageContainer) {
      let touchStartX = 0;
      let touchStartY = 0;
      const swipeThreshold = 50;

      imageContainer.addEventListener('touchstart', function(e) {
        if (!modal.classList.contains('is-active')) return;
        if (e.touches.length !== 1) return;
        touchStartX = e.touches[0].clientX;
        touchStartY = e.touches[0].clientY;
      }, { passive: true });

      imageContainer.addEventListener('touchend', function(e) {
        if (!modal.classList.contains('is-active')) return;
        if (scale !== 1) return;
        if (e.changedTouches.length !== 1) return;

        const touch = e.changedTouches[0];
        const deltaX = touch.clientX - touchStartX;
        const deltaY = touch.clientY - touchStartY;

        if (Math.abs(deltaX) > Math.abs(deltaY) && Math.abs(deltaX) > swipeThreshold) {
          if (deltaX < 0) {
            showNext();
          } else {
            showPrevious();
          }
        }
      }, { passive: true });
    }

    document.addEventListener('keydown', function(e) {
      if (!modal.classList.contains('is-active')) return;

      switch(e.key) {
        case 'Escape':
          closePreview();
          break;
        case 'ArrowLeft':
          showPrevious();
          break;
        case 'ArrowRight':
          showNext();
          break;
        case '+':
        case '=':
          zoomIn();
          break;
        case '-':
          zoomOut();
          break;
        case '0':
          resetZoom();
          break;
      }
    });
  }

  // Initialize on DOM ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() {
      setupModalListeners();
    });
  } else {
    setupModalListeners();
  }
  
  // Make openPreview accessible globally for inline onclick handlers
  window.openPreview = openPreview;

})();
