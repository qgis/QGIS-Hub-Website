/**
 * The 3D model viewer.
 *
 * The page shows a thumbnail with a "View in 3D" button over it. The model
 * itself is only fetched once the reader asks to see it.
 */
import bindControls from './controls';
import Viewer from './viewer';

function show(element, visible) {
  element.hidden = !visible;
}

async function openViewer(container) {
  const canvas = container.querySelector('canvas');
  const loading = container.querySelector('[data-viewer-loading]');
  const failure = container.querySelector('[data-viewer-error]');
  const {format, url, mtlUrl} = container.dataset;

  show(container, true);
  show(loading, true);

  const viewer = new Viewer(canvas);
  bindControls(container, viewer);

  try {
    await viewer.load(format, url, mtlUrl);
  } catch (error) {
    console.error(error);
    show(failure, true);
  } finally {
    show(loading, false);
  }
}

function init() {
  const container = document.querySelector('#urlView');
  if (!container || !container.dataset.url) {
    return;
  }
  const trigger = document.querySelector('[data-viewer-open]');
  if (!trigger) {
    return;
  }
  trigger.addEventListener('click', () => {
    show(trigger, false);
    // The still image gives way to the model it stands in for.
    document.querySelectorAll('.style-polaroid .image-resource')
      .forEach((image) => show(image, false));
    openViewer(container);
  }, {once: true});
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init);
} else {
  init();
}
